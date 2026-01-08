"""Data models for general module."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserSearchRequest(BaseModel):
    """Request model for user search."""
    
    email: EmailStr = Field(..., description="Email to search for")


class UserSearchResult(BaseModel):
    """User search result model."""
    
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: Optional[str] = Field(None, description="User's full name")
    status: Optional[str] = Field(None, description="User status (mute, deaf, blind, normal)")
