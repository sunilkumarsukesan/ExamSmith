"""
Admin Routes for ExamSmith.
Handles user management and system administration.
ADMIN role required for all endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import uuid
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models_db.user import (
    User, UserCreate, UserUpdate, UserResponse, 
    UserRole, UserStatus
)
from auth.password import hash_password
from auth.dependencies import require_role, TokenPayload
from mongo.client import mongo_client
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

# Admin-only dependency
require_admin = require_role(["ADMIN"])


# ===== Helper Functions =====

def get_users_collection():
    """Get users collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["users"]


def get_books_collection():
    """Get books collection for admin."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["books"]


# ===== User Management Endpoints =====

@router.post("/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Create a new user (any role).
    
    **Admin only** - Can create ADMIN, INSTRUCTOR, or STUDENT accounts.
    """
    try:
        collection = get_users_collection()
        
        # Check if email already exists
        existing = collection.find_one({"email": request.email})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # Create user with specified role
        user_id = str(uuid.uuid4())
        user = User(
            user_id=user_id,
            email=request.email,
            password_hash=hash_password(request.password),
            name=request.name,
            role=request.role,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        collection.insert_one(user.model_dump())
        
        logger.info(f"Admin {current_user.email} created user: {request.email} with role {request.role}")
        
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
        logger.error(f"Create user failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user")


@router.get("/list-users", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    status_filter: Optional[UserStatus] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: TokenPayload = Depends(require_admin)
):
    """
    List all users with optional filters.
    
    **Admin only**
    """
    try:
        collection = get_users_collection()
        
        # Build query
        query = {}
        if role:
            query["role"] = role.value
        if status_filter:
            query["status"] = status_filter.value
        
        # Fetch users
        cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        users = []
        for doc in cursor:
            users.append(UserResponse(
                user_id=doc["user_id"],
                email=doc["email"],
                name=doc["name"],
                role=doc["role"],
                status=doc["status"],
                created_at=doc["created_at"],
                last_login=doc.get("last_login")
            ))
        
        return users
        
    except Exception as e:
        logger.error(f"List users failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list users")


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Get a specific user by ID.
    
    **Admin only**
    """
    try:
        collection = get_users_collection()
        user_doc = collection.find_one({"user_id": user_id})
        
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
        logger.error(f"Get user failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user")


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Update a user's details.
    
    **Admin only** - Can update name, role, or status.
    """
    try:
        collection = get_users_collection()
        
        # Find user
        user_doc = collection.find_one({"user_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-demotion
        if user_id == current_user.user_id and request.role and request.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote yourself from admin role"
            )
        
        # Build update
        update_data = {"updated_at": datetime.utcnow()}
        if request.name:
            update_data["name"] = request.name
        if request.role:
            update_data["role"] = request.role.value
        if request.status:
            update_data["status"] = request.status.value
        
        # Update
        collection.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        
        # Fetch updated user
        updated = collection.find_one({"user_id": user_id})
        
        logger.info(f"Admin {current_user.email} updated user: {user_id}")
        
        return UserResponse(
            user_id=updated["user_id"],
            email=updated["email"],
            name=updated["name"],
            role=updated["role"],
            status=updated["status"],
            created_at=updated["created_at"],
            last_login=updated.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update user failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")


@router.put("/disable-user/{user_id}", response_model=UserResponse)
async def disable_user(
    user_id: str,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Disable a user account.
    
    **Admin only** - Disabled users cannot log in.
    """
    try:
        collection = get_users_collection()
        
        # Find user
        user_doc = collection.find_one({"user_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-disable
        if user_id == current_user.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot disable your own account"
            )
        
        # Disable user
        collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "status": UserStatus.DISABLED.value,
                "updated_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Admin {current_user.email} disabled user: {user_id}")
        
        # Fetch updated user
        updated = collection.find_one({"user_id": user_id})
        
        return UserResponse(
            user_id=updated["user_id"],
            email=updated["email"],
            name=updated["name"],
            role=updated["role"],
            status=updated["status"],
            created_at=updated["created_at"],
            last_login=updated.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disable user failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to disable user")


@router.put("/enable-user/{user_id}", response_model=UserResponse)
async def enable_user(
    user_id: str,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Re-enable a disabled user account.
    
    **Admin only**
    """
    try:
        collection = get_users_collection()
        
        # Find user
        user_doc = collection.find_one({"user_id": user_id})
        if not user_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Enable user
        collection.update_one(
            {"user_id": user_id},
            {"$set": {
                "status": UserStatus.ACTIVE.value,
                "updated_at": datetime.utcnow()
            }}
        )
        
        logger.info(f"Admin {current_user.email} enabled user: {user_id}")
        
        # Fetch updated user
        updated = collection.find_one({"user_id": user_id})
        
        return UserResponse(
            user_id=updated["user_id"],
            email=updated["email"],
            name=updated["name"],
            role=updated["role"],
            status=updated["status"],
            created_at=updated["created_at"],
            last_login=updated.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enable user failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to enable user")


# ===== Book/Ingestion Management =====

@router.get("/books")
async def list_books(
    current_user: TokenPayload = Depends(require_admin)
):
    """
    List all ingested books.
    
    **Admin only**
    """
    try:
        collection = get_books_collection()
        cursor = collection.find({}).sort("created_at", -1)
        
        books = []
        for doc in cursor:
            books.append({
                "book_id": doc.get("book_id", str(doc.get("_id"))),
                "title": doc.get("title", "Unknown"),
                "source_file": doc.get("source_file"),
                "status": doc.get("status", "injected"),
                "injected_at": doc.get("injected_at") or doc.get("created_at"),
                "chunk_count": doc.get("chunk_count", 0)
            })
        
        return {"books": books, "total": len(books)}
        
    except Exception as e:
        logger.error(f"List books failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list books")


# TODO: POST /admin/upload-book - File upload for new book
# TODO: POST /admin/run-injection - Trigger injection pipeline
