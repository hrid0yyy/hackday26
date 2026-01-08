"""Authentication service layer with Supabase integration."""

from typing import Optional
from fastapi import HTTPException, status
from src.core.db import supabase_client
from src.core.config import settings
from src.modules.authentication.models import (
    SignUpRequest,
    SignInRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    AuthResponse,
    UserResponse,
    MessageResponse,
)
from src.modules.authentication.utils import (
    format_user_metadata,
    get_token_expiry_seconds,
)


class AuthenticationService:
    """Service class for handling authentication operations."""
    
    def __init__(self):
        """Initialize the authentication service."""
        self.supabase = supabase_client
    
    async def sign_up(self, request: SignUpRequest) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            request: Sign up request data
            
        Returns:
            AuthResponse: Authentication response with tokens
            
        Raises:
            HTTPException: If sign up fails
        """
        try:
            # Create user with Supabase Auth (RLS will handle permissions)
            response = self.supabase.auth.sign_up({
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.full_name,
                        "status": request.status
                    },
                    "email_redirect_to": None  # Disable email verification
                }
            })
            
            if not response.user or not response.session:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
            
            # Create profile record in profiles table
            try:
                profile_data = {
                    "id": response.user.id,
                    "status": request.status or "normal"
                }
                self.supabase.table("profiles").insert(profile_data).execute()
            except Exception as profile_error:
                # If profile creation fails, log but don't fail signup
                # The user is already created in auth.users
                print(f"Warning: Failed to create profile: {profile_error}")
            
            # Use Supabase's JWT tokens directly
            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            expires_in = get_token_expiry_seconds(response.session.expires_at)
            
            # Prepare user response
            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=request.full_name,
                email_verified=response.user.email_confirmed_at is not None,
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at
            )
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                user=user_response
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Sign up failed: {str(e)}"
            )
    
    async def sign_in(self, request: SignInRequest) -> AuthResponse:
        """
        Authenticate a user and return tokens.
        
        Args:
            request: Sign in request data
            
        Returns:
            AuthResponse: Authentication response with tokens
            
        Raises:
            HTTPException: If authentication fails
        """
        try:
            # Authenticate with Supabase
            response = self.supabase.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if not response.user or not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            # Use Supabase's JWT tokens directly
            access_token = response.session.access_token
            refresh_token = response.session.refresh_token
            expires_in = get_token_expiry_seconds(response.session.expires_at)
            
            # Get user metadata
            user_metadata = response.user.user_metadata or {}
            
            # Prepare user response
            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_metadata.get("full_name"),
                email_verified=response.user.email_confirmed_at is not None,
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at
            )
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=expires_in,
                user=user_response
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    
    async def sign_out(self, access_token: str) -> MessageResponse:
        """
        Sign out a user and invalidate their session.
        
        Args:
            access_token: User's access token
            
        Returns:
            MessageResponse: Success message
            
        Raises:
            HTTPException: If sign out fails
        """
        try:
            # Set the access token for the session
            self.supabase.auth.set_session(access_token, access_token)
            
            # Sign out from Supabase
            self.supabase.auth.sign_out()
            
            return MessageResponse(
                message="Successfully signed out",
                success=True
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Sign out failed: {str(e)}"
            )
    
    async def forgot_password(self, request: ForgotPasswordRequest) -> MessageResponse:
        """
        Send password reset email to user.
        
        Args:
            request: Forgot password request data
            
        Returns:
            MessageResponse: Success message
            
        Raises:
            HTTPException: If operation fails
        """
        try:
            redirect_url = request.redirect_url or f"{settings.FRONTEND_URL}/reset-password"
            
            # Request password reset from Supabase
            self.supabase.auth.reset_password_email(
                request.email,
                options={"redirect_to": redirect_url}
            )
            
            # Always return success to prevent email enumeration
            return MessageResponse(
                message="If the email exists, a password reset link has been sent",
                success=True
            )
            
        except Exception as e:
            # Return success even on error to prevent email enumeration
            return MessageResponse(
                message="If the email exists, a password reset link has been sent",
                success=True
            )
    
    async def reset_password(self, request: ResetPasswordRequest) -> MessageResponse:
        """
        Reset user password using reset token.
        
        Args:
            request: Reset password request data
            
        Returns:
            MessageResponse: Success message
            
        Raises:
            HTTPException: If password reset fails
        """
        try:
            # Verify the reset token and update password
            response = self.supabase.auth.update_user({
                "password": request.new_password
            })
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid or expired reset token"
                )
            
            return MessageResponse(
                message="Password successfully reset",
                success=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reset password. Token may be invalid or expired"
            )
    
    async def change_password(self, user_id: str, request: ChangePasswordRequest) -> MessageResponse:
        """
        Change user password (requires authentication).
        
        Args:
            user_id: Authenticated user ID
            request: Change password request data
            
        Returns:
            MessageResponse: Success message
            
        Raises:
            HTTPException: If password change fails
        """
        try:
            # Verify user is authenticated and update password
            # Note: Supabase validates the current session automatically
            response = self.supabase.auth.update_user({
                "password": request.new_password
            })
            
            if not response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to change password"
                )
            
            return MessageResponse(
                message="Password successfully changed",
                success=True
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to change password: {str(e)}"
            )
    
    async def refresh_access_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh access token using refresh token.
        
        Args:
            refresh_token: Refresh token from Supabase
            
        Returns:
            AuthResponse: New authentication tokens
            
        Raises:
            HTTPException: If token refresh fails
        """
        try:
            # Use Supabase's refresh token method
            response = self.supabase.auth.refresh_session(refresh_token)
            
            if not response.user or not response.session:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired refresh token"
                )
            
            # Get user metadata
            user_metadata = response.user.user_metadata or {}
            
            # Prepare user response
            user_response = UserResponse(
                id=response.user.id,
                email=response.user.email,
                full_name=user_metadata.get("full_name"),
                email_verified=response.user.email_confirmed_at is not None,
                created_at=response.user.created_at,
                last_sign_in_at=response.user.last_sign_in_at
            )
            
            return AuthResponse(
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="bearer",
                expires_in=get_token_expiry_seconds(response.session.expires_at),
                user=user_response
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to refresh token"
            )
    
    async def get_current_user(self, user_id: str) -> UserResponse:
        """
        Get current authenticated user details.
        
        Args:
            user_id: User ID from token
            
        Returns:
            UserResponse: User details
            
        Raises:
            HTTPException: If user not found
        """
        try:
            # Get user from Supabase using their token context
            # This respects RLS and only returns data the user can access
            user_response = self.supabase.auth.get_user()
            
            if not user_response or not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user = user_response.user
            # Get user metadata
            user_metadata = user.user_metadata or {}
            
            return UserResponse(
                id=user.id,
                email=user.email,
                full_name=user_metadata.get("full_name"),
                email_verified=user.email_confirmed_at is not None,
                created_at=user.created_at,
                last_sign_in_at=user.last_sign_in_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user details: {str(e)}"
            )


# Create a singleton instance
auth_service = AuthenticationService()
