"""Pydantic models for chatbot requests and responses."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user/assistant/system)")
    content: str = Field(..., description="Message content")


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    conversation_id: Optional[int] = Field(None, description="Existing conversation ID")


class ChatResponse(BaseModel):
    """Chat response model."""
    conversation_id: int = Field(..., description="Conversation ID")
    message: str = Field(..., description="Assistant response")
    title: Optional[str] = Field(None, description="Conversation title (only on new conversations)")


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: int = Field(..., description="Conversation ID")
    title: str = Field(..., description="Conversation title")
    created_at: datetime = Field(..., description="Creation timestamp")
    user_id: str = Field(..., description="User ID")


class MessageResponse(BaseModel):
    """Message response model."""
    id: int = Field(..., description="Message ID")
    conversation_id: int = Field(..., description="Conversation ID")
    role: str = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    created_at: datetime = Field(..., description="Creation timestamp")
