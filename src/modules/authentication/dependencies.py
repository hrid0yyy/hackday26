"""FastAPI dependencies for authentication."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.core.db import supabase_client
from src.modules.authentication.service import auth_service


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Get current authenticated user ID from Supabase JWT token.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        str: User ID
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        user = supabase_client.auth.get_user(token)
        
        if not user or not user.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user.user.id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: str = Depends(get_current_user_id)
):
    """
    Get current authenticated user details.
    
    Args:
        user_id: User ID from token
        
    Returns:
        UserResponse: Current user details
        
    Raises:
        HTTPException: If user not found
    """
    return await auth_service.get_current_user(user_id)


async def get_optional_current_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[str]:
    """
    Get current user ID if authenticated, None otherwise.
    Useful for optional authentication endpoints.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Optional[str]: User ID if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user = supabase_client.auth.get_user(token)
        
        if not user or not user.user:
            return None
        
        return user.user.id
    except:
        return None


async def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and return refresh token from Authorization header.
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        str: Refresh token
        
    Raises:
        HTTPException: If token is missing
    """
    token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


class RateLimitDependency:
    """
    Rate limiting dependency (placeholder for future implementation).
    Can be integrated with Redis or other rate limiting solutions.
    """
    
    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_requests: Maximum requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    async def __call__(self) -> None:
        """
        Check rate limit (placeholder implementation).
        
        Raises:
            HTTPException: If rate limit exceeded
        """
        # TODO: Implement actual rate limiting logic with Redis
        # For now, this is a placeholder
        pass


# Pre-configured rate limiters
auth_rate_limit = RateLimitDependency(max_requests=5, window_seconds=60)

password_reset_rate_limit = RateLimitDependency(max_requests=3, window_seconds=300)
    