import hashlib
from typing import List, Dict, Any

class Deduplicator:
    """Handles content deduplication using SHA256 hashing"""
    
    @staticmethod
    def compute_hash(content: str) -> str:
        """
        Compute SHA256 hash of content for deduplication.
        
        Args:
            content: String content to hash
            
        Returns:
            SHA256 hash as hex string
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def add_hash_to_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Add content_hash field to documents.
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            Documents with content_hash field added
        """
        for doc in documents:
            doc['content_hash'] = Deduplicator.compute_hash(doc['content'])
        return documents
