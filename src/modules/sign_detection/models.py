"""Data models for Sign Detection module."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SignDetectionRequest(BaseModel):
    """Request model for processing detected signs."""
    
    raw_text: str = Field(..., description="Raw text from sign detection (e.g., 'iaammmliikee')")
    receiver_id: str = Field(..., description="ID of user receiving the message")


class SignDetectionResponse(BaseModel):
    """Response model for processed sign detection."""
    
    id: str = Field(..., description="Message ID")
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    raw_text: str = Field(..., description="Original raw text")
    cleaned_text: str = Field(..., description="LLM-cleaned text")
    created_at: datetime = Field(..., description="Timestamp")


class ConversationMessage(BaseModel):
    """Database model for conversation messages."""
    
    id: Optional[str] = None
    sender_id: str
    receiver_id: str
    raw_text: str
    cleaned_text: str
    created_at: Optional[datetime] = None
