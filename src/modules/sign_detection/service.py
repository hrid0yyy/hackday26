"""Sign Language Detection Service.

This module provides real-time sign language recognition using
a pre-trained Hugging Face Vision Transformer model.
"""

from __future__ import annotations

import io
from functools import cached_property
from typing import TypedDict

from PIL import Image
from transformers import pipeline

from src.core.config import settings


class PredictionResult(TypedDict):
    """Type definition for prediction results."""

    sign: str
    confidence: float


class SignLanguageService:
    """Service for Sign Language Detection using Hugging Face Transformers.

    The model is loaded only once when first accessed (lazy initialization)
    to prevent memory leaks and reduce startup time.
    """

    _instance: SignLanguageService | None = None
    _model_name: str = settings.SIGN_DETECTION_MODEL
    _confidence_threshold: float = settings.SIGN_DETECTION_CONFIDENCE_THRESHOLD

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
        """Predict sign language character from image bytes.

        Args:
            image_bytes: Raw image data in bytes format.

        Returns:
            PredictionResult containing sign and confidence, or None if:
            - Confidence is below threshold
            - Image processing fails

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

            # TODO: Insert log into Supabase
            # await self._log_prediction(sign, confidence)

            return PredictionResult(sign=sign, confidence=confidence)

        except (OSError, ValueError) as e:
            # Handle image processing errors
            raise ValueError(f"Failed to process image: {str(e)}") from e

    def warmup(self) -> None:
        """Pre-load the model to avoid cold start latency.

        Call this during application startup.
        """
        _ = self.model  # Access cached_property to trigger loading


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
