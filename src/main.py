"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.modules.authentication import router as auth_router
from src.modules.chatbot import router as chatbot_router
from src.modules.chat import router as chat_router
from src.modules.sign_detection import router as sign_detection_router
from src.modules.general import router as general_router
from src.modules.speech_to_text import router as speech_to_text_router

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hackday backend",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(chatbot_router)
app.include_router(chat_router)
app.include_router(sign_detection_router)
app.include_router(general_router)
app.include_router(speech_to_text_router)

# Optional: Warmup the model at startup
@app.on_event("startup")
async def startup_event():
    from src.modules.sign_detection.service import get_service_instance
    service = get_service_instance()
    service.warmup()


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Hello Hackday!uth",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
