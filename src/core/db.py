"""Supabase database client initialization."""

from supabase import create_client, Client
from src.core.config import settings


def get_supabase_client() -> Client:
    """
    Get Supabase client instance with anon key.
    This respects Row Level Security (RLS) policies.
    
    Returns:
        Client: Supabase client
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


def get_supabase_admin_client() -> Client:
    """
    Get Supabase client instance with service role key.
    This BYPASSES Row Level Security (RLS) policies.
    Use only for backend operations that need elevated privileges.
    
    Returns:
        Client: Supabase admin client
    """
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


# Initialize global client (respects RLS)
supabase_client = get_supabase_client()

# Initialize admin client (bypasses RLS)
supabase_admin_client = get_supabase_admin_client()
