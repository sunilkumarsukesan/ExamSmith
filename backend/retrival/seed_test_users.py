"""
Seed Script to create test users for ExamSmith.
Creates admin, instructor, and student test accounts.

Usage:
    python seed_test_users.py
"""

import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pymongo import MongoClient
from config import settings
from auth.password import hash_password
from models_db.user import UserRole, UserStatus


def get_db_client():
    """Get MongoDB client."""
    try:
        client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ Connected to MongoDB")
        return client
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        sys.exit(1)


def create_test_users(client):
    """Create test users with different roles."""
    db = client[settings.mongodb_users_db]
    users = db["users"]
    
    test_users = [
        {
            "email": "admin@examsmith.com",
            "password": "AdminPass123!",
            "name": "Admin User",
            "role": UserRole.ADMIN.value,
        },
        {
            "email": "instructor@test.com",
            "password": "Instructor123!",
            "name": "Test Instructor",
            "role": UserRole.INSTRUCTOR.value,
        },
        {
            "email": "student@examsmith.com",
            "password": "Student123!",
            "name": "Test Student",
            "role": UserRole.STUDENT.value,
        },
    ]
    
    print("\n" + "=" * 60)
    print("Creating Test Users")
    print("=" * 60)
    
    for user_data in test_users:
        email = user_data["email"]
        
        # Check if user already exists
        existing = users.find_one({"email": email})
        if existing:
            print(f"\n⚠ User already exists: {email}")
            print(f"  Skipping creation. To reset password, use reset_password.py")
            continue
        
        # Create user
        user = {
            "user_id": str(uuid.uuid4()),
            "email": email,
            "password_hash": hash_password(user_data["password"]),
            "name": user_data["name"],
            "role": user_data["role"],
            "status": UserStatus.ACTIVE.value,
            "created_at": datetime.utcnow(),
            "updated_at": None,
            "last_login": None
        }
        
        users.insert_one(user)
        print(f"\n✓ Created {user_data['role'].lower()}: {email}")
        print(f"  Name: {user_data['name']}")
        print(f"  Password: {user_data['password']}")
        print(f"  User ID: {user['user_id']}")
    
    print("\n" + "=" * 60)
    print("✓ Test user setup completed!")
    print("=" * 60)
    print("\nTest Credentials:")
    print("-" * 60)
    for user_data in test_users:
        print(f"\n{user_data['role']}:")
        print(f"  Email:    {user_data['email']}")
        print(f"  Password: {user_data['password']}")
    print("\n" + "=" * 60 + "\n")


def main():
    print("\n" + "=" * 60)
    print("ExamSmith Test User Seeder")
    print("=" * 60 + "\n")
    
    # Connect to MongoDB
    client = get_db_client()
    
    # Create test users
    create_test_users(client)
    
    client.close()


if __name__ == "__main__":
    main()
