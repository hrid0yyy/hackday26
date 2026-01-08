"""Pydantic models for text to sign language conversion."""

from typing import Optional, List
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class UserStatus(str, Enum):
    """User disability status from profiles table."""
    MUTE = "mute"
    DEAF = "deaf"
    BLIND = "blind"
    NORMAL = "normal"


class SignWord(BaseModel):
    """Model for a single word/phrase and its ASL representation."""
    word: str = Field(..., description="The original word or phrase")
    sign_type: str = Field(..., description="Type: 'sign' for ASL sign, 'fingerspell' for fingerspelling")
    sign_description: str = Field(..., description="Detailed description of how to perform the sign")
    handshape: Optional[str] = Field(None, description="Description of the hand shape(s) used")
    movement: Optional[str] = Field(None, description="Description of the movement")
    location: Optional[str] = Field(None, description="Where the sign is performed (e.g., 'chest', 'forehead')")
    facial_expression: Optional[str] = Field(None, description="Required facial expression if any")
    notes: Optional[str] = Field(None, description="Additional notes or tips")


class LetterSign(BaseModel):
    """Model for a single letter's ASL fingerspelling."""
    letter: str = Field(..., description="The letter")
    image_url: str = Field(..., description="URL to ASL fingerspelling image for this letter")
    description: str = Field(..., description="Description of how to form this letter")


class TextToSignRequest(BaseModel):
    """Request model for text to ASL conversion."""
    text: str = Field(..., description="The text to convert to ASL signs")
    receiver_status: UserStatus = Field(..., description="The receiver's status: deaf, mute, blind, or normal")
    include_fingerspelling: bool = Field(
        default=True, 
        description="Include fingerspelling instructions for names/unknown words"
    )
    detail_level: str = Field(
        default="detailed",
        description="Level of detail: 'basic', 'detailed', or 'expert'"
    )
    generate_images: bool = Field(
        default=True,
        description="Generate ASL sign images for each word"
    )


class TextToSignResponse(BaseModel):
    """Response model for text to ASL conversion."""
    original_text: str = Field(..., description="The original input text")
    processed_text: str = Field(..., description="The processed/cleaned text")
    receiver_status: UserStatus = Field(..., description="The receiver's disability status")
    asl_gloss: Optional[str] = Field(None, description="ASL gloss (sign order) representation - for deaf/mute users")
    signs: Optional[List[SignWord]] = Field(None, description="List of signs with descriptions - for deaf/mute users")
    letter_images: Optional[List[LetterSign]] = Field(None, description="List of letters with their ASL image URLs")
    audio_description: Optional[str] = Field(None, description="Audio-friendly description - for blind users")
    sentence_structure_note: Optional[str] = Field(
        None, 
        description="Note about ASL grammar/sentence structure differences"
    )
    total_signs: Optional[int] = Field(None, description="Total number of signs in the translation")


class ChatConversationResponse(BaseModel):
    """Response model for chat conversation."""
    id: str = Field(..., description="Conversation UUID")
    sender_id: str = Field(..., description="Sender's UUID")
    receiver_id: str = Field(..., description="Receiver's UUID")
    raw_text: str = Field(..., description="Original raw text")
    cleaned_text: str = Field(..., description="Processed/cleaned text")
    created_at: datetime = Field(..., description="Creation timestamp")


class FingerspellResponse(BaseModel):
    """Response model for fingerspelling a word."""
    word: str = Field(..., description="The word being fingerspelled")
    letters: List[dict] = Field(..., description="List of letters with handshape descriptions")
