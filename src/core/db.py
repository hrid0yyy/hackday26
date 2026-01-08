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


# Initialize global client (respects RLS)
supabase_client = get_supabase_client()
