from .base import RetrieverMode
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation
from embeddings import embed_query
import logging

logger = logging.getLogger(__name__)

class ConceptExplanationRetriever(RetrieverMode):
    """Hybrid search on textbook collection for concept explanations."""
    
    async def retrieve(
        self,
        query: str,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5,
        top_k: int = 5,
        filters: dict = None,
        query_embedding: list[float] = None,
        **kwargs
    ) -> tuple[list[dict], list[Citation]]:
        """
        Retrieve concept explanations from textbook using hybrid search.
        
        Args:
            query: Text query
            vector_weight: Weight for vector search (0-1)
            bm25_weight: Weight for BM25 search (0-1)
            top_k: Number of results
            filters: MongoDB filters (e.g., {"metadata.lang": "en"})
            query_embedding: Embedding vector (if not provided, uses query text)
        """
        
        collection = mongo_client.textbook_collection
        if collection is None:
            logger.warning("Textbook collection unavailable")
            return [], []
        
        # Default filters
        if not filters:
            filters = {"metadata.lang": "en"}
        
        # Configure hybrid search
        config = HybridSearchConfig(
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            top_k=top_k
        )
        
        # Generate REAL embedding using Mistral API
        # NO placeholder embeddings allowed per instruction file
        if not query_embedding:
            try:
                query_embedding = await embed_query(query)
                logger.debug(f"Generated Mistral embedding for query: {query[:50]}...")
            except Exception as e:
                logger.error(f"Embedding generation failed: {str(e)}")
                # Fallback to BM25-only search (vector weight = 0)
                logger.warning("Falling back to BM25-only search (no embeddings)")
                config = HybridSearchConfig(
                    vector_weight=0.0,
                    bm25_weight=1.0,
                    top_k=top_k
                )
                query_embedding = [0.0] * 1024  # Will be ignored with weight=0
        
        # Perform hybrid search
        results = await HybridSearch.search(
            collection,
            query,
            query_embedding,
            config,
            filters
        )
        
        # Convert to context blocks and citations
        context_blocks = [doc.get("content", "") for doc in results]
        citations = [
            Citation(
                chunk_id=str(doc.get("_id")),
                source="textbook",
                page=doc.get("metadata", {}).get("page"),
                lesson_name=doc.get("metadata", {}).get("lesson_name")
            )
            for doc in results
        ]
        
        return context_blocks, citations
