from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB Atlas connection manager."""
    
    def __init__(self):
        try:
            self.client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            logger.info("✓ MongoDB connected")
        except ConnectionFailure as e:
            logger.error(f"✗ MongoDB connection failed: {str(e)}")
            self.client = None
        except Exception as e:
            logger.error(f"✗ MongoDB init failed: {str(e)}")
            self.client = None
    
    @property
    def textbook_collection(self):
        """Get textbook collection."""
        if not self.client:
            return None
        return self.client[settings.mongodb_db_textbook][settings.mongodb_collection_textbook]
    
    @property
    def questionpapers_collection(self):
        """Get question papers collection."""
        if not self.client:
            return None
        return self.client[settings.mongodb_db_questionpapers][settings.mongodb_collection_questionpapers]
    
    @property
    def chat_sessions_collection(self):
        """Get chat sessions collection."""
        if not self.client:
            return None
        return self.client[settings.mongodb_users_db]["chat_sessions"]
    
    @property
    def chat_messages_collection(self):
        """Get chat messages collection."""
        if not self.client:
            return None
        return self.client[settings.mongodb_users_db]["chat_messages"]
    
    @property
    def chat_quota_collection(self):
        """Get chat quota collection for rate limiting."""
        if not self.client:
            return None
        return self.client[settings.mongodb_users_db]["chat_daily_usage"]
    
    def check_and_increment_quota(self, user_id: str, daily_limit: int = 20) -> tuple[bool, int]:
        """
        Check if user has remaining quota and increment if allowed.
        Returns (allowed: bool, remaining: int)
        """
        if not self.client:
            return False, 0
            
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc_id = f"{user_id}:{today}"
        
        coll = self.chat_quota_collection
        
        # Atomic upsert with increment
        result = coll.find_one_and_update(
            {"_id": doc_id, "count": {"$lt": daily_limit}},
            {
                "$inc": {"count": 1},
                "$setOnInsert": {"user_id": user_id, "date": today},
                "$set": {"updated_at": datetime.now(timezone.utc)}
            },
            upsert=True,
            return_document=True
        )
        
        if result:
            remaining = daily_limit - result.get("count", 0)
            return True, max(0, remaining)
        else:
            # Check current count
            doc = coll.find_one({"_id": doc_id})
            if doc:
                return False, max(0, daily_limit - doc.get("count", daily_limit))
            return False, 0
    
    def get_remaining_quota(self, user_id: str, daily_limit: int = 20) -> int:
        """Get remaining quota without incrementing."""
        if not self.client:
            return 0
            
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        doc_id = f"{user_id}:{today}"
        
        doc = self.chat_quota_collection.find_one({"_id": doc_id})
        if doc:
            return max(0, daily_limit - doc.get("count", 0))
        return daily_limit
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global instance
mongo_client = MongoDBClient()
