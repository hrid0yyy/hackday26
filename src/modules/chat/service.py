"""Chat service for conversation history management."""

from typing import Optional
from supabase import Client
from postgrest.exceptions import APIError

from .models import ChatMessage, ChatHistoryResponse


class ChatService:
    """Service for managing chat conversations."""
    
    def __init__(self, supabase: Client):
        """Initialize the chat service.
        
        Args:
            supabase: Supabase client instance
        """
        self.supabase = supabase
    
    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message: str
    ) -> ChatMessage:
        """Send a message between two users.
        
        Args:
            sender_id: Sender user's ID
            receiver_id: Receiver user's ID
            message: Message text to send
            
        Returns:
            ChatMessage with the created message details
            
        Raises:
            Exception: If message creation fails
        """
        try:
            # Insert message into chat_conversation table
            message_data = {
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "cleaned_text": message,
                "raw_text": message
            }
            
            response = self.supabase.table("chat_conversation") \
                .insert(message_data) \
                .execute()
            
            if not response.data:
                raise Exception("Failed to create message")
            
            # Convert to ChatMessage model
            msg = response.data[0]
            return ChatMessage(
                id=msg["id"],
                sender_id=msg["sender_id"],
                receiver_id=msg["receiver_id"],
                raw_text=msg.get("raw_text"),
                cleaned_text=msg.get("cleaned_text"),
                created_at=msg["created_at"]
            )
            
        except APIError as e:
            raise Exception(f"Failed to send message: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error sending message: {str(e)}")
    
    async def get_conversation_history(
        self,
        current_user_id: str,
        other_user_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> ChatHistoryResponse:
        """Get conversation history between two users.
        
        Retrieves all messages where the current user is either sender or receiver,
        and the other user is either receiver or sender.
        
        Args:
            current_user_id: Current authenticated user's ID
            other_user_id: The other user's ID to get conversation with
            limit: Maximum number of messages to return (optional)
            offset: Number of messages to skip for pagination
            
        Returns:
            ChatHistoryResponse with messages and total count
            
        Raises:
            Exception: If database query fails
        """
        try:
            # Build query for messages between the two users
            # Get messages where:
            # (sender = current_user AND receiver = other_user) OR
            # (sender = other_user AND receiver = current_user)
            query = self.supabase.table("chat_conversation") \
                .select("*") \
                .or_(
                    f"and(sender_id.eq.{current_user_id},receiver_id.eq.{other_user_id}),"
                    f"and(sender_id.eq.{other_user_id},receiver_id.eq.{current_user_id})"
                ) \
                .order("created_at", desc=True)
            
            # Apply pagination if specified
            if limit is not None:
                query = query.range(offset, offset + limit - 1)
            
            # Execute query
            response = query.execute()
            
            # Convert to ChatMessage models
            messages = [
                ChatMessage(
                    id=msg["id"],
                    sender_id=msg["sender_id"],
                    receiver_id=msg["receiver_id"],
                    raw_text=msg.get("raw_text"),
                    cleaned_text=msg.get("cleaned_text"),
                    created_at=msg["created_at"]
                )
                for msg in response.data
            ]
            
            # Get total count for pagination info
            # Count query without pagination
            count_response = self.supabase.table("chat_conversation") \
                .select("id", count="exact") \
                .or_(
                    f"and(sender_id.eq.{current_user_id},receiver_id.eq.{other_user_id}),"
                    f"and(sender_id.eq.{other_user_id},receiver_id.eq.{current_user_id})"
                ) \
                .execute()
            
            total_count = count_response.count if count_response.count is not None else len(messages)
            
            return ChatHistoryResponse(
                user_id=other_user_id,
                messages=messages,
                total_count=total_count
            )
            
        except APIError as e:
            raise Exception(f"Failed to fetch conversation history: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error fetching conversation history: {str(e)}")
