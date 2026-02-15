"""
FastAPI Dependencies for Authentication and Authorization.
Provides middleware-like functionality for route protection.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Optional
from functools import wraps
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth.jwt_handler import verify_token, TokenPayload

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenPayload:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: Bearer token from Authorization header
        
    Returns:
        TokenPayload with user information
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid token.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


async def require_auth(
    current_user: TokenPayload = Depends(get_current_user)
) -> TokenPayload:
    """
    Dependency that requires authentication.
    Use this for any protected route.
    
    Usage:
        @router.get("/protected")
        async def protected_route(user: TokenPayload = Depends(require_auth)):
            return {"user": user.email}
    """
    return current_user


def require_role(allowed_roles: List[str]):
    """
    Dependency factory for role-based authorization.
    
    Args:
        allowed_roles: List of roles allowed to access the route
        
    Returns:
        Dependency function that checks user role
        
    Usage:
        @router.get("/admin-only")
        async def admin_route(user: TokenPayload = Depends(require_role(["ADMIN"]))):
            return {"user": user.email}
            
        @router.get("/instructor-or-admin")
        async def instructor_route(user: TokenPayload = Depends(require_role(["ADMIN", "INSTRUCTOR"]))):
            return {"user": user.email}
    """
    async def role_checker(
        current_user: TokenPayload = Depends(get_current_user)
    ) -> TokenPayload:
        if current_user.role not in allowed_roles:
            logger.warning(
                f"Access denied for user {current_user.email} with role {current_user.role}. "
                f"Required roles: {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join(allowed_roles)}"
            )
        return current_user
    
    return role_checker


# Convenience role checkers
require_admin = require_role(["ADMIN"])
require_instructor = require_role(["ADMIN", "INSTRUCTOR"])
require_student = require_role(["ADMIN", "INSTRUCTOR", "STUDENT"])
