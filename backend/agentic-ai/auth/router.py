"""
auth/router.py
FastAPI router exposing authentication endpoints:
- POST /api/v1/auth/signup
- POST /api/v1/auth/signin
- POST /api/v1/auth/refresh
- GET  /api/v1/auth/me
- GET  /api/v1/auth/status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from .models import (
    SignUpRequest,
    SignInRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserProfile,
    UserContext,
    AuthStatus,
)
from .dependencies import get_current_user
from .provider import get_auth_provider
from .config import auth_config

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])


@router.post("/signup", response_model=TokenResponse)
def sign_up(req: SignUpRequest):
    """Register a new user account with Supabase or active auth provider."""
    provider = get_auth_provider()
    try:
        return provider.sign_up(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/signin", response_model=TokenResponse)
def sign_in(req: SignInRequest):
    """Sign in using email and password, returning Supabase session token."""
    provider = get_auth_provider()
    try:
        return provider.sign_in(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest):
    """Refresh an expired session access token using refresh_token."""
    provider = get_auth_provider()
    try:
        return provider.refresh_token(req)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}",
        )


@router.get("/me", response_model=UserProfile)
def get_current_user_profile(user: UserContext = Depends(get_current_user)):
    """Retrieve profile and RBAC role for the currently authenticated user."""
    return UserProfile(
        id=user.user_id,
        email=user.email,
        full_name=user.full_name or user.email.split("@")[0].title(),
        role=user.role,
        metadata=user.metadata,
    )


@router.get("/status", response_model=AuthStatus)
def get_auth_status():
    """Verify live status of Supabase Authentication subsystem."""
    provider = get_auth_provider()
    provider_name = "supabase" if auth_config.is_supabase_configured else "dev-fallback"
    return AuthStatus(
        status="configured" if auth_config.is_supabase_configured else "dev_mode",
        provider=provider_name,
        supabase_configured=auth_config.is_supabase_configured,
        supabase_url=auth_config.supabase_url,
        require_auth=auth_config.require_auth,
    )
