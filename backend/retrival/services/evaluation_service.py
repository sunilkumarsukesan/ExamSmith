"""
Evaluation Service for ExamSmith.
Handles semantic evaluation of student answers using embeddings.
"""

import logging
import httpx
from typing import List, Optional, Dict, Any
import numpy as np
from config import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluating student answers semantically."""
    
    def __init__(self):
        self.mistral_api_key = settings.mistral_api_key
        self.embed_model = getattr(settings, 'mistral_embed_model', 'mistral-embed')
        self.embed_url = "https://api.mistral.ai/v1/embeddings"
    
    async def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding for a text using Mistral API."""
        if not self.mistral_api_key:
            logger.warning("Mistral API key not configured")
            return None
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.embed_url,
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.embed_model,
                        "input": [text[:8000]]  # Truncate to avoid token limits
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["data"][0]["embedding"]
                else:
                    logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Embedding failed: {str(e)}")
            return None
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        a = np.array(vec1)
        b = np.array(vec2)
        
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return float(dot_product / (norm_a * norm_b))
    
    async def evaluate_descriptive_answer(
        self,
        student_answer: str,
        answer_key: str,
        textbook_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a descriptive answer semantically.
        
        Returns:
        - answer_key_similarity: Similarity to the answer key (0-1)
        - textbook_similarity: Similarity to textbook content (0-1)
        - final_score: Weighted average (0-1)
        - feedback: Generated feedback
        """
        result = {
            "answer_key_similarity": 0.0,
            "textbook_similarity": 0.0,
            "final_score": 0.0,
            "feedback": "",
            "used_semantic": False
        }
        
        # Handle empty answers
        if not student_answer or not student_answer.strip():
            result["feedback"] = "No answer provided."
            return result
        
        # Try semantic evaluation with embeddings
        student_embedding = await self.get_embedding(student_answer)
        answer_key_embedding = await self.get_embedding(answer_key) if answer_key else None
        textbook_embedding = await self.get_embedding(textbook_context) if textbook_context else None
        
        if student_embedding:
            result["used_semantic"] = True
            
            # Calculate similarity with answer key
            if answer_key_embedding:
                result["answer_key_similarity"] = max(0, self.cosine_similarity(
                    student_embedding, answer_key_embedding
                ))
            
            # Calculate similarity with textbook content
            if textbook_embedding:
                result["textbook_similarity"] = max(0, self.cosine_similarity(
                    student_embedding, textbook_embedding
                ))
            
            # Calculate final score: 50% answer key + 50% textbook
            if answer_key_embedding and textbook_embedding:
                result["final_score"] = (
                    0.5 * result["answer_key_similarity"] + 
                    0.5 * result["textbook_similarity"]
                )
            elif answer_key_embedding:
                result["final_score"] = result["answer_key_similarity"]
            elif textbook_embedding:
                result["final_score"] = result["textbook_similarity"]
            else:
                # Fallback to length-based scoring
                result["final_score"] = min(1.0, len(student_answer) / 200)
        else:
            # Fallback to keyword-based evaluation
            result = self._keyword_evaluation(student_answer, answer_key)
        
        # Generate feedback based on score
        result["feedback"] = self._generate_feedback(
            result["final_score"],
            result.get("used_semantic", False)
        )
        
        return result
    
    def _keyword_evaluation(
        self, 
        student_answer: str, 
        answer_key: str
    ) -> Dict[str, Any]:
        """Fallback keyword-based evaluation when embeddings unavailable."""
        student_text = student_answer.strip().lower()
        expected_text = str(answer_key).lower() if answer_key else ""
        
        if not student_text:
            return {
                "answer_key_similarity": 0.0,
                "textbook_similarity": 0.0,
                "final_score": 0.0,
                "feedback": "No answer provided.",
                "used_semantic": False
            }
        
        if len(student_text) < 10:
            return {
                "answer_key_similarity": 0.1,
                "textbook_similarity": 0.1,
                "final_score": 0.1,
                "feedback": "Answer too brief. Please provide more detail.",
                "used_semantic": False
            }
        
        # Keyword overlap scoring
        expected_words = set(expected_text.split())
        student_words = set(student_text.split())
        
        if len(expected_words) > 0:
            common = expected_words.intersection(student_words)
            keyword_score = len(common) / len(expected_words)
        else:
            keyword_score = 0.5  # No answer key
        
        # Length component
        length_score = min(1.0, len(student_text) / max(len(expected_text), 50))
        
        # Combined score
        final_score = 0.6 * keyword_score + 0.4 * length_score
        final_score = min(1.0, max(0.1, final_score))
        
        return {
            "answer_key_similarity": keyword_score,
            "textbook_similarity": keyword_score,
            "final_score": final_score,
            "feedback": "",
            "used_semantic": False
        }
    
    def _generate_feedback(self, score: float, used_semantic: bool) -> str:
        """Generate feedback based on score."""
        method = "semantic analysis" if used_semantic else "keyword matching"
        
        if score >= 0.85:
            return f"Excellent answer! Comprehensive coverage of key concepts. (Evaluated using {method})"
        elif score >= 0.70:
            return f"Good answer with solid understanding. Consider adding more specific details. (Evaluated using {method})"
        elif score >= 0.50:
            return f"Partial answer. Some key concepts covered but needs more depth. (Evaluated using {method})"
        elif score >= 0.30:
            return f"Basic answer. Missing several important concepts. Review the topic. (Evaluated using {method})"
        else:
            return f"Answer needs significant improvement. Please review the material thoroughly. (Evaluated using {method})"


# Singleton instance
evaluation_service = EvaluationService()
