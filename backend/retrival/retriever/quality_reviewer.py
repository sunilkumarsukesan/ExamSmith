"""
Quality Reviewer for Generated Question Papers

Applies post-generation quality fixes to ensure TN Board alignment:
1. MCQ Quality Rules
2. Grammar Ambiguity Elimination
3. Retrieval De-dependency Reduction
4. Writing Skills Context Simplification
5. Final Validation Check
"""

import logging
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from models import ReviewQuestionInput
from llm.factory import LLMFactory

logger = logging.getLogger("retriever.quality_reviewer")


class QualityReviewer:
    """
    Post-processor that reviews and fixes generated questions
    to ensure strict TN Board alignment.
    """
    
    def __init__(self, llm_provider=None):
        """Initialize the quality reviewer with an LLM provider."""
        self.llm = llm_provider or LLMFactory.create()
        
        # MCQ Review Prompt
        self.mcq_review_prompt = """You are a Tamil Nadu SSLC Class 10 English exam question quality reviewer.

Review this MCQ and fix if it violates any rules:

RULES:
1. Exactly ONE correct answer must exist
2. Include 2 close, plausible distractors (same part of speech, similar meaning)
3. Include 1 clearly incorrect distractor
4. Vocabulary must be Class 10 TN Board level (not too easy, not too hard)
5. Context must be from prose/poetry content, not abstract dictionary usage
6. All options must be grammatically parallel

MCQ TO REVIEW:
Question: {question_text}
Options: {options}
Correct Answer: {correct_answer}
Source: {unit_name}

If the MCQ is good, return: {{"fixed": false}}

If the MCQ needs fixing, return ONLY valid JSON:
{{
    "fixed": true,
    "question_text": "improved question text",
    "options": ["A) option1", "B) option2", "C) option3", "D) option4"],
    "correct_answer": "A/B/C/D"
}}
"""

        # Grammar Review Prompt
        self.grammar_review_prompt = """You are a Tamil Nadu SSLC Class 10 English grammar question reviewer.

Review this grammar question for ambiguity:

RULES:
1. Ensure ONLY ONE valid correct answer exists
2. Avoid sentences that allow multiple valid transformations
3. Use predictable board-style constructions
4. Do NOT use advanced grammar beyond Class 10 syllabus

GRAMMAR QUESTION:
Question: {question_text}
Grammar Area: {grammar_area}

If unambiguous, return: {{"fixed": false}}

If ambiguous or problematic, return ONLY valid JSON:
{{
    "fixed": true,
    "question_text": "unambiguous rewritten question"
}}
"""

        # Prose/Poetry Review Prompt (RAG de-dependency)
        self.prose_poetry_review_prompt = """You are reviewing a prose/poetry question for Tamil Nadu SSLC Class 10 English exam.

GOAL: Reduce textbook dependency - questions should test UNDERSTANDING, not RECALL.

RULES:
1. Do NOT retain exact textbook sentence structure
2. Abstract the core idea, then reframe the question
3. Avoid phrases that closely match textbook wording
4. Preserve the meaning and learning objective

QUESTION TO REVIEW:
Question: {question_text}
Lesson Type: {lesson_type}
Unit: {unit_name}
Marks: {marks}

If the question already tests understanding (not recall), return: {{"fixed": false}}

If too textbook-dependent, return ONLY valid JSON:
{{
    "fixed": true,
    "question_text": "reframed question testing understanding"
}}
"""

        # Writing Skills Review Prompt
        self.writing_review_prompt = """You are reviewing a writing skills question for Tamil Nadu SSLC Class 10 English exam.

RULES:
1. Use familiar school, village, or student-life contexts
2. Avoid overly administrative or complex real-world scenarios
3. Keep prompts clear, concrete, and board-friendly
4. Student should be able to relate to the scenario

WRITING QUESTION:
Question: {question_text}
Section: {section}
Marks: {marks}

If context is appropriate, return: {{"fixed": false}}

If too formal/complex, return ONLY valid JSON:
{{
    "fixed": true,
    "question_text": "simplified, student-friendly question"
}}
"""

    async def review_paper(self, questions: List[ReviewQuestionInput]) -> Tuple[List[ReviewQuestionInput], Dict[str, Any]]:
        """
        Review and fix all questions in the paper.
        
        Args:
            questions: List of generated questions
            
        Returns:
            Tuple of (fixed_questions, review_report)
        """
        logger.info("=" * 60)
        logger.info("STARTING QUALITY REVIEW")
        logger.info("=" * 60)
        
        fixed_questions = []
        review_report = {
            "total_questions": len(questions),
            "mcq_reviewed": 0,
            "mcq_fixes": 0,
            "grammar_reviewed": 0,
            "grammar_fixes": 0,
            "prose_poetry_reviewed": 0,
            "prose_poetry_fixes": 0,
            "writing_reviewed": 0,
            "writing_fixes": 0,
            "total_fixes": 0,
            "validation_passed": True,
            "details": []
        }
        
        for q in questions:
            fixed_q, was_fixed, fix_type = await self._review_question(q)
            fixed_questions.append(fixed_q)
            
            if was_fixed:
                review_report["total_fixes"] += 1
                review_report["details"].append({
                    "question_number": q.question_number,
                    "fix_type": fix_type,
                    "original": q.question_text[:80] + "..." if len(q.question_text) > 80 else q.question_text
                })
                
                if fix_type == "mcq":
                    review_report["mcq_fixes"] += 1
                elif fix_type == "grammar":
                    review_report["grammar_fixes"] += 1
                elif fix_type == "prose_poetry":
                    review_report["prose_poetry_fixes"] += 1
                elif fix_type == "writing":
                    review_report["writing_fixes"] += 1
        
        # Final validation
        review_report["validation_passed"] = self._validate_paper_structure(
            questions, fixed_questions
        )
        
        logger.info(f"Quality review complete: {review_report['total_fixes']} fixes applied")
        logger.info("=" * 60)
        
        return fixed_questions, review_report

    async def _review_question(self, question: ReviewQuestionInput) -> Tuple[ReviewQuestionInput, bool, Optional[str]]:
        """
        Review a single question and apply fixes if needed.
        
        Returns:
            Tuple of (fixed_question, was_fixed, fix_type)
        """
        try:
            # Determine question type and apply appropriate review
            if question.part == "I" or (question.options and len(question.options) >= 4):
                return await self._review_mcq(question)
            
            elif question.grammar_area or (question.lesson_type and "grammar" in question.lesson_type.lower()):
                return await self._review_grammar(question)
            
            elif question.lesson_type in ["prose", "poetry", "supplementary"]:
                return await self._review_prose_poetry(question)
            
            elif question.lesson_type == "writing" or (question.section and "writing" in question.section.lower()):
                return await self._review_writing(question)
            
            else:
                # No review needed for other types (memory poem, map, etc.)
                return question, False, None
                
        except Exception as e:
            logger.error(f"Error reviewing Q{question.question_number}: {e}")
            return question, False, None

    async def _review_mcq(self, question: ReviewQuestionInput) -> Tuple[ReviewQuestionInput, bool, Optional[str]]:
        """Review and fix MCQ questions."""
        try:
            prompt = self.mcq_review_prompt.format(
                question_text=question.question_text,
                options=question.options or [],
                correct_answer=question.correct_answer or "",
                unit_name=question.unit_name or ""
            )
            
            response = await self.llm.generate(prompt, max_tokens=500)
            
            if response:
                fixed_data = self._parse_json_response(response)
                if fixed_data and fixed_data.get("fixed", False):
                    if "question_text" in fixed_data:
                        question.question_text = fixed_data["question_text"]
                    if "options" in fixed_data:
                        question.options = fixed_data["options"]
                    if "correct_answer" in fixed_data:
                        question.correct_answer = fixed_data["correct_answer"]
                    logger.info(f"  ✓ Fixed MCQ Q{question.question_number}")
                    return question, True, "mcq"
            
            return question, False, None
            
        except Exception as e:
            logger.error(f"MCQ review failed for Q{question.question_number}: {e}")
            return question, False, None

    async def _review_grammar(self, question: ReviewQuestionInput) -> Tuple[ReviewQuestionInput, bool, Optional[str]]:
        """Review and fix grammar questions for ambiguity."""
        try:
            prompt = self.grammar_review_prompt.format(
                question_text=question.question_text,
                grammar_area=question.grammar_area or "General"
            )
            
            response = await self.llm.generate(prompt, max_tokens=300)
            
            if response:
                fixed_data = self._parse_json_response(response)
                if fixed_data and fixed_data.get("fixed", False):
                    if "question_text" in fixed_data:
                        question.question_text = fixed_data["question_text"]
                    logger.info(f"  ✓ Fixed Grammar Q{question.question_number}")
                    return question, True, "grammar"
            
            return question, False, None
            
        except Exception as e:
            logger.error(f"Grammar review failed for Q{question.question_number}: {e}")
            return question, False, None

    async def _review_prose_poetry(self, question: ReviewQuestionInput) -> Tuple[ReviewQuestionInput, bool, Optional[str]]:
        """Review and fix prose/poetry questions for textbook dependency."""
        try:
            prompt = self.prose_poetry_review_prompt.format(
                question_text=question.question_text,
                lesson_type=question.lesson_type or "",
                unit_name=question.unit_name or "",
                marks=question.marks
            )
            
            response = await self.llm.generate(prompt, max_tokens=400)
            
            if response:
                fixed_data = self._parse_json_response(response)
                if fixed_data and fixed_data.get("fixed", False):
                    if "question_text" in fixed_data:
                        question.question_text = fixed_data["question_text"]
                    logger.info(f"  ✓ Fixed Prose/Poetry Q{question.question_number}")
                    return question, True, "prose_poetry"
            
            return question, False, None
            
        except Exception as e:
            logger.error(f"Prose/Poetry review failed for Q{question.question_number}: {e}")
            return question, False, None

    async def _review_writing(self, question: ReviewQuestionInput) -> Tuple[ReviewQuestionInput, bool, Optional[str]]:
        """Review and fix writing skills questions for context simplification."""
        try:
            prompt = self.writing_review_prompt.format(
                question_text=question.question_text,
                section=question.section or "",
                marks=question.marks
            )
            
            response = await self.llm.generate(prompt, max_tokens=500)
            
            if response:
                fixed_data = self._parse_json_response(response)
                if fixed_data and fixed_data.get("fixed", False):
                    if "question_text" in fixed_data:
                        question.question_text = fixed_data["question_text"]
                    logger.info(f"  ✓ Fixed Writing Q{question.question_number}")
                    return question, True, "writing"
            
            return question, False, None
            
        except Exception as e:
            logger.error(f"Writing review failed for Q{question.question_number}: {e}")
            return question, False, None

    def _parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response."""
        try:
            # Clean response
            response = response.strip()
            
            # Try direct parse
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            try:
                # Find JSON object
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response[start:end]
                    return json.loads(json_str)
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    def _validate_paper_structure(
        self, 
        original: List[ReviewQuestionInput], 
        fixed: List[ReviewQuestionInput]
    ) -> bool:
        """
        Validate that paper structure is preserved after fixes.
        
        Checks:
        - Question counts unchanged
        - Marks distribution unchanged
        - Internal choices preserved
        """
        if len(original) != len(fixed):
            logger.error(f"Question count mismatch: {len(original)} vs {len(fixed)}")
            return False
        
        # Check marks preservation
        original_marks = sum(q.marks for q in original)
        fixed_marks = sum(q.marks for q in fixed)
        if original_marks != fixed_marks:
            logger.error(f"Marks mismatch: {original_marks} vs {fixed_marks}")
            return False
        
        # Check internal choice preservation
        original_choices = sum(1 for q in original if q.internal_choice)
        fixed_choices = sum(1 for q in fixed if q.internal_choice)
        if original_choices != fixed_choices:
            logger.error(f"Internal choice count mismatch: {original_choices} vs {fixed_choices}")
            return False
        
        # Check part distribution
        for part in ["I", "II", "III", "IV"]:
            orig_count = sum(1 for q in original if q.part == part)
            fixed_count = sum(1 for q in fixed if q.part == part)
            if orig_count != fixed_count:
                logger.error(f"Part {part} count mismatch: {orig_count} vs {fixed_count}")
                return False
        
        logger.info("✓ Paper structure validation PASSED")
        return True


# Singleton instance
_quality_reviewer: Optional[QualityReviewer] = None


def get_quality_reviewer() -> QualityReviewer:
    """Get or create the quality reviewer singleton."""
    global _quality_reviewer
    if _quality_reviewer is None:
        _quality_reviewer = QualityReviewer()
    return _quality_reviewer
