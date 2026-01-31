"""
Question Reviser - Human-in-the-Loop revision system
Allows teachers to provide feedback and regenerate questions using RAG
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import json
import re

from mongo.client import mongo_client
from llm.factory import get_llm
from config import settings
from embeddings import embed_query
from .image_search import get_new_picture_for_revision

logger = logging.getLogger(__name__)


class QuestionReviser:
    """Handles question revision with teacher feedback using RAG"""
    
    def __init__(self):
        self.revision_history: Dict[str, List[Dict]] = {}  # paper_id -> list of revisions
    
    async def revise_question(
        self,
        original_question: Dict[str, Any],
        teacher_feedback: str,
        paper_id: str
    ) -> Dict[str, Any]:
        """
        Revise a question based on teacher feedback using RAG
        
        Args:
            original_question: The original question object
            teacher_feedback: Teacher's feedback/instructions
            paper_id: ID of the paper containing this question
            
        Returns:
            Revised question object with revision metadata
        """
        logger.info(f"Revising question {original_question.get('question_number')} with feedback: {teacher_feedback}")
        print(f"[DEBUG] Revising question {original_question.get('question_number')} with feedback: {teacher_feedback}")
        print(f"[DEBUG] Original question keys: {original_question.keys()}")
        print(f"[DEBUG] lesson_type: {original_question.get('lesson_type')}")
        print(f"[DEBUG] image_url: {original_question.get('image_url')}")
        print(f"[DEBUG] image_topic: {original_question.get('image_topic')}")
        print(f"[DEBUG] question_number: {original_question.get('question_number')} (type: {type(original_question.get('question_number'))})")
        
        # Check if this is a picture-based question (Q42 or has image_url)
        # Handle both int and string question_number
        q_num = original_question.get('question_number')
        is_q42 = q_num == 42 or q_num == "42" or str(q_num) == "42"
        
        is_picture_question = (
            original_question.get('lesson_type') == 'picture_composition' or 
            original_question.get('image_url') is not None or
            original_question.get('image_topic') is not None or
            is_q42
        )
        
        print(f"[DEBUG] is_q42: {is_q42}, is_picture_question: {is_picture_question}")
        logger.info(f"Is picture question: {is_picture_question}")
        
        if is_picture_question:
            print(f"[DEBUG] TAKING PICTURE PATH!")
            logger.info("Detected picture-based question - using image revision handler")
            revised_question = await self._revise_picture_question(original_question, teacher_feedback)
            print(f"[DEBUG] Revised picture result: {revised_question}")
            logger.info(f"Revised picture question result: {revised_question}")
            self._store_revision_history(paper_id, original_question, revised_question, teacher_feedback)
            return revised_question
        
        print(f"[DEBUG] TAKING LLM PATH (NOT PICTURE)")
        
        # Step 1: Build search query from feedback + original question context
        search_query = self._build_search_query(original_question, teacher_feedback)
        logger.info(f"Search query: {search_query}")
        
        # Step 2: Search textbook for relevant context
        textbook_context = await self._search_textbook_context(search_query, teacher_feedback)
        logger.info(f"Found {len(textbook_context)} textbook passages")
        
        # Step 3: Search question papers for similar questions
        similar_questions = await self._search_similar_questions(search_query, original_question)
        logger.info(f"Found {len(similar_questions)} similar questions")
        
        # Step 4: Generate revised question using LLM
        revised_question = await self._generate_revised_question(
            original_question,
            teacher_feedback,
            textbook_context,
            similar_questions
        )
        
        # Step 5: Store revision history
        self._store_revision_history(paper_id, original_question, revised_question, teacher_feedback)
        
        return revised_question
    
    async def _revise_picture_question(
        self,
        original_question: Dict[str, Any],
        teacher_feedback: str
    ) -> Dict[str, Any]:
        """
        Handle revision of picture-based questions (Q42).
        Gets a new image based on teacher feedback.
        
        Args:
            original_question: The original picture question
            teacher_feedback: Teacher's feedback about what image they want
            
        Returns:
            Revised question with new image
        """
        print(f"[DEBUG] _revise_picture_question called!")
        current_topic = original_question.get('image_topic', '')
        print(f"[DEBUG] Current topic: {current_topic}")
        
        # Get new picture based on feedback
        new_picture_question = await get_new_picture_for_revision(teacher_feedback, current_topic)
        print(f"[DEBUG] New picture question from image_search: {new_picture_question}")
        
        # Preserve question number and other metadata
        new_picture_question['question_number'] = original_question.get('question_number', 42)
        new_picture_question['part'] = original_question.get('part', 'III')
        new_picture_question['revision_id'] = str(uuid.uuid4())
        new_picture_question['revised_at'] = datetime.utcnow().isoformat()
        new_picture_question['teacher_feedback'] = teacher_feedback
        new_picture_question['is_revised'] = True
        new_picture_question['previous_topic'] = current_topic
        
        logger.info(f"Revised picture question: {current_topic} -> {new_picture_question.get('image_topic')}")
        
        return new_picture_question
    
    def _build_search_query(self, original_question: Dict, feedback: str) -> str:
        """Build a search query combining question context and feedback"""
        parts = []
        
        # Add feedback (primary intent)
        parts.append(feedback)
        
        # Add question context
        if original_question.get('section'):
            parts.append(original_question['section'])
        if original_question.get('unit_name'):
            parts.append(original_question['unit_name'])
        if original_question.get('lesson_type'):
            parts.append(original_question['lesson_type'])
            
        return " ".join(parts)
    
    async def _search_textbook_context(self, query: str, feedback: str) -> List[Dict]:
        """Search textbook collection for relevant passages using vector search"""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                logger.warning("Textbook collection not available")
                return []
            
            # Get embedding for query
            query_embedding = await embed_query(query)
            
            if query_embedding is None:
                logger.warning("Could not generate embedding, falling back to text search")
                # Fallback to simple find with regex
                results = []
                keywords = feedback.split()[:3]  # First 3 words
                for keyword in keywords:
                    docs = list(collection.find({
                        "content": {"$regex": keyword, "$options": "i"}
                    }).limit(3))
                    for doc in docs:
                        results.append({
                            "content": doc.get("content", ""),
                            "unit": doc.get("metadata", {}).get("unit", "Unknown"),
                            "lesson": doc.get("metadata", {}).get("lesson_name", "")
                        })
                return results[:5]
            
            # Try vector search
            try:
                pipeline = [
                    {
                        "$vectorSearch": {
                            "index": "vector_index",
                            "path": "embedding",
                            "queryVector": query_embedding,
                            "numCandidates": 50,
                            "limit": 5
                        }
                    },
                    {
                        "$project": {
                            "content": 1,
                            "metadata": 1,
                            "score": {"$meta": "vectorSearchScore"},
                            "_id": 0
                        }
                    }
                ]
                
                results = list(collection.aggregate(pipeline))
                return [
                    {
                        "content": doc.get("content", ""),
                        "unit": doc.get("metadata", {}).get("unit", "Unknown"),
                        "lesson": doc.get("metadata", {}).get("lesson_name", "")
                    }
                    for doc in results
                ]
            except Exception as e:
                logger.warning(f"Vector search failed, using fallback: {e}")
                # Fallback to regular find
                docs = list(collection.find().limit(5))
                return [
                    {
                        "content": doc.get("content", ""),
                        "unit": doc.get("metadata", {}).get("unit", "Unknown"),
                        "lesson": doc.get("metadata", {}).get("lesson_name", "")
                    }
                    for doc in docs
                ]
                
        except Exception as e:
            logger.error(f"Error searching textbook: {e}")
            return []
    
    async def _search_similar_questions(self, query: str, original_question: Dict) -> List[Dict]:
        """Search question papers for similar questions"""
        try:
            collection = mongo_client.questionpapers_collection
            if collection is None:
                logger.warning("Question papers collection not available")
                return []
            
            # Build filter based on question type
            filters = {}
            if original_question.get('part'):
                filters['part'] = original_question['part']
            if original_question.get('section'):
                filters['section'] = original_question['section']
            
            # Simple find with filters
            docs = list(collection.find(filters).limit(5))
            
            return [
                {
                    "question": doc.get("question", doc.get("question_text", "")),
                    "part": doc.get("part", ""),
                    "section": doc.get("section", ""),
                    "marks": doc.get("marks", 0),
                    "unit": doc.get("unit", doc.get("unit_name", ""))
                }
                for doc in docs
            ]
                
        except Exception as e:
            logger.error(f"Error searching questions: {e}")
            return []
    
    async def _generate_revised_question(
        self,
        original_question: Dict,
        teacher_feedback: str,
        textbook_context: List[Dict],
        similar_questions: List[Dict]
    ) -> Dict[str, Any]:
        """Generate revised question using LLM with RAG context"""
        
        # Format textbook context
        textbook_text = "\n\n".join([
            f"[From {ctx.get('unit', 'Unknown Unit')}]\n{ctx.get('content', '')[:500]}"
            for ctx in textbook_context[:3]
        ]) if textbook_context else "No specific textbook context found."
        
        # Format similar questions
        similar_q_text = "\n".join([
            f"- {q.get('question', '')}"
            for q in similar_questions[:3]
        ]) if similar_questions else "No similar questions found."
        
        # Build the prompt
        prompt = f"""You are an expert exam question writer for 10th grade TN SSLC English.

