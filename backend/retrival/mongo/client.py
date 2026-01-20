from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings
import logging

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
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

# Global instance
mongo_client = MongoDBClient()
