"""
Reset passwords for all test users in ExamSmith.

Usage:
    python reset_all_passwords.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from pymongo import MongoClient
from config import settings
from auth.password import hash_password


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


def reset_all_passwords(client):
    """Reset passwords for all test users."""
    db = client[settings.mongodb_users_db]
    users = db["users"]
    
    test_credentials = [
        {"email": "admin@examsmith.com", "password": "AdminPass123!", "role": "ADMIN"},
        {"email": "instructor@test.com", "password": "Instructor123!", "role": "INSTRUCTOR"},
        {"email": "student@examsmith.com", "password": "Student123!", "role": "STUDENT"},
    ]
    
    print("\n" + "=" * 70)
    print("Resetting Test User Passwords")
    print("=" * 70)
    
    for cred in test_credentials:
        email = cred["email"]
        password = cred["password"]
        
        # Find user
        user = users.find_one({"email": email})
        if not user:
            print(f"\n✗ User not found: {email}")
            continue
        
        # Reset password
        new_hash = hash_password(password)
        result = users.update_one(
            {"email": email},
            {
                "$set": {
                    "password_hash": new_hash,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"\n✓ Password reset for {cred['role']}: {email}")
            print(f"  New Password: {password}")
        else:
            print(f"\n✗ Failed to update password for: {email}")
    
    print("\n" + "=" * 70)
    print("✓ Password reset completed!")
    print("=" * 70)
    print("\nTest Credentials:")
    print("-" * 70)
    for cred in test_credentials:
        print(f"\n{cred['role']}:")
        print(f"  Email:    {cred['email']}")
        print(f"  Password: {cred['password']}")
    print("\n" + "=" * 70 + "\n")


def main():
    print("\n" + "=" * 70)
    print("ExamSmith Password Reset Utility")
    print("=" * 70 + "\n")
    
    # Connect to MongoDB
    client = get_db_client()
    
    # Reset passwords
    reset_all_passwords(client)
    
    client.close()


if __name__ == "__main__":
    main()
