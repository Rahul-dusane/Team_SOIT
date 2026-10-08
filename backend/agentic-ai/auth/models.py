"""
auth/models.py
Pydantic contracts and schemas for authentication, authorization, and user contexts.
Designed for scalability, multi-tenancy, and RBAC expansion.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"
    VIEWER = "viewer"
    USER = "user"


class UserProfile(BaseModel):
    id: str = Field(..., description="Unique user UUID from Supabase auth.users")
    email: str = Field(..., description="Primary authenticated email address")
    full_name: Optional[str] = Field(default=None, description="Display name")
    role: UserRole = Field(default=UserRole.RECRUITER, description="Assigned role for RBAC")
    avatar_url: Optional[str] = Field(default=None, description="Profile picture URL")
    created_at: Optional[str] = Field(default=None, description="Account creation timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary custom user attributes")


class UserContext(BaseModel):
    """
    Lightweight, immutable context injected into FastAPI dependencies.
    Provides standard identity and role-checking helpers.
    """
    user_id: str
    email: str
    role: UserRole = UserRole.RECRUITER
    full_name: Optional[str] = None
    is_authenticated: bool = True
    provider: str = "supabase"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def has_role(self, *roles: UserRole) -> bool:
        """Helper to quickly check if user matches one of the provided roles."""
        return self.role in roles or self.role == UserRole.ADMIN


class SignUpRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=6, description="User password (min 6 chars)")
    full_name: Optional[str] = Field(default="", description="User full name")
    role: Optional[UserRole] = Field(default=UserRole.RECRUITER, description="Requested role")


class SignInRequest(BaseModel):
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Supabase refresh token")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = 3600
    refresh_token: Optional[str] = None
    user: UserProfile


class AuthStatus(BaseModel):
    status: str
    provider: str
    supabase_configured: bool
    supabase_url: str
    require_auth: bool
