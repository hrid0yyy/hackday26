"""Speech to Text Service.

This module provides speech-to-text conversion using OpenAI Whisper API.
"""

from __future__ import annotations

import io
from datetime import datetime
import uuid
from typing import BinaryIO

from openai import AsyncOpenAI
from supabase import Client

from src.core.config import settings
from src.core.db import get_supabase_admin_client


class SpeechToTextService:
    """Service for Speech to Text conversion using OpenAI Whisper."""

    _instance: SpeechToTextService | None = None

    def __new__(cls) -> SpeechToTextService:
        """Singleton pattern to ensure only one service instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the service."""
        self._openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_audio(self, audio_file: BinaryIO, filename: str = "audio.wav") -> str:
        """Transcribe audio to text using OpenAI Whisper.

        Args:
            audio_file: Audio file in binary format
            filename: Original filename (for format detection)

        Returns:
            Transcribed text

        Raises:
            ValueError: If audio processing fails
        """
        try:
            # Use OpenAI Whisper API for transcription
            # Whisper supports: mp3, mp4, mpeg, mpga, m4a, wav, webm
            transcription = await self._openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=(filename, audio_file, "audio/wav"),  # Can be any supported format
                language="en",  # Optional: specify language or let Whisper detect
            )

            return transcription.text

        except Exception as e:
            raise ValueError(f"Failed to transcribe audio: {str(e)}") from e

    async def save_message(
        self,
        transcribed_text: str,
        sender_id: str,
        receiver_id: str
    ) -> dict:
        """Save transcribed message to database.
        
        Args:
            transcribed_text: Transcribed text from audio
            sender_id: ID of user who sent the audio
            receiver_id: ID of user receiving the message
            
        Returns:
            Saved message data
        """
        supabase: Client = get_supabase_admin_client()
        
        record = {
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "raw_text": transcribed_text,  # Store as raw_text (no cleaning needed)
            "cleaned_text": transcribed_text,  # Same as raw for speech
            "created_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("chat_conversation").insert(record).execute()
        return result.data[0] if result.data else record


# Global service instance
_service_instance: SpeechToTextService | None = None


def get_service_instance() -> SpeechToTextService:
    """Get or create the global service instance.

    Returns:
        SpeechToTextService: The singleton service instance.
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = SpeechToTextService()
    return _service_instance
