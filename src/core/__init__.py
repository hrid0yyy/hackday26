"""Core module for database and configuration."""

from .config import settings
from .db import supabase_client, get_supabase_client

__all__ = [
    "settings",
    "supabase_client",
    "get_supabase_client",
]
