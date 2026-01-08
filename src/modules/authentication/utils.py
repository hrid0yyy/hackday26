"""Utility functions for authentication."""

from typing import Optional


def format_user_metadata(user_metadata: Optional[dict]) -> dict:
    """
    Format user metadata from Supabase.
    
    Args:
        user_metadata: User metadata dict from Supabase
        
    Returns:
        dict: Formatted metadata
    """
    if not user_metadata:
        return {}
    return user_metadata


def get_token_expiry_seconds(expires_at: Optional[int]) -> int:
    """
    Calculate token expiry in seconds.
    
    Args:
        expires_at: Token expiration timestamp
        
    Returns:
        int: Seconds until expiration (default 3600 if not provided)
    """
    if not expires_at:
        return 3600  # Default 1 hour
    
    from datetime import datetime
    now = datetime.utcnow().timestamp()
    expiry = max(0, int(expires_at - now))
    return expiry if expiry > 0 else 3600
