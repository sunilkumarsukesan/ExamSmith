from .base import RetrieverMode
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation
from embeddings import embed_query
import logging

logger = logging.getLogger(__name__)

class AnswerEvaluationRetriever(RetrieverMode):
    """Retrieves official answers and supporting evidence for answer evaluation."""
    
    async def retrieve(
        self,
        query: str = None,
        question_id: str = None,
        question_text: str = None,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5,
        top_k: int = 5,
        query_embedding: list[float] = None,
        **kwargs
    ) -> tuple[list[dict], list[Citation]]:
        """
        Retrieve official answers and supporting evidence.
        
        Args:
            query: Search query for evidence
            question_id: Specific question number to retrieve answer for
            question_text: Question text for semantic search
            vector_weight: Weight for vector search
            bm25_weight: Weight for BM25 search
            top_k: Number of supporting evidence chunks
            query_embedding: Embedding vector
        """
        
        qp_collection = mongo_client.questionpapers_collection
        textbook_collection = mongo_client.textbook_collection
        
        if qp_collection is None:
            logger.warning("Question papers collection unavailable")
            return [], []
        
        result_data = []
        citations = []
        
        try:
            # Step 1: Retrieve official answer
            if question_id:
                official_q = qp_collection.find_one({"question.number": question_id})
            else:
                # Fallback: find question by semantic similarity
                pipeline = [
                    {"$search": {"text": {"query": question_text or query, "path": "content"}}},
                    {"$limit": 1}
                ]
                official_q = next(qp_collection.aggregate(pipeline), None)
            
            if official_q:
                answer_data = official_q.get("question", {}).get("answer", {})
                result_data.append({
                    "type": "official_answer",
                    "content": answer_data.get("text", ""),
                    "option": answer_data.get("option", "")
                })
                
                citations.append(
                    Citation(
                        chunk_id=str(official_q.get("_id")),
                        source="question_paper",
                        question_number=str(official_q.get("question", {}).get("number", "Unknown")),
                        year=official_q.get("metadata", {}).get("year")
                    )
                )
            
            # Step 2: Retrieve supporting textbook evidence
            if textbook_collection and (query or question_text):
                # Generate REAL embedding using Mistral API
                if not query_embedding:
                    try:
                        query_embedding = await embed_query(query or question_text)
                        logger.debug("Generated Mistral embedding for evidence retrieval")
                    except Exception as e:
                        logger.warning(f"Embedding failed, using BM25-only: {str(e)}")
                        query_embedding = [0.0] * 1024
                
                config = HybridSearchConfig(
                    vector_weight=vector_weight,
                    bm25_weight=bm25_weight,
                    top_k=top_k
                )
                
                evidence = await HybridSearch.search(
                    textbook_collection,
                    query or question_text,
                    query_embedding,
                    config,
                    filters={"metadata.lang": "en"}
                )
                
                for doc in evidence:
                    result_data.append({
                        "type": "supporting_evidence",
                        "content": doc.get("content", "")
                    })
                    citations.append(
                        Citation(
                            chunk_id=str(doc.get("_id")),
                            source="textbook",
                            lesson_name=doc.get("metadata", {}).get("lesson_name"),
                            page=doc.get("metadata", {}).get("page")
                        )
                    )
            
            # Flatten context blocks
            context_blocks = [item["content"] for item in result_data]
            
            return context_blocks, citations
        
        except Exception as e:
            logger.error(f"Answer evaluation retrieval failed: {str(e)}")
            return [], []