ORIGINAL QUESTION:
- Question Number: {original_question.get('question_number')}
- Part: {original_question.get('part')}
- Section: {original_question.get('section')}
- Question: {original_question.get('question_text')}
- Marks: {original_question.get('marks')}
- Unit: {original_question.get('unit_name', 'Not specified')}

TEACHER'S FEEDBACK:
{teacher_feedback}

TEXTBOOK CONTEXT (for reference):
{textbook_text}

SIMILAR QUESTIONS (for reference):
{similar_q_text}

INSTRUCTIONS:
1. Generate a REVISED question that addresses the teacher's feedback
2. Keep the same format (Part {original_question.get('part')}, {original_question.get('marks')} marks)
3. Ensure the question is appropriate for 10th grade level
4. If the teacher wants a different unit/topic, use the textbook context provided
5. Make it original - don't copy from similar questions

Respond ONLY with this exact JSON format (no markdown, no explanation):
{{
    "question_number": {original_question.get('question_number')},
    "part": "{original_question.get('part')}",
    "section": "{original_question.get('section')}",
    "question_text": "<your revised question>",
    "marks": {original_question.get('marks')},
    "internal_choice": {str(original_question.get('internal_choice', False)).lower()},
    "unit_name": "<unit name based on content used>",
    "lesson_type": "{original_question.get('lesson_type', 'general')}",
    "brief_answer_guide": "<brief answer guide>"
}}"""

        try:
            llm = get_llm()
            response = await llm.generate(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.7
            )
            
            # Parse JSON response
            response_text = response.strip()
            
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Find JSON object in response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response_text = json_match.group()
            
            revised = json.loads(response_text.strip())
            
            # Add revision metadata
            revised['revision_id'] = str(uuid.uuid4())
            revised['revised_at'] = datetime.utcnow().isoformat()
            revised['teacher_feedback'] = teacher_feedback
            revised['is_revised'] = True
            
            # Preserve options if original had them (for MCQs)
            if original_question.get('options') and 'options' not in revised:
                revised['options'] = original_question.get('options')
            
            logger.info(f"Successfully revised question {original_question.get('question_number')}")
            return revised
            
        except Exception as e:
            logger.error(f"Error generating revised question: {e}")
            # Return original with error flag
            return {
                **original_question,
                'revision_error': str(e),
                'is_revised': False
            }
    
    def _store_revision_history(
        self,
        paper_id: str,
        original: Dict,
        revised: Dict,
        feedback: str
    ):
        """Store revision in history for tracking"""
        if paper_id not in self.revision_history:
            self.revision_history[paper_id] = []
        
        self.revision_history[paper_id].append({
            'revision_id': revised.get('revision_id', str(uuid.uuid4())),
            'question_number': original.get('question_number'),
            'original_question': original,
            'revised_question': revised,
            'teacher_feedback': feedback,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        logger.info(f"Stored revision history for paper {paper_id}, question {original.get('question_number')}")
    
    def get_revision_history(self, paper_id: str, question_number: Optional[int] = None) -> List[Dict]:
        """Get revision history for a paper or specific question"""
        history = self.revision_history.get(paper_id, [])
        
        if question_number is not None:
            history = [h for h in history if h['question_number'] == question_number]
        
        return history


# Singleton instance
_reviser_instance: Optional[QuestionReviser] = None


def get_question_reviser() -> QuestionReviser:
    """Get singleton instance of QuestionReviser"""
    global _reviser_instance
    if _reviser_instance is None:
        _reviser_instance = QuestionReviser()
    return _reviser_instance
