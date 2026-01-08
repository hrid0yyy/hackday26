"""FastAPI routes for chatbot endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.modules.chatbot.models import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from src.modules.chatbot.service import chatbot_service
from src.modules.authentication.dependencies import get_current_user_id


# Create router
router = APIRouter(
    prefix="/chat",
    tags=["Chatbot"],
    responses={
        401: {"description": "Unauthorized"},
        500: {"description": "Internal Server Error"},
    }
)


@router.post(
    "/",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message",
    description="Send a message to the AI chatbot. Creates new conversation if no conversation_id provided.",
    responses={
        200: {"description": "Message processed successfully"},
        404: {"description": "Conversation not found"},
        401: {"description": "Not authenticated"},
    }
)
async def chat(
    request: ChatRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Send a message to the AI chatbot.
    
    - **message**: The user's message
    - **conversation_id**: Optional. If provided, continues existing conversation. If not, creates new conversation.
    
    The agent has access to web search capabilities and will use them when needed.
    For new conversations, a title is automatically generated using AI.
    """
    return await chatbot_service.chat(request, user_id)


@router.get(
    "/conversations",
    response_model=List[ConversationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user conversations",
    description="Get all conversations for the authenticated user",
    responses={
        200: {"description": "Conversations retrieved successfully"},
        401: {"description": "Not authenticated"},
    }
)
async def get_conversations(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all conversations for the authenticated user.
    
    Returns a list of conversations ordered by creation date (newest first).
    """
    return await chatbot_service.get_user_conversations(user_id)


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get conversation messages",
    description="Get all messages in a specific conversation",
    responses={
        200: {"description": "Messages retrieved successfully"},
        404: {"description": "Conversation not found or access denied"},
        401: {"description": "Not authenticated"},
    }
)
async def get_conversation_messages(
    conversation_id: int,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all messages in a specific conversation.
    
    Returns messages ordered by creation time (oldest first).
    Only accessible if the conversation belongs to the authenticated user.
    """
    return await chatbot_service.get_conversation_messages(conversation_id, user_id)


@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if chatbot service is running",
)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "message": "Chatbot service is healthy",
        "success": True
    }
