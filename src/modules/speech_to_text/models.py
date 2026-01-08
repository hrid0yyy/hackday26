"""Data models for Speech to Text module."""

from datetime import datetime
from pydantic import BaseModel, Field


class SpeechToTextResponse(BaseModel):
    """Response model for speech to text conversion."""
    
    id: str = Field(..., description="Message ID")
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    transcribed_text: str = Field(..., description="Transcribed text from audio")
    created_at: datetime = Field(..., description="Timestamp")
