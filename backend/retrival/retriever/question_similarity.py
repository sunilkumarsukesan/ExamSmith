from .base import RetrieverMode
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation
import logging

logger = logging.getLogger(__name__)

class QuestionSimilarityRetriever(RetrieverMode):
    """Vector search on question papers for similar questions."""
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        difficulty: str = None,
        query_embedding: list[float] = None,
        **kwargs
    ) -> tuple[list[dict], list[Citation]]:
        """
        Retrieve similar exam questions from question paper collection.
        
        Args:
            query: Question text to match
            top_k: Number of similar questions to return
            difficulty: Filter by difficulty (easy, medium, hard)
            query_embedding: Embedding vector for semantic search
        """
        
        collection = mongo_client.questionpapers_collection
        if collection is None:
            logger.warning("Question papers collection unavailable")
            return [], []
        
        # Build filters
        filters = {}
        if difficulty:
            filters["metadata.difficulty"] = difficulty
        
        # If no embedding provided, try vector search with placeholder
        if not query_embedding:
            query_embedding = [0.0] * 1024  # Placeholder
        
        try:
            # Use vector search only for question similarity
            pipeline = [
                {
                    "$search": {
                        "cosmosSearch": True,
                        "vector": query_embedding,
                        "k": top_k,
                    }
                },
                {"$addFields": {"similarity_score": {"$meta": "searchScore"}}},
            ]
            
            if filters:
                pipeline.insert(1, {"$match": filters})
            
            results = list(collection.aggregate(pipeline))
            logger.debug(f"Question similarity search returned {len(results)} results")
            
            # Convert to context blocks and citations
            context_blocks = []
            citations = []
            
            for doc in results:
                question_num = doc.get("question", {}).get("number", "Unknown")
                question_text = doc.get("content", "")
                context_blocks.append(question_text)
                citations.append(
                    Citation(
                        chunk_id=str(doc.get("_id")),
                        source="question_paper",
                        year=doc.get("metadata", {}).get("year"),
                        question_number=str(question_num)
                    )
                )
            
            return context_blocks, citations
        
        except Exception as e:
            logger.error(f"Question similarity search failed: {str(e)}")
            return [], []
