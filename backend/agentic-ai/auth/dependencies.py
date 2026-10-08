"""
auth/dependencies.py
FastAPI dependency injection utilities for authentication and authorization.
Supports Supabase JWTs, API Key service authentication, and Role-Based Access Control (RBAC).
"""

import os
from typing import Optional, List
from fastapi import Depends, HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader

from .config import auth_config
from .models import UserContext, UserRole
from .provider import get_auth_provider

security_bearer = HTTPBearer(auto_error=False)
security_api_key = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_user(
    request: Request,
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key: Optional[str] = Security(security_api_key),
) -> UserContext:
    """
    Main authentication dependency for FastAPI endpoints.
    1. Checks Bearer JWT from Supabase session.
    2. Checks X-API-Key for machine-to-machine integrations.
    3. Respects REQUIRE_AUTH / TESTING flags.
    """
    # 1. Bypass during unit test execution if TESTING=true
    if auth_config.testing:
        return UserContext(
            user_id="test_runner",
            email="test@hirelens.ai",
            role=UserRole.ADMIN,
            full_name="Automated Test Runner",
            provider="test"
        )

    # 2. Check X-API-Key header (Machine-to-Machine / Service route)
    expected_api_key = auth_config.api_key
    raw_api_key = api_key or request.headers.get("x-api-key") or request.headers.get("X-API-Key")
    if raw_api_key and expected_api_key and raw_api_key == expected_api_key:
        return UserContext(
            user_id="service_account",
            email="service@hirelens.internal",
            role=UserRole.ADMIN,
            full_name="HireLens Service Account",
            provider="api-key"
        )

    # 3. Check Bearer token (Primary Supabase Auth route)
    bearer_token = None
    if auth_header and auth_header.credentials:
        bearer_token = auth_header.credentials
    else:
        auth_hdr = request.headers.get("authorization") or request.headers.get("Authorization")
        if auth_hdr and auth_hdr.lower().startswith("bearer "):
            bearer_token = auth_hdr[7:].strip()

    if bearer_token:
        try:
            provider = get_auth_provider()
            user_context = provider.verify_token(bearer_token)
            return user_context
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unauthorized: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Authentication failed: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # 4. If REQUIRE_AUTH=false and no credentials provided, return guest/dev context
    if not auth_config.require_auth:
        return UserContext(
            user_id="dev_user_01",
            email="developer@hirelens.ai",
            role=UserRole.RECRUITER,
            full_name="HireLens Recruiter",
            provider="dev-permissive"
        )

    # 5. Missing required credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized: Missing or invalid authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_user(
    auth_header: Optional[HTTPAuthorizationCredentials] = Security(security_bearer),
    api_key: Optional[str] = Security(security_api_key),
) -> Optional[UserContext]:
    """Optional authentication dependency; returns None if not authenticated instead of raising 401."""
    try:
        return await get_current_user(auth_header=auth_header, api_key=api_key)
    except HTTPException:
        return None


def require_role(*allowed_roles: UserRole):
    """
    Scalable Role-Based Access Control (RBAC) dependency factory.
    Example:
        @app.delete("/api/v1/candidates/{id}")
        def delete_candidate(user: UserContext = Depends(require_role(UserRole.ADMIN, UserRole.RECRUITER))):
            ...
    """
    async def role_checker(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if not current_user.has_role(*allowed_roles):
            role_names = [r.value for r in allowed_roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Action requires one of roles: {role_names}. Current role: '{current_user.role.value}'"
            )
        return current_user

    return role_checker
