"""
Authentication Routes for ExamSmith.
Handles login, registration, and token management.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from datetime import datetime
import uuid
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models_db.user import (
    User, UserCreate, LoginRequest, LoginResponse, 
    UserResponse, TokenResponse, UserRole, UserStatus
)
from auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.password import hash_password, verify_password
from auth.dependencies import get_current_user, TokenPayload
from mongo.client import mongo_client
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ===== Helper Functions =====

def get_users_collection():
    """Get or create users collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    
    # Use a dedicated database for users
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["users"]


async def get_user_by_email(email: str) -> Optional[dict]:
    """Find user by email."""
    collection = get_users_collection()
    return collection.find_one({"email": email})


async def get_user_by_id(user_id: str) -> Optional[dict]:
    """Find user by ID."""
    collection = get_users_collection()
    return collection.find_one({"user_id": user_id})


# ===== Auth Endpoints =====

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return JWT token.
    
    - **email**: User's email address
    - **password**: User's password
    """
    try:
        # Find user
        user_doc = await get_user_by_email(request.email)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if user is disabled
        if user_doc.get("status") == UserStatus.DISABLED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled. Contact administrator."
            )
        
        # Verify password
        if not verify_password(request.password, user_doc["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Update last login
        collection = get_users_collection()
        collection.update_one(
            {"user_id": user_doc["user_id"]},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Create token
        access_token = create_access_token(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            role=user_doc["role"]
        )
        
        logger.info(f"User logged in: {request.email}")
        
        return LoginResponse(
            user=UserResponse(
                user_id=user_doc["user_id"],
                email=user_doc["email"],
                name=user_doc["name"],
                role=user_doc["role"],
                status=user_doc["status"],
                created_at=user_doc["created_at"],
                last_login=datetime.utcnow()
            ),
            token=TokenResponse(
                access_token=access_token,
                token_type="bearer",
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(request: UserCreate):
    """
    Register a new student account.
    
    Note: Only STUDENT role can self-register. 
    ADMIN and INSTRUCTOR accounts must be created by an admin.
    """
    try:
        # Check if email already exists
        existing = await get_user_by_email(request.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Force STUDENT role for self-registration
        if request.role != UserRole.STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only student accounts can self-register. Contact admin for other roles."
            )
        
        # Create user
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            email=request.email,
            password_hash=hash_password(request.password),
            name=request.name,
            role=UserRole.STUDENT,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        collection = get_users_collection()
        collection.insert_one(user.model_dump())
        
        logger.info(f"New user registered: {request.email}")
        
        return UserResponse(
            user_id=user.user_id,
            email=user.email,
            name=user.name,
            role=user.role,
            status=user.status,
            created_at=user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: TokenPayload = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    """
    try:
        user_doc = await get_user_by_id(current_user.user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            name=user_doc["name"],
            role=user_doc["role"],
            status=user_doc["status"],
            created_at=user_doc["created_at"],
            last_login=user_doc.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get profile")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: TokenPayload = Depends(get_current_user)):
    """
    Refresh the access token for authenticated user.
    """
    try:
        # Verify user still exists and is active
        user_doc = await get_user_by_id(current_user.user_id)
        
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if user_doc.get("status") == UserStatus.DISABLED.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Create new token
        access_token = create_access_token(
            user_id=user_doc["user_id"],
            email=user_doc["email"],
            role=user_doc["role"]
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Token refresh failed")
