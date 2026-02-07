from typing import Optional
import logging
from config import settings

logger = logging.getLogger(__name__)

class HybridSearchConfig:
    """Configuration for hybrid search."""
    def __init__(
        self,
        vector_weight: float = settings.hybrid_default_vector_weight,
        bm25_weight: float = settings.hybrid_default_bm25_weight,
        rrf_k: int = settings.hybrid_rrf_k,
        top_k: int = settings.hybrid_default_top_k,
    ):
        # Normalize weights
        total = vector_weight + bm25_weight
        self.vector_weight = vector_weight / total if total > 0 else 0.5
        self.bm25_weight = bm25_weight / total if total > 0 else 0.5
        self.rrf_k = rrf_k
        self.top_k = top_k

class HybridSearch:
    """Hybrid search: BM25 + Vector with RRF fusion."""
    
    @staticmethod
    async def search(
        collection,
        query: str,
        query_embedding: list[float],
        config: HybridSearchConfig,
        filters: dict = None,
    ) -> list[dict]:
        """
        Perform hybrid search with Reciprocal Rank Fusion (RRF).
        
        Args:
            collection: MongoDB collection
            query: Text query
            query_embedding: 1024-dim vector embedding
            config: HybridSearchConfig with weights
            filters: MongoDB filter dict
        
        Returns:
            list[dict]: Top-K results ranked by RRF score
        """
        
        if collection is None:
            logger.warning("Collection unavailable - returning empty results")
            return []
        
        try:
            # Step 1: BM25 Search
            bm25_results = await HybridSearch._bm25_search(
                collection, query, filters, top_k=config.top_k
            )
            
            # Step 2: Vector Search
            vector_results = await HybridSearch._vector_search(
                collection, query_embedding, filters, top_k=config.top_k
            )
            
            # Step 3: RRF Fusion
            fused_results = HybridSearch._rrf_fusion(
                bm25_results,
                vector_results,
                config,
            )
            
            return fused_results[:config.top_k]
        
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []
    
    @staticmethod
    async def _bm25_search(
        collection,
        query: str,
        filters: dict = None,
        top_k: int = 5,
    ) -> list[dict]:
        """BM25 search using MongoDB Atlas Search."""
        try:
            # Use the actual index name from MongoDB Atlas
            bm25_index_name = getattr(settings, 'bm25_index_name', 'bm25_english')
            
            pipeline = [
                {
                    "$search": {
                        "index": bm25_index_name,
                        "text": {
                            "query": query,
                            "path": "content",
                        }
                    }
                },
                {
                    "$addFields": {"bm25_score": {"$meta": "searchScore"}}
                },
            ]
            
            if filters:
                pipeline.insert(1, {"$match": filters})
            
            pipeline.append({"$limit": top_k})
            
            results = list(collection.aggregate(pipeline))
            logger.debug(f"BM25 search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"BM25 search error: {str(e)}")
            return []
    
    @staticmethod
    async def _vector_search(
        collection,
        query_embedding: list[float],
        filters: dict = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Vector search using MongoDB Atlas Vector Search."""
        try:
            # Prefer the native $vectorSearch stage (MongoDB 7.0+/Atlas).
            # If the cluster doesn't support it, fall back to Atlas Search knnBeta.
            vector_index_name = getattr(settings, 'vector_index_name', 'vector_index_english')
            vector_path = "embedding"     # per ingestion schema
            num_candidates = max(50, top_k * 10)

            try:
                vector_stage: dict = {
                    "$vectorSearch": {
                        "index": vector_index_name,
                        "path": vector_path,
                        "queryVector": query_embedding,
                        "numCandidates": num_candidates,
                        "limit": top_k,
                    }
                }
                if filters:
                    # $vectorSearch supports server-side filtering.
                    vector_stage["$vectorSearch"]["filter"] = filters

                pipeline = [
                    vector_stage,
                    {"$addFields": {"vector_score": {"$meta": "vectorSearchScore"}}},
                ]
                results = list(collection.aggregate(pipeline))
                logger.debug(f"Vector search returned {len(results)} results")
                return results
            except Exception as inner:
                # Fall back to $search + knnBeta (older Atlas Search vector syntax)
                logger.debug(f"$vectorSearch unavailable, falling back to knnBeta: {inner}")

            search_body: dict = {
                "index": vector_index_name,
                "knnBeta": {
                    "vector": query_embedding,
                    "path": vector_path,
                    "k": top_k,
                },
            }
            # Apply filters after $search if provided (safe across Atlas versions)
            pipeline = [
                {"$search": search_body},
                {"$addFields": {"vector_score": {"$meta": "searchScore"}}},
            ]
            if filters:
                pipeline.append({"$match": filters})
            pipeline.append({"$limit": top_k})

            results = list(collection.aggregate(pipeline))
            logger.debug(f"Vector search returned {len(results)} results")
            return results
        
        except Exception as e:
            logger.error(f"Vector search error: {str(e)}")
            return []
    
    @staticmethod
    def _rrf_fusion(
        bm25_results: list[dict],
        vector_results: list[dict],
        config: HybridSearchConfig,
    ) -> list[dict]:
        """
        Reciprocal Rank Fusion (RRF) to combine BM25 and vector scores.
        
        Formula: RRF(d) = sum of (1 / (k + rank(d)))
        """
        
        # Create rank dictionaries
        bm25_ranks = {str(doc.get("_id")): i for i, doc in enumerate(bm25_results)}
        vector_ranks = {str(doc.get("_id")): i for i, doc in enumerate(vector_results)}
        
        # Compute RRF scores
        all_doc_ids = set(bm25_ranks.keys()) | set(vector_ranks.keys())
        rrf_scores = {}
        
        for doc_id in all_doc_ids:
            bm25_rank = bm25_ranks.get(doc_id, len(bm25_results) + 1)
            vector_rank = vector_ranks.get(doc_id, len(vector_results) + 1)
            
            rrf_score = (
                config.bm25_weight * (1 / (config.rrf_k + bm25_rank)) +
                config.vector_weight * (1 / (config.rrf_k + vector_rank))
            )
            rrf_scores[doc_id] = rrf_score
        
        # Create result map
        result_map = {}
        for doc in bm25_results + vector_results:
            doc_id = str(doc.get("_id"))
            if doc_id not in result_map:
                result_map[doc_id] = doc
        
        # Sort by RRF score and return
        sorted_results = sorted(
            rrf_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        fused = [result_map[doc_id] for doc_id, _ in sorted_results]
        logger.debug(f"RRF fusion: combined {len(bm25_results)} BM25 + {len(vector_results)} vector results -> {len(fused)} fused")
        
        return fused
