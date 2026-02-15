from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
import logging
from typing import List, Dict, Any
from src.config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB connection and operations handler"""
    
    def __init__(self):
        self.uri = MONGODB_URI
        self.db_name = MONGODB_DB_NAME
        self.collection_name = MONGODB_COLLECTION_NAME
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.uri)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info("MongoDB connected successfully")
            self._create_indexes()
        except PyMongoError as e:
            logger.error(f"MongoDB connection failed: {str(e)}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better query performance (SUGGESTION)"""
        try:
            # Index on content_hash for deduplication
            self.collection.create_index("content_hash", unique=False)
            # Index on created_at for filtering
            self.collection.create_index("created_at")
            logger.info("MongoDB indexes created")
        except PyMongoError as e:
            logger.error(f"Failed to create indexes: {str(e)}")
    
    def upsert_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Upsert documents using content_hash as unique key.
        
        Args:
            documents: List of documents to upsert
            
        Returns:
            Dict with upserted and matched counts
        """
        if not documents:
            return {"upserted": 0, "matched": 0}
        
        try:
            total_docs = len(documents)
            logger.info(f"💾 MONGODB INJECTION START - Total documents to inject: {total_docs}")
            
            operations = [
                UpdateOne(
                    {"content_hash": doc["content_hash"]},
                    {"$set": doc},
                    upsert=True
                )
                for doc in documents
            ]
            
            result = self.collection.bulk_write(operations)
            upserted_count = len(result.upserted_ids) if hasattr(result, 'upserted_ids') else 0
            matched_count = result.modified_count
            
            logger.info(f"✅ MONGODB INJECTION SUCCESS")
            logger.info(f"   📤 New Documents (Upserted): {upserted_count}")
            logger.info(f"   🔄 Updated Documents: {matched_count}")
            logger.info(f"   📊 Total Injected: {upserted_count + matched_count}/{total_docs}")
            
            return {
                "upserted": upserted_count,
                "matched": matched_count
            }
        except PyMongoError as e:
            logger.error(f"❌ MONGODB INJECTION FAILED - Error: {str(e)}")
            raise
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB disconnected")
