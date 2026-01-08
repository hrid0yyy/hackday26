"""Chatbot service layer with database integration."""

from typing import Optional, List, Dict
from fastapi import HTTPException, status
from src.core.db import supabase_client
from src.modules.chatbot.models import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    MessageResponse,
)
from src.modules.chatbot.agent import chatbot_agent


class ChatbotService:
    """Service class for handling chatbot operations."""
    
    def __init__(self):
        """Initialize the chatbot service."""
        self.supabase = supabase_client
        self.agent = chatbot_agent
    
    async def chat(self, request: ChatRequest, user_id: str) -> ChatResponse:
        """
        Process a chat request and manage conversation.
        
        Args:
            request: Chat request data
            user_id: Authenticated user ID
            
        Returns:
            ChatResponse: Chat response with conversation ID
            
        Raises:
            HTTPException: If chat processing fails
        """
        try:
            conversation_id = request.conversation_id
            title = None
            
            # If no conversation ID, create a new conversation
            if not conversation_id:
                # Generate title using AI
                title = await self.agent.generate_title(request.message)
                
                # Create new conversation (user_id auto-populated by Supabase RLS)
                conversation_result = self.supabase.table("conversation").insert({
                    "title": title
                }).execute()
                
                if not conversation_result.data:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create conversation"
                    )
                
                conversation_id = conversation_result.data[0]["id"]
            else:
                # Verify conversation exists (RLS will ensure user can only access their own)
                conversation_check = self.supabase.table("conversation").select("id").eq(
                    "id", conversation_id
                ).execute()
                
                if not conversation_check.data:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Conversation not found or access denied"
                    )
            
            # Get chat history for context
            chat_history = await self._get_chat_history(conversation_id)
            
            # Insert user message
            user_message_result = self.supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "role": "user",
                "content": request.message
            }).execute()
            
            if not user_message_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save user message"
                )
            
            # Get agent response
            agent_response = await self.agent.chat(request.message, chat_history)
            
            # Insert assistant message
            assistant_message_result = self.supabase.table("messages").insert({
                "conversation_id": conversation_id,
                "role": "assistant",
                "content": agent_response
            }).execute()
            
            if not assistant_message_result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to save assistant message"
                )
            
            return ChatResponse(
                conversation_id=conversation_id,
                message=agent_response,
                title=title
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Chat processing failed: {str(e)}"
            )
    
    async def _get_chat_history(self, conversation_id: int) -> List[Dict[str, str]]:
        """
        Get chat history for a conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of messages in format [{"role": "user/assistant", "content": "..."}]
        """
        try:
            # Get messages ordered by creation time
            messages_result = self.supabase.table("messages").select(
                "role, content"
            ).eq(
                "conversation_id", conversation_id
            ).order("created_at", desc=False).execute()
            
            if not messages_result.data:
                return []
            
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages_result.data
            ]
            
        except Exception:
            return []
    
    async def get_user_conversations(self, user_id: str) -> List[ConversationResponse]:
        """
        Get all conversations for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of conversations
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            # RLS ensures user only sees their own conversations
            result = self.supabase.table("conversation").select(
                "id, title, created_at, user_id"
            ).order("created_at", desc=True).execute()
            
            if not result.data:
                return []
            
            return [
                ConversationResponse(
                    id=conv["id"],
                    title=conv["title"],
                    created_at=conv["created_at"],
                    user_id=conv["user_id"]
                )
                for conv in result.data
            ]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversations: {str(e)}"
            )
    
    async def get_conversation_messages(
        self, conversation_id: str, user_id: str
    ) -> List[MessageResponse]:
        """
        Get all messages in a conversation.
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID (for verification)
            
        Returns:
            List of messages
            
        Raises:
            HTTPException: If retrieval fails or access denied
        """
        try:
            # RLS ensures user can only access their own conversation's messages
            # Get messages
            result = self.supabase.table("messages").select(
                "id, conversation_id, role, content, created_at"
            ).eq(
                "conversation_id", conversation_id
            ).order("created_at", desc=False).execute()
            
            if not result.data:
                return []
            
            return [
                MessageResponse(
                    id=msg["id"],
                    conversation_id=msg["conversation_id"],
                    role=msg["role"],
                    content=msg["content"],
                    created_at=msg["created_at"]
                )
                for msg in result.data
            ]
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get messages: {str(e)}"
            )


# Create singleton instance
chatbot_service = ChatbotService()
