"""Pydantic models for authentication requests and responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator
import re


class SignUpRequest(BaseModel):
    """Sign up request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    full_name: Optional[str] = Field(None, max_length=100, description="User's full name")
    status: Optional[str] = Field("normal", description="User status (mute, deaf, blind, normal)")
    
    @validator('status')
    def validate_status(cls, v):
        """Validate status is one of allowed values."""
        allowed = ['mute', 'deaf', 'blind', 'normal']
        if v not in allowed:
            raise ValueError(f'Status must be one of: {", ".join(allowed)}')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format."""
        if not v or '@' not in v:
            raise ValueError('Invalid email address')
        return v.lower()


class SignInRequest(BaseModel):
    """Sign in request model."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    @validator('email')
    def validate_email(cls, v):
        """Normalize email to lowercase."""
        return v.lower()


class ForgotPasswordRequest(BaseModel):
    """Forgot password request model."""
    email: EmailStr = Field(..., description="User email address")
    redirect_url: Optional[str] = Field(None, description="URL to redirect after password reset")
    
    @validator('email')
    def validate_email(cls, v):
        """Normalize email to lowercase."""
        return v.lower()


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="Refresh token")


class AuthResponse(BaseModel):
    """Authentication response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserResponse"


class UserResponse(BaseModel):
    """User response model."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="User's full name")
    email_verified: bool = Field(default=False, description="Email verification status")
    created_at: Optional[datetime] = Field(None, description="Account creation timestamp")
    last_sign_in_at: Optional[datetime] = Field(None, description="Last sign in timestamp")


class MessageResponse(BaseModel):
    """Generic message response model."""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Operation success status")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    success: bool = Field(default=False, description="Operation success status")


# Update forward references
AuthResponse.model_rebuild()
