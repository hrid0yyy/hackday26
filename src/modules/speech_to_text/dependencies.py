"""Dependency injection for Speech to Text module."""

from typing import Generator

from .service import SpeechToTextService, get_service_instance


def get_speech_service() -> Generator[SpeechToTextService, None, None]:
    """Dependency function to provide SpeechToTextService instance.

    This function is used with FastAPI's Depends() for dependency injection.

    Yields:
        SpeechToTextService: The initialized speech to text service.
    """
    service = get_service_instance()
    yield service
