"""
auth/provider.py
Pluggable Authentication Providers.
Implements Supabase Auth provider with JWT decoding, remote token validation,
and a robust Dev/Fallback provider for local development resilience.
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import jwt
import httpx

from .config import auth_config
from .models import UserContext, UserRole, UserProfile, SignUpRequest, SignInRequest, RefreshTokenRequest, TokenResponse

logger = logging.getLogger("hirelens.auth")


class BaseAuthProvider(ABC):
    """Abstract Authentication Provider interface for clean extensibility."""

    @abstractmethod
    def verify_token(self, token: str) -> UserContext:
        """Validates bearer access token and returns UserContext."""
        pass

    @abstractmethod
    def sign_up(self, req: SignUpRequest) -> TokenResponse:
        """Registers a new user."""
        pass

    @abstractmethod
    def sign_in(self, req: SignInRequest) -> TokenResponse:
        """Authenticates user credentials."""
        pass

    @abstractmethod
    def refresh_token(self, req: RefreshTokenRequest) -> TokenResponse:
        """Refreshes expired access token."""
        pass


class SupabaseAuthProvider(BaseAuthProvider):
    """
    Production Supabase Authentication Provider.
    Communicates with Supabase GoTrue Auth API and verifies tokens either
    via local JWT secret (sub-millisecond) or remote /auth/v1/user endpoint.
    """

    def __init__(self):
        self.supabase_url = auth_config.supabase_url
        self.anon_key = auth_config.supabase_anon_key or ""
        self.service_role_key = auth_config.supabase_service_role_key or ""
        self.jwt_secret = auth_config.supabase_jwt_secret
        # In-memory TTL token cache: token -> (user_context, expiry_timestamp)
        self._cache: Dict[str, tuple[UserContext, float]] = {}

    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "apikey": self.anon_key or self.service_role_key or "",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def verify_token(self, token: str) -> UserContext:
        # 1. Check TTL cache
        now = time.time()
        if token in self._cache:
            cached_user, expires_at = self._cache[token]
            if now < expires_at:
                return cached_user
            else:
                del self._cache[token]

        # 2. Fast-path: local JWT decode if secret is provided
        if self.jwt_secret:
            try:
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_aud": False}
                )
                user_id = payload.get("sub")
                email = payload.get("email", "")
                user_meta = payload.get("user_metadata", {})
                role_str = user_meta.get("role") or payload.get("role") or "recruiter"
                try:
                    role = UserRole(role_str)
                except ValueError:
                    role = UserRole.RECRUITER

                user = UserContext(
                    user_id=user_id,
                    email=email,
                    role=role,
                    full_name=user_meta.get("full_name") or user_meta.get("name"),
                    metadata=user_meta,
                    provider="supabase"
                )
                exp = payload.get("exp", now + 300)
                self._cache[token] = (user, min(now + 60, exp))
                return user
            except jwt.ExpiredSignatureError:
                raise ValueError("Session token has expired. Please sign in again.")
            except Exception as e:
                logger.warning(f"Local JWT decode failed, attempting remote verification: {e}")

        # 3. Remote verification via Supabase GoTrue /auth/v1/user
        if not self.anon_key and not self.service_role_key:
            # If no API key configured, attempt to decode unverified for dev inspection
            try:
                payload = jwt.decode(token, options={"verify_signature": False})
                user_id = payload.get("sub", "dev_user")
                email = payload.get("email", "recruiter@hirelens.ai")
                user_meta = payload.get("user_metadata", {})
                role_val = user_meta.get("role") or UserRole.RECRUITER
                return UserContext(
                    user_id=user_id,
                    email=email,
                    role=UserRole(role_val) if role_val in [r.value for r in UserRole] else UserRole.RECRUITER,
                    full_name=user_meta.get("full_name", "HireLens User"),
                    metadata=user_meta,
                    provider="supabase-unverified"
                )
            except Exception as e:
                raise ValueError(f"Invalid token format: {e}")

        url = f"{self.supabase_url}/auth/v1/user"
        try:
            with httpx.Client(timeout=6.0) as client:
                res = client.get(url, headers=self._get_headers(token))
                if res.status_code == 200:
                    data = res.json()
                    user_meta = data.get("user_metadata", {})
                    role_str = user_meta.get("role") or data.get("role") or "recruiter"
                    try:
                        role = UserRole(role_str)
                    except ValueError:
                        role = UserRole.RECRUITER

                    user = UserContext(
                        user_id=data.get("id"),
                        email=data.get("email"),
                        role=role,
                        full_name=user_meta.get("full_name") or user_meta.get("name"),
                        metadata=user_meta,
                        provider="supabase"
                    )
                    self._cache[token] = (user, now + 60)
                    return user
                else:
                    detail = res.json().get("msg") or res.json().get("error_description") or "Invalid token"
                    raise ValueError(f"Supabase token validation failed: {detail}")
        except httpx.RequestError as e:
            logger.error(f"Network error verifying Supabase token: {e}")
            raise ValueError(f"Authentication service temporarily unavailable: {e}")

    def sign_up(self, req: SignUpRequest) -> TokenResponse:
        url = f"{self.supabase_url}/auth/v1/signup"
        payload = {
            "email": req.email,
            "password": req.password,
            "data": {
                "full_name": req.full_name,
                "role": req.role.value if req.role else UserRole.RECRUITER.value
            }
        }
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, headers=self._get_headers(), json=payload)
            if res.status_code in (200, 201):
                data = res.json()
                # If Supabase requires email confirmation, session might be None initially
                access_token = data.get("access_token") or "pending_confirmation"
                user_data = data.get("user") or data
                user_meta = user_data.get("user_metadata", {})
                profile = UserProfile(
                    id=user_data.get("id", "temp_id"),
                    email=user_data.get("email", req.email),
                    full_name=user_meta.get("full_name", req.full_name),
                    role=req.role or UserRole.RECRUITER,
                    metadata=user_meta
                )
                return TokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    expires_in=data.get("expires_in", 3600),
                    refresh_token=data.get("refresh_token"),
                    user=profile
                )
            else:
                err = res.json().get("msg") or res.json().get("error_description") or res.text
                raise ValueError(f"Supabase sign-up failed: {err}")

    def sign_in(self, req: SignInRequest) -> TokenResponse:
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        payload = {
            "email": req.email,
            "password": req.password
        }
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, headers=self._get_headers(), json=payload)
            if res.status_code == 200:
                data = res.json()
                user_data = data.get("user", {})
                user_meta = user_data.get("user_metadata", {})
                role_str = user_meta.get("role") or UserRole.RECRUITER.value
                try:
                    role = UserRole(role_str)
                except ValueError:
                    role = UserRole.RECRUITER

                profile = UserProfile(
                    id=user_data.get("id"),
                    email=user_data.get("email"),
                    full_name=user_meta.get("full_name"),
                    role=role,
                    metadata=user_meta
                )
                return TokenResponse(
                    access_token=data.get("access_token"),
                    token_type="bearer",
                    expires_in=data.get("expires_in", 3600),
                    refresh_token=data.get("refresh_token"),
                    user=profile
                )
            else:
                err = res.json().get("error_description") or res.json().get("msg") or "Invalid email or password"
                raise ValueError(f"Sign-in failed: {err}")

    def refresh_token(self, req: RefreshTokenRequest) -> TokenResponse:
        url = f"{self.supabase_url}/auth/v1/token?grant_type=refresh_token"
        payload = {"refresh_token": req.refresh_token}
        with httpx.Client(timeout=8.0) as client:
            res = client.post(url, headers=self._get_headers(), json=payload)
            if res.status_code == 200:
                data = res.json()
                user_data = data.get("user", {})
                user_meta = user_data.get("user_metadata", {})
                profile = UserProfile(
                    id=user_data.get("id"),
                    email=user_data.get("email"),
                    full_name=user_meta.get("full_name"),
                    role=UserRole(user_meta.get("role", UserRole.RECRUITER.value)),
                    metadata=user_meta
                )
                return TokenResponse(
                    access_token=data.get("access_token"),
                    token_type="bearer",
                    expires_in=data.get("expires_in", 3600),
                    refresh_token=data.get("refresh_token"),
                    user=profile
                )
            else:
                err = res.json().get("error_description") or "Invalid refresh token"
                raise ValueError(f"Refresh failed: {err}")


class DevFallbackAuthProvider(BaseAuthProvider):
    """
    Local fallback authentication provider used in development or testing
    when Supabase keys or internet connectivity are not available.
    Generates standard HS256 JWTs using dev secret.
    """

    def __init__(self):
        self.secret = auth_config.dev_jwt_secret
        # In-memory user store for development mode
        self.users_db: Dict[str, Dict[str, Any]] = {
            "recruiter@hirelens.ai": {
                "id": "usr_dev_recruiter_01",
                "password": "password123",
                "full_name": "Alex Mercer",
                "role": UserRole.RECRUITER
            },
            "admin@hirelens.ai": {
                "id": "usr_dev_admin_01",
                "password": "adminpassword123",
                "full_name": "Dev Administrator",
                "role": UserRole.ADMIN
            }
        }

    def verify_token(self, token: str) -> UserContext:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            role_val = payload.get("role", UserRole.RECRUITER.value)
            try:
                role = UserRole(role_val)
            except ValueError:
                role = UserRole.RECRUITER

            return UserContext(
                user_id=payload.get("sub", "dev_user"),
                email=payload.get("email", ""),
                role=role,
                full_name=payload.get("name"),
                metadata=payload.get("metadata", {}),
                provider="dev-fallback"
            )
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired.")
        except Exception as e:
            raise ValueError(f"Invalid token signature: {e}")

    def sign_up(self, req: SignUpRequest) -> TokenResponse:
        email = req.email.lower()
        if email in self.users_db:
            raise ValueError(f"User with email '{email}' already exists.")
        
        user_id = f"usr_dev_{int(time.time())}"
        self.users_db[email] = {
            "id": user_id,
            "password": req.password,
            "full_name": req.full_name or "HireLens User",
            "role": req.role or UserRole.RECRUITER
        }
        return self._build_token_response(user_id, email, req.full_name or "HireLens User", req.role or UserRole.RECRUITER)

    def sign_in(self, req: SignInRequest) -> TokenResponse:
        email = req.email.lower()
        user_record = self.users_db.get(email)
        if not user_record or user_record["password"] != req.password:
            # In dev mode, auto-create if not found to provide effortless testing!
            user_id = f"usr_dev_{int(time.time())}"
            self.users_db[email] = {
                "id": user_id,
                "password": req.password,
                "full_name": email.split("@")[0].title(),
                "role": UserRole.RECRUITER
            }
            user_record = self.users_db[email]

        return self._build_token_response(
            user_record["id"], email, user_record["full_name"], user_record["role"]
        )

    def refresh_token(self, req: RefreshTokenRequest) -> TokenResponse:
        # Dev refresh generates new token with standard recruiter role
        return self._build_token_response("usr_dev_refreshed", "recruiter@hirelens.ai", "Alex Mercer", UserRole.RECRUITER)

    def _build_token_response(self, user_id: str, email: str, name: str, role: UserRole) -> TokenResponse:
        now = int(time.time())
        payload = {
            "sub": user_id,
            "email": email,
            "name": name,
            "role": role.value,
            "iat": now,
            "exp": now + 86400  # 24 hours
        }
        token = jwt.encode(payload, self.secret, algorithm="HS256")
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=86400,
            refresh_token=f"ref_{token[:16]}",
            user=UserProfile(
                id=user_id,
                email=email,
                full_name=name,
                role=role
            )
        )


# Singleton instance resolution
_supabase_provider = None
_dev_provider = None

def get_auth_provider() -> BaseAuthProvider:
    global _supabase_provider, _dev_provider
    if auth_config.is_supabase_configured:
        if _supabase_provider is None:
            _supabase_provider = SupabaseAuthProvider()
        return _supabase_provider
    else:
        if _dev_provider is None:
            _dev_provider = DevFallbackAuthProvider()
        return _dev_provider
