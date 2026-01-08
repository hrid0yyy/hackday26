"""Service layer for general module."""

from typing import Optional
from fastapi import HTTPException, status
from src.core.db import supabase_admin_client


class GeneralService:
    """Service class for general operations."""
    
    def __init__(self):
        """Initialize the general service."""
        self.supabase = supabase_admin_client
    
    async def search_user_by_email(self, email: str) -> Optional[dict]:
        """
        Search for a user by email address.
        
        Args:
            email: Email address to search for
            
        Returns:
            User data if found, None otherwise
            
        Raises:
            HTTPException: If search fails
        """
        try:
            # Use admin client to list users and find by email
            # Supabase doesn't have a direct email search, so we list and filter
            users_response = self.supabase.auth.admin.list_users()
            
            # Find user with matching email
            user_data = None
            for user in users_response:
                if user.email and user.email.lower() == email.lower():
                    user_data = user
                    break
            
            if not user_data:
                return None
            
            # Get profile data if exists
            profile_data = None
            try:
                profile_response = self.supabase.table("profiles").select(
                    "status"
                ).eq("id", user_data.id).execute()
                
                if profile_response.data:
                    profile_data = profile_response.data[0]
            except Exception as profile_error:
                # Profile might not exist, that's okay
                pass
            
            # Combine user and profile data
            result = {
                "id": user_data.id,
                "email": user_data.email,
                "full_name": user_data.user_metadata.get("full_name") if user_data.user_metadata else None,
                "status": profile_data.get("status") if profile_data else None
            }
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"User search failed: {str(e)}"
            )


# Global service instance
general_service = GeneralService()
