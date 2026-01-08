"""Sign Language Detection API Routes.

WebSocket endpoint for real-time sign language recognition.
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from .dependencies import get_sign_service
from .service import SignLanguageService

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
