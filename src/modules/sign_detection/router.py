"""Sign Language Detection API Routes.

WebSocket endpoint for real-time sign language recognition.
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status

from .dependencies import get_sign_service
from .service import SignLanguageService
from .models import SignDetectionRequest, SignDetectionResponse
from src.modules.authentication.dependencies import get_current_user_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/sign-detection",
    tags=["Sign Detection"],
)


@router.websocket("/ws/predict")
async def websocket_predict(
    websocket: WebSocket,
    service: SignLanguageService = Depends(get_sign_service),
) -> None:
    """WebSocket endpoint for real-time sign language prediction.

    Client sends binary image data, server responds with JSON predictions.

    Protocol:
        - Client sends: Raw image bytes (JPEG, PNG, etc.)
        - Server responds: {"sign": "A", "confidence": 0.95}
        - Server responds: {"error": "message"} on failure

    Args:
        websocket: WebSocket connection.
        service: Sign language detection service (injected).
    """
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Receive binary image data from client
            image_bytes = await websocket.receive_bytes()

            try:
                # Perform prediction
                result = await service.predict_frame(image_bytes)

                if result is None:
                    # Low confidence or no detection
                    response: dict[str, Any] = {
                        "sign": None,
                        "confidence": 0.0,
                        "message": "No confident detection",
                    }
                else:
                    # Successful prediction
                    response = {
                        "sign": result["sign"],
                        "confidence": round(result["confidence"], 4),
                        "is_new": result["is_new"],  # Indicates if sign is new or repeat
                    }

                # Send JSON response back to client
                await websocket.send_text(json.dumps(response))

            except ValueError as e:
                # Image processing error
                logger.warning(f"Image processing error: {e}")
                error_response = {
                    "error": "Invalid image data",
                    "message": str(e),
                }
                await websocket.send_text(json.dumps(error_response))

            except Exception as e:
                # Unexpected error
                logger.error(f"Prediction error: {e}", exc_info=True)
                error_response = {
                    "error": "Internal server error",
                    "message": "Failed to process prediction",
                }
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass  # Connection might already be closed


@router.post("/process-text", response_model=SignDetectionResponse)
async def process_detected_text(
    request: SignDetectionRequest,
    service: SignLanguageService = Depends(get_sign_service),
    sender_id: str = Depends(get_current_user_id),  # Auto-extracted from JWT
):
    """Process and save raw sign detection text as a conversation message.
    
    This endpoint is called when the user stops recording.
    It cleans the raw text using LLM and saves it as a message between two users.
    The sender_id is automatically extracted from the JWT token.
    
    Args:
        request: Contains raw_text and receiver_id
        service: Sign language detection service
        sender_id: Automatically extracted from JWT token
        
    Returns:
        SignDetectionResponse with cleaned text and message ID
    """
    try:
        # Clean the text using LLM
        logger.info(f"Cleaning raw text: {request.raw_text}")
        cleaned_text = await service.clean_text_with_llm(request.raw_text)
        logger.info(f"Cleaned text: {cleaned_text}")
        
        # Save to database (sender_id from JWT token)
        record = await service.save_detection_record(
            raw_text=request.raw_text,
            cleaned_text=cleaned_text,
            sender_id=sender_id,  # From JWT token
            receiver_id=request.receiver_id
        )
        
        return SignDetectionResponse(
            id=record["id"],
            sender_id=record["sender_id"],
            receiver_id=record["receiver_id"],
            raw_text=record["raw_text"],
            cleaned_text=record["cleaned_text"],
            created_at=record["created_at"]
        )
        
    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process text: {str(e)}"
        )
