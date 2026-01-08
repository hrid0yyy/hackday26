"""API routes for general module."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends

from .models import UserSearchRequest, UserSearchResult
from .service import general_service
from src.modules.authentication.dependencies import get_current_user_id

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/general",
    tags=["General"],
)


@router.post("/search-user", response_model=Optional[UserSearchResult])
async def search_user_by_email(
    request: UserSearchRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Search for a user by email address.
    
    Requires authentication. Returns user details if found.
    
    Args:
        request: Contains email to search
        current_user_id: Authenticated user ID (from JWT)
        
    Returns:
        UserSearchResult if user found, None otherwise
    """
    try:
        logger.info(f"User {current_user_id} searching for: {request.email}")
        
        user_data = await general_service.search_user_by_email(request.email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserSearchResult(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search user: {str(e)}"
        )


@router.get("/search-user/{email}", response_model=Optional[UserSearchResult])
async def search_user_by_email_get(
    email: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Search for a user by email address (GET method).
    
    Requires authentication. Returns user details if found.
    
    Args:
        email: Email address to search for
        current_user_id: Authenticated user ID (from JWT)
        
    Returns:
        UserSearchResult if user found, None otherwise
    """
    try:
        logger.info(f"User {current_user_id} searching for: {email}")
        
        user_data = await general_service.search_user_by_email(email)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserSearchResult(**user_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching user: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search user: {str(e)}"
        )
