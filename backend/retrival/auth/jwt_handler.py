"""
JWT Token Handler for ExamSmith Authentication.
Handles token creation and verification.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from pydantic import BaseModel
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import settings

logger = logging.getLogger(__name__)

# JWT Configuration - loaded from settings
SECRET_KEY = getattr(settings, 'jwt_secret_key', 'examsmith-secret-key-change-in-production')
ALGORITHM = getattr(settings, 'jwt_algorithm', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'jwt_expire_minutes', 1440)  # 24 hours default


class TokenPayload(BaseModel):
    """JWT Token payload schema."""
    user_id: str
    email: str
    role: str
    exp: Optional[datetime] = None
    iat: Optional[datetime] = None


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User's unique identifier
        email: User's email
        role: User's role (ADMIN, INSTRUCTOR, STUDENT)
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": now
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    logger.info(f"Created access token for user: {email}")
    return token


def verify_token(token: str) -> Optional[TokenPayload]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        TokenPayload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check expiration
        exp = payload.get("exp")
        if exp:
            exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
            if datetime.now(timezone.utc) > exp_datetime:
                logger.warning("Token has expired")
                return None
        
        return TokenPayload(
            user_id=payload.get("user_id"),
            email=payload.get("email"),
            role=payload.get("role"),
            exp=datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc) if payload.get("exp") else None,
            iat=datetime.fromtimestamp(payload.get("iat"), tz=timezone.utc) if payload.get("iat") else None
        )
        
    except JWTError as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {str(e)}")
        return None


def decode_token_without_verification(token: str) -> Optional[dict]:
    """
    Decode token without verification (for debugging only).
    DO NOT use in production for authentication.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
    except Exception:
        return None
