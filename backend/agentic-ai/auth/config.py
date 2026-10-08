"""
auth/config.py
Configuration loader for HireLens authentication.
Supports Supabase URL, anon key, service key, JWT secret, and fallback dev modes.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class AuthConfig:
    def __init__(self):
        # 1. Supabase Host / URL
        supabase_host = os.getenv("SUPABASE_HOST", "").strip()
        raw_url = os.getenv("SUPABASE_URL") or os.getenv("VITE_SUPABASE_URL")
        
        if raw_url:
            self.supabase_url = raw_url.rstrip("/")
        elif supabase_host:
            # If supabase_host is e.g. db.grcihwgasjgofsrlhdox.supabase.co -> https://grcihwgasjgofsrlhdox.supabase.co
            project_ref = supabase_host.replace("db.", "").replace(".supabase.co", "")
            self.supabase_url = f"https://{project_ref}.supabase.co"
        else:
            self.supabase_url = "https://grcihwgasjgofsrlhdox.supabase.co"

        # 2. Supabase Keys
        self.supabase_anon_key: Optional[str] = (
            os.getenv("SUPABASE_ANON_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")
        )
        raw_jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
        raw_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if raw_jwt_secret and raw_jwt_secret.startswith("eyJ") and not raw_service_key:
            self.supabase_service_role_key = raw_jwt_secret
            self.supabase_jwt_secret = None
        elif raw_jwt_secret and raw_jwt_secret.startswith("eyJ"):
            self.supabase_service_role_key = raw_service_key
            self.supabase_jwt_secret = None
        else:
            self.supabase_service_role_key = raw_service_key
            self.supabase_jwt_secret = raw_jwt_secret

        # 3. Environment & Enforcements
        self.environment: str = os.getenv("ENVIRONMENT", "development").lower()
        self.testing: bool = os.getenv("TESTING", "false").lower() in ("true", "1")
        self.require_auth: bool = os.getenv("REQUIRE_AUTH", "false").lower() in ("true", "1")
        self.api_key: Optional[str] = os.getenv("API_KEY")

        # 4. Fallback dev signing secret (used when running locally without Supabase network)
        self.dev_jwt_secret: str = os.getenv("AUTH_DEV_SECRET", "hirelens-dev-secret-key-32chars-min-secure")

    @property
    def is_supabase_configured(self) -> bool:
        """True if Supabase URL and a real (non-placeholder) anon key or service role key are configured."""
        anon = (self.supabase_anon_key or "").strip()
        svc = (self.supabase_service_role_key or "").strip()
        has_real_anon = bool(
            anon and
            not anon.startswith("your_") and
            not anon.startswith("your-") and
            anon != "your_supabase_anon_key_here"
        )
        has_real_svc = bool(
            svc and
            not svc.startswith("your_") and
            not svc.startswith("your-") and
            svc != "your_supabase_service_role_key_here"
        )
        return bool(self.supabase_url and (has_real_anon or has_real_svc))


auth_config = AuthConfig()
