from .base import RetrieverMode
from mongo.client import mongo_client
from models import Citation
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class PaperGenerationRetriever(RetrieverMode):
    """Retrieves questions across all sections for paper generation."""
    
    async def retrieve(
        self,
        query: str = None,
        part: str = None,
        section: str = None,
        topic: str = None,
        difficulty: str = None,
        top_k: int = 50,
        **kwargs
    ) -> tuple[List[dict], List[Citation]]:
        """
        Retrieve questions matching section/topic for paper generation.
        
        Args:
            query: General query (optional)
            part: Paper part (I, II, III, IV)
            section: Section within part (prose, poetry, grammar, etc.)
            topic: Specific topic filter
            difficulty: Difficulty level (easy, medium, hard)
            top_k: Maximum number of questions to retrieve
        """
        
        collection = mongo_client.questionpapers_collection
        if collection is None:
            logger.warning("Question papers collection unavailable")
            return [], []
        
        # Build filters
        filters = {}
        if part:
            filters["metadata.part"] = part
        if section:
            filters["metadata.section"] = section
        if topic:
            filters["metadata.topic"] = topic
        if difficulty:
            filters["metadata.difficulty"] = difficulty
        
        try:
            # Use simple query with filters
            results = list(
                collection.find(filters)
                .limit(top_k)
            )
            
            logger.debug(f"Paper generation retrieval: {len(results)} questions found")
            
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
            logger.error(f"Paper generation retrieval failed: {str(e)}")
            return [], []
    
    async def retrieve_section_questions(
        self,
        section: str,
        count: int,
        difficulty: str = None,
    ) -> List[dict]:
        """Retrieve questions for a specific section with count requirement."""
        collection = mongo_client.questionpapers_collection
        if collection is None:
            return []
        
        # Map section names to part names in MongoDB
        # All Part II subsections (prose, poetry, grammar, map) come from "Part - II"
        # All Part III subsections come from "Part - III"
        part_map = {
            "part_i": "Part - I",
            "prose": "Part - II",          # All Part II questions
            "poetry": "Part - II",         # All Part II questions
            "grammar": "Part - II",        # All Part II questions
            "map": "Part - II",            # All Part II questions
            "prose_paragraph": "Part - III",   # All Part III questions
            "supplementary": "Part - III",     # All Part III questions
            "writing": "Part - III",           # All Part III questions
            "memory_poem": "Part - III",       # All Part III questions
            "part_iv": "Part - IV",
        }
        
        part_name = part_map.get(section, section)
        filters = {"metadata.part": part_name}
        if difficulty:
            filters["metadata.difficulty"] = difficulty
        
        try:
            results = list(collection.find(filters).limit(count))
            logger.info(f"Retrieved {len(results)} questions for section '{section}' (part: '{part_name}')")
            return results
        except Exception as e:
            logger.error(f"Section retrieval failed: {str(e)}")
            return []
