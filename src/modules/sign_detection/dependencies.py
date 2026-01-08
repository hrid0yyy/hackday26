"""Dependency injection for Sign Language Detection module."""

from typing import Generator

from .service import SignLanguageService, get_service_instance


def get_sign_service() -> Generator[SignLanguageService, None, None]:
    """Dependency function to provide SignLanguageService instance.

    This function is used with FastAPI's Depends() for dependency injection.
    It ensures a single service instance is shared across all requests.

    Yields:
        SignLanguageService: The initialized sign language service.

    Example:
        ```python
        @router.post("/detect")
        async def detect(service: SignLanguageService = Depends(get_sign_service)):
            result = await service.predict_frame(image_bytes)
            return result
        ```
    """
    service = get_service_instance()
    yield service
