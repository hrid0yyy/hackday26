"""Speech to Text API Routes.

API endpoint for speech-to-text conversion.
"""

import logging
from typing import Any

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status

from .dependencies import get_speech_service
from .service import SpeechToTextService
from .models import SpeechToTextResponse
from src.modules.authentication.dependencies import get_current_user_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/speech-to-text",
    tags=["Speech to Text"],
)


@router.post("/convert", response_model=SpeechToTextResponse)
async def convert_speech_to_text(
    audio: UploadFile = File(..., description="Audio file (wav, mp3, m4a, etc.)"),
    receiver_id: str = Form(..., description="ID of user receiving the message"),
    service: SpeechToTextService = Depends(get_speech_service),
    sender_id: str = Depends(get_current_user_id),  # Auto-extracted from JWT
):
    """Convert speech audio to text and save as message.
    
    Accepts audio file, transcribes it using OpenAI Whisper,
    and saves as a conversation message.
    
    The sender_id is automatically extracted from the JWT token.
    
    Args:
        audio: Audio file (wav, mp3, m4a, webm, etc.)
        receiver_id: ID of user receiving the message
        service: Speech to text service (injected)
        sender_id: Automatically extracted from JWT token
        
    Returns:
        SpeechToTextResponse with transcribed text and message ID
    """
    try:
        # Validate audio file
        if not audio.content_type or not audio.content_type.startswith("audio/"):
            # Allow common audio formats even if content_type isn't perfect
            allowed_extensions = [".wav", ".mp3", ".m4a", ".mp4", ".mpeg", ".mpga", ".webm"]
            if not any(audio.filename.lower().endswith(ext) for ext in allowed_extensions):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file type. Please upload an audio file."
                )
        
        logger.info(f"Transcribing audio from user {sender_id}: {audio.filename}")
        
        # Read audio file
        audio_bytes = await audio.read()
        
        # Transcribe audio to text
        transcribed_text = await service.transcribe_audio(
            io.BytesIO(audio_bytes),
            audio.filename
        )
        
        logger.info(f"Transcribed text: {transcribed_text}")
        
        # Save to database
        record = await service.save_message(
            transcribed_text=transcribed_text,
            sender_id=sender_id,  # From JWT token
            receiver_id=receiver_id
        )
        
        return SpeechToTextResponse(
            id=record["id"],
            sender_id=record["sender_id"],
            receiver_id=record["receiver_id"],
            transcribed_text=record["cleaned_text"],
            created_at=record["created_at"]
        )
        
    except ValueError as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing audio: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process audio: {str(e)}"
        )
