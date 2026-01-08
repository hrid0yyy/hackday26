"""Chat module routes."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from src.core.db import get_supabase_client, get_supabase_admin_client
from .service import ChatService
from .models import SendMessageRequest, ChatHistoryRequest, ChatHistoryResponse, ChatMessage


router = APIRouter(prefix="/chat", tags=["Chat"])


def get_chat_service(supabase: Client = Depends(get_supabase_admin_client)) -> ChatService:
    """Dependency to get chat service instance.
    
    Args:
        supabase: Supabase client from dependency
        
    Returns:
        ChatService instance
    """
    return ChatService(supabase)


@router.post("/send", response_model=ChatMessage)
async def send_message(
    request: SendMessageRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Send a message between two users.
    
    Args:
        request: Send message request containing sender_id, receiver_id, and message
        chat_service: Chat service instance
        
    Returns:
        ChatMessage with the created message details
        
    Raises:
        HTTPException: If sending message fails
    """
    try:
        message = await chat_service.send_message(
            sender_id=request.sender_id,
            receiver_id=request.receiver_id,
            message=request.message
        )
        return message
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/history", response_model=ChatHistoryResponse)
async def get_conversation_history(
    request: ChatHistoryRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get conversation history between two users.
    
    Retrieves all messages between the specified users,
    including messages where either user is the sender or receiver.
    
    Args:
        request: Chat history request containing user IDs and pagination params
        chat_service: Chat service instance
        
    Returns:
        ChatHistoryResponse with messages and total count
        
    Raises:
        HTTPException: If fetching conversation history fails
    """
    try:
        history = await chat_service.get_conversation_history(
            current_user_id=request.user_id,
            other_user_id=request.other_user_id,
            limit=request.limit,
            offset=request.offset
        )
        return history
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch conversation history: {str(e)}"
        )
