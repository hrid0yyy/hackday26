"""Chat module models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    message: str = Field(..., description="Message text to send", min_length=1)


class ChatHistoryRequest(BaseModel):
    """Request model for getting chat history."""
    user_id: str = Field(..., description="Current user's ID")
    other_user_id: str = Field(..., description="The other user's ID to get conversation with")
    limit: Optional[int] = Field(None, description="Maximum number of messages to return")
    offset: int = Field(0, description="Number of messages to skip for pagination")


class ChatMessage(BaseModel):
    """Chat message model."""
    id: str = Field(..., description="Message ID")
    sender_id: str = Field(..., description="Sender user ID")
    receiver_id: str = Field(..., description="Receiver user ID")
    raw_text: Optional[str] = Field(None, description="Raw detected text")
    cleaned_text: Optional[str] = Field(None, description="LLM cleaned text")
    created_at: datetime = Field(..., description="Message creation timestamp")


class ChatHistoryResponse(BaseModel):
    """Chat history response model."""
    user_id: str = Field(..., description="The other user's ID")
    messages: list[ChatMessage] = Field(default_factory=list, description="List of messages")
    total_count: int = Field(..., description="Total number of messages")
