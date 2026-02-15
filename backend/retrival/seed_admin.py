"""
Seed Script for ExamSmith.
Creates initial admin user and sets up required collections.

Usage:
    python seed_admin.py

Or with custom credentials:
    python seed_admin.py --email admin@examsmith.com --password YourSecurePassword123
"""

import argparse
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


def create_admin_user(client, email: str, password: str, name: str = "System Admin"):
    """Create the initial admin user."""
    db = client[settings.mongodb_users_db]
    users = db["users"]
    
    # Check if admin already exists
    existing = users.find_one({"email": email})
    if existing:
        print(f"⚠ Admin user already exists: {email}")
        return False
    
    # Create admin user
    admin = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": hash_password(password),
        "name": name,
        "role": UserRole.ADMIN.value,
        "status": UserStatus.ACTIVE.value,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "last_login": None
    }
    
    users.insert_one(admin)
    print(f"✓ Admin user created: {email}")
    print(f"  User ID: {admin['user_id']}")
    return True


def setup_indexes(client):
    """Create required indexes."""
    db = client[settings.mongodb_users_db]
    
    # Users collection indexes
    users = db["users"]
    users.create_index("email", unique=True)
    users.create_index("user_id", unique=True)
    users.create_index("role")
    print("✓ Created indexes on 'users' collection")
    
    # Question papers collection indexes
    papers = db["question_papers"]
    papers.create_index("paper_id", unique=True)
    papers.create_index("status")
    papers.create_index("created_by")
    papers.create_index("created_at")
    print("✓ Created indexes on 'question_papers' collection")
    
    # Attempts collection indexes
    attempts = db["attempts"]
    attempts.create_index("attempt_id", unique=True)
    attempts.create_index("student_id")
    attempts.create_index("paper_id")
    attempts.create_index([("student_id", 1), ("paper_id", 1)])
    print("✓ Created indexes on 'attempts' collection")
    
    # Evaluations collection indexes
    evaluations = db["evaluations"]
    evaluations.create_index("evaluation_id", unique=True)
    evaluations.create_index("attempt_id")
    evaluations.create_index("student_id")
    print("✓ Created indexes on 'evaluations' collection")
    
    # Revisions collection indexes
    revisions = db["revisions"]
    revisions.create_index("paper_id")
    revisions.create_index("revised_by")
    print("✓ Created indexes on 'revisions' collection")


def main():
    parser = argparse.ArgumentParser(description="Seed ExamSmith database with admin user")
    parser.add_argument("--email", default="admin@examsmith.com", help="Admin email")
    parser.add_argument("--password", default="AdminPass123!", help="Admin password")
    parser.add_argument("--name", default="System Administrator", help="Admin name")
    parser.add_argument("--skip-indexes", action="store_true", help="Skip index creation")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 50)
    print("ExamSmith Database Seeder")
    print("=" * 50 + "\n")
    
    # Connect to MongoDB
    client = get_db_client()
    
    # Create indexes
    if not args.skip_indexes:
        print("\nSetting up indexes...")
        setup_indexes(client)
    
    # Create admin user
    print("\nCreating admin user...")
    created = create_admin_user(
        client,
        email=args.email,
        password=args.password,
        name=args.name
    )
    
    client.close()
    
    print("\n" + "=" * 50)
    if created:
        print("✓ Seed completed successfully!")
        print(f"\nAdmin Credentials:")
        print(f"  Email: {args.email}")
        print(f"  Password: {args.password}")
        print("\n⚠ IMPORTANT: Change the password after first login!")
    else:
        print("Seed completed (admin already exists)")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
