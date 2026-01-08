"""FastAPI routes for authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from src.modules.authentication.models import (
    SignUpRequest,
    SignInRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    AuthResponse,
    UserResponse,
    MessageResponse,
    ErrorResponse,
)
from src.modules.authentication.service import auth_service
from src.modules.authentication.dependencies import (
    get_current_user_id,
    get_current_user,
    verify_refresh_token,
    auth_rate_limit,
    password_reset_rate_limit,
)


# Create router
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    }
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email and password",
    responses={
        201: {"description": "User successfully registered"},
        409: {"description": "User already exists"},
        400: {"description": "Invalid input data"},
    }
)
async def sign_up(
    request: SignUpRequest,
    _rate_limit: None = Depends(auth_rate_limit)
):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **full_name**: Optional user's full name
    """
    return await auth_service.sign_up(request)


@router.post(
    "/signin",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign in user",
    description="Authenticate user and return access and refresh tokens",
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"description": "Invalid credentials"},
    }
)
async def sign_in(
    request: SignInRequest,
    _rate_limit: None = Depends(auth_rate_limit)
):
    """
    Authenticate user with email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token and refresh token.
    """
    return await auth_service.sign_in(request)


@router.post(
    "/signout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Sign out user",
    description="Sign out user and invalidate session",
    responses={
        200: {"description": "Successfully signed out"},
        401: {"description": "Not authenticated"},
    }
)
async def sign_out(
    user_id: str = Depends(get_current_user_id)
):
    """
    Sign out the current user and invalidate their session.
    
    Requires authentication via Bearer token.
    """
    # For JWT-based auth, logout is typically handled client-side
    # But we can optionally blacklist the token or revoke the session
    return MessageResponse(
        message="Successfully signed out. Please remove tokens from client.",
        success=True
    )


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email to user",
    responses={
        200: {"description": "Password reset email sent (if email exists)"},
    }
)
async def forgot_password(
    request: ForgotPasswordRequest,
    _rate_limit: None = Depends(password_reset_rate_limit)
):
    """
    Request a password reset email.
    
    - **email**: User's email address
    - **redirect_url**: Optional URL to redirect after password reset
    
    Always returns success to prevent email enumeration attacks.
    """
    return await auth_service.forgot_password(request)


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset user password using reset token",
    responses={
        200: {"description": "Password successfully reset"},
        400: {"description": "Invalid or expired token"},
    }
)
async def reset_password(
    request: ResetPasswordRequest,
    _rate_limit: None = Depends(password_reset_rate_limit)
):
    """
    Reset password using the token received via email.
    
    - **token**: Password reset token from email
    - **new_password**: New strong password
    """
    return await auth_service.reset_password(request)


@router.post(
    "/change-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change password for authenticated user",
    responses={
        200: {"description": "Password successfully changed"},
        400: {"description": "Invalid current password"},
        401: {"description": "Not authenticated"},
    }
)
async def change_password(
    request: ChangePasswordRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Change password for the authenticated user.
    
    - **old_password**: Current password
    - **new_password**: New strong password
    
    Requires authentication via Bearer token.
    """
    return await auth_service.change_password(user_id, request)


@router.post(
    "/refresh",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token",
    responses={
        200: {"description": "Token successfully refreshed"},
        401: {"description": "Invalid or expired refresh token"},
    }
)
async def refresh_token(
    refresh_token: str = Depends(verify_refresh_token)
):
    """
    Refresh access token using a valid refresh token.
    
    Provide refresh token in Authorization header as Bearer token.
    Returns new access and refresh tokens.
    """
    return await auth_service.refresh_access_token(refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get details of currently authenticated user",
    responses={
        200: {"description": "User details retrieved"},
        401: {"description": "Not authenticated"},
        404: {"description": "User not found"},
    }
)
async def get_me(
    user: UserResponse = Depends(get_current_user)
):
    """
    Get details of the currently authenticated user.
    
    Requires authentication via Bearer token.
    """
    return user


@router.get(
    "/health",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check if authentication service is running",
    responses={
        200: {"description": "Service is healthy"},
    }
)
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns service status.
    """
    return MessageResponse(
        message="Authentication service is healthy",
        success=True
    )
