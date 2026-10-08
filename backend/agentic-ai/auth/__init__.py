"""
auth package
Modular, scalable authentication layer for HireLens supporting Supabase Auth,
JWT verification, role-based access control (RBAC), and pluggable providers.
"""

from .models import UserContext, UserRole, UserProfile
from .dependencies import get_current_user, get_optional_user, require_role
from .config import auth_config
from .provider import get_auth_provider

__all__ = [
    "UserContext",
    "UserRole",
    "UserProfile",
    "get_current_user",
    "get_optional_user",
    "require_role",
    "auth_config",
    "get_auth_provider",
]
