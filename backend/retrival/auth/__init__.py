# Auth module for ExamSmith
# Provides JWT-based authentication and role-based authorization

from auth.jwt_handler import create_access_token, verify_token
from auth.password import hash_password, verify_password
from auth.dependencies import get_current_user, require_auth, require_role

__all__ = [
    "create_access_token",
    "verify_token", 
    "hash_password",
    "verify_password",
    "get_current_user",
    "require_auth",
    "require_role"
]
