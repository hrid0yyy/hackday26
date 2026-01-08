"""FastAPI routes for text to ASL sign language conversion."""

from fastapi import APIRouter, HTTPException, status
from typing import List

from src.modules.text_to_sign.models import (
    TextToSignRequest,
    TextToSignResponse,
    FingerspellResponse,
)
from src.modules.text_to_sign.service import text_to_sign_service


# Create router
router = APIRouter(
    prefix="/text-to-sign",
    tags=["Text to Sign Language"],
    responses={
        400: {"description": "Bad Request"},
        500: {"description": "Internal Server Error"},
    }
)


@router.post(
    "/convert",
    response_model=TextToSignResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert text based on receiver's disability",
    description="Convert text and process it based on the receiver's disability status (deaf, mute, blind, normal)",
    responses={
        200: {"description": "Text converted successfully"},
        400: {"description": "Invalid request"},
    }
)
async def convert_text_to_asl(request: TextToSignRequest):
    """
    Convert text based on the receiver's disability status.
    
    - **text**: The text to convert (e.g., "I love you")
    - **receiver_status**: The receiver's status - "deaf", "mute", "blind", or "normal"
    - **include_fingerspelling**: Whether to include fingerspelling for names/unknown words
    - **detail_level**: Level of detail - 'basic', 'detailed', or 'expert'
    - **generate_images**: Generate ASL sign images for each word (default: True)
    
    Based on receiver_status:
    - **deaf/mute**: Converts to ASL with sign descriptions + generates images using DALL-E
    - **blind**: Optimizes text for screen readers
    - **normal**: Just cleans the text
    
    For deaf/mute users, each sign includes:
    - Detailed description of how to perform the sign
    - Handshape, movement, location
    - Generated image showing the ASL sign (if generate_images=True)
    """
    try:
        return await text_to_sign_service.convert_text_to_sign(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting text: {str(e)}"
        )


@router.get(
    "/fingerspell/{word}",
    response_model=FingerspellResponse,
    status_code=status.HTTP_200_OK,
    summary="Get fingerspelling for a word",
    description="Get ASL fingerspelling instructions for a specific word",
)
async def get_fingerspelling(word: str):
    """
    Get fingerspelling instructions for a word.
    
    - **word**: The word to fingerspell
    
    Returns letter-by-letter handshape descriptions for fingerspelling.
    """
    if not word or len(word) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Word must be between 1 and 50 characters"
        )
    
    return text_to_sign_service.get_fingerspelling(word)


@router.get(
    "/common-phrases",
    response_model=List[dict],
    status_code=status.HTTP_200_OK,
    summary="Get common ASL phrases",
    description="Get a list of common ASL phrases with their sign descriptions",
)
async def get_common_phrases():
    """
    Get common ASL phrases with their sign descriptions.
    
    Returns a list of frequently used phrases and how to sign them.
    """
    return await text_to_sign_service.get_common_phrases()


@router.get(
    "/alphabet",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Get ASL fingerspelling alphabet",
    description="Get the complete ASL fingerspelling alphabet with handshape descriptions",
)
async def get_alphabet():
    """
    Get the complete ASL fingerspelling alphabet.
    
    Returns all 26 letters with their handshape descriptions.
    """
    return {
        "alphabet": text_to_sign_service.fingerspell_alphabet,
        "tips": [
            "Keep your hand steady at shoulder height",
            "Face your palm toward the person you're communicating with",
            "Pause briefly between words (double-letter words: bounce the letter slightly)",
            "Practice smooth transitions between letters",
            "Maintain eye contact while fingerspelling"
        ]
    }
