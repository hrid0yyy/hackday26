"""Sign Language Detection Service.

This module provides real-time sign language recognition using
a pre-trained Hugging Face Vision Transformer model.
"""

from __future__ import annotations

import io
import time
from functools import cached_property
from typing import TypedDict
from datetime import datetime
import uuid

from PIL import Image
from transformers import pipeline
from supabase import Client
from openai import AsyncOpenAI

from src.core.config import settings
from src.core.db import get_supabase_admin_client


class PredictionResult(TypedDict):
    """Type definition for prediction results."""

    sign: str
    confidence: float
    is_new: bool  # Flag to indicate if this is a new sign or repeat


class SignLanguageService:
    """Service for Sign Language Detection using Hugging Face Transformers.

    The model is loaded only once when first accessed (lazy initialization)
    to prevent memory leaks and reduce startup time.
    """

    _instance: SignLanguageService | None = None
    _model_name: str = settings.SIGN_DETECTION_MODEL
    _confidence_threshold: float = settings.SIGN_DETECTION_CONFIDENCE_THRESHOLD

    def __init__(self):
        """Initialize the service with deduplication state."""
        self._last_sign: str | None = None
        self._last_sign_time: float = 0
        self._same_sign_count: int = 0
        self._max_repeats: int = settings.SIGN_DETECTION_MAX_REPEATS
        self._cooldown_seconds: float = settings.SIGN_DETECTION_COOLDOWN

    def __new__(cls) -> SignLanguageService:
        """Singleton pattern to ensure only one service instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @cached_property
    def model(self):
        """Load the Hugging Face model (cached - only loaded once).

        Returns:
            transformers.Pipeline: Pre-trained image classification pipeline.
        """
        return pipeline(
            "image-classification",
            model=self._model_name,
            device=settings.SIGN_DETECTION_DEVICE,
            token=settings.HUGGINGFACE_TOKEN,  # Only needed for private models
        )

    async def predict_frame(self, image_bytes: bytes) -> PredictionResult | None:
        """Predict sign language character from image bytes with deduplication.

        Args:
            image_bytes: Raw image data in bytes format.

        Returns:
            PredictionResult containing sign, confidence, and is_new flag, or None if:
            - Confidence is below threshold
            - Image processing fails
            - Same sign detected more than max_repeats times

        Raises:
            ValueError: If image data is malformed or cannot be processed.
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Ensure RGB format
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Run inference (synchronous call wrapped in async function)
            predictions = self.model(image)

            # Get the top prediction
            if not predictions:
                return None

            top_prediction = predictions[0]
            confidence = top_prediction["score"]

            # Filter low-confidence predictions
            if confidence < self._confidence_threshold:
                return None

            # Extract sign character (label)
            sign = top_prediction["label"]
            
            current_time = time.time()
            is_new = True

            # Deduplication logic
            if self._last_sign == sign:
                # Same sign detected
                time_since_last = current_time - self._last_sign_time
                
                # Reset count if cooldown period passed
                if time_since_last > self._cooldown_seconds:
                    self._same_sign_count = 1
                    self._last_sign_time = current_time
                    is_new = True
                else:
                    self._same_sign_count += 1
                    
                    # Suppress if exceeded max repeats
                    if self._same_sign_count > self._max_repeats:
                        return None
                    
                    is_new = False
            else:
                # New sign detected
                self._last_sign = sign
                self._last_sign_time = current_time
                self._same_sign_count = 1
                is_new = True

            # TODO: Insert log into Supabase
            # await self._log_prediction(sign, confidence)

            return PredictionResult(sign=sign, confidence=confidence, is_new=is_new)

        except (OSError, ValueError) as e:
            # Handle image processing errors
            raise ValueError(f"Failed to process image: {str(e)}") from e

    def warmup(self) -> None:
        """Pre-load the model to avoid cold start latency.

        Call this during application startup.
        """
        _ = self.model  # Access cached_property to trigger loading

    async def clean_text_with_llm(self, raw_text: str) -> str:
        """Clean raw sign detection text using LLM.
        
        Args:
            raw_text: Raw text from sign detection (e.g., "iaammmliikee")
            
        Returns:
            Cleaned text that preserves the original message
        """
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        prompt = f"""You are a text correction assistant for sign language detection.

The user performed sign language gestures that were detected as: "{raw_text}"

This text has issues like:
- Repeated letters (e.g., "aaa" should be "a")
- Missing spaces between words
- Potential misspellings from detection errors

Your task:
1. Fix repeated letters and add proper spacing
2. Correct obvious spelling mistakes
3. STRICTLY preserve the original message intent - do NOT change the meaning
4. If unsure, keep the original text
5. Return ONLY the cleaned text, nothing else

Examples:
- "iaammmliikee" → "i am like"
- "heeelloowwoorrlld" → "hello world"
- "iaamhriidoy" → "i am hridoy"

Now clean this text: "{raw_text}"

Cleaned text:"""

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a text correction assistant. Return only the cleaned text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        cleaned_text = response.choices[0].message.content.strip()
        return cleaned_text

    async def save_detection_record(
        self,
        raw_text: str,
        cleaned_text: str,
        sender_id: str,
        receiver_id: str
    ) -> dict:
        """Save conversation message to Supabase.
        
        Args:
            raw_text: Original raw text from detection
            cleaned_text: LLM-cleaned text
            sender_id: ID of user who sent the message
            receiver_id: ID of user receiving the message
            
        Returns:
            Saved message data
        """
        supabase: Client = get_supabase_admin_client()
        
        record = {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("chat_conversation").insert(record).execute()
        return result.data[0] if result.data else record


# Global service instance
_service_instance: SignLanguageService | None = None


def get_service_instance() -> SignLanguageService:
    """Get or create the global service instance.

    Returns:
        SignLanguageService: The singleton service instance.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = SignLanguageService()
    return _service_instance
