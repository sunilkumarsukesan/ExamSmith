"""
Question Generation Module

Generates original questions for each section of the TN SSLC English exam
using LLM with paraphrased textbook context.
"""

from typing import List, Dict, Tuple
import logging
import random
from llm.factory import get_llm
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates original exam questions from retrieved textbook content."""

    def __init__(self):
        self.llm = get_llm()
        self.hybrid_search = HybridSearch()
    
    def _get_random_unit(self) -> int:
        """Get a random unit from 1-7."""
        return random.randint(1, 7)

    async def generate_part_i_mcqs(
        self,
        textbook_context: str,
        previous_paper_context: str,
    ) -> List[Dict]:
        """
        Generate 14 MCQ questions for Part I from ALL 7 units.
        
        Topics are randomly distributed across all 7 units to ensure diversity.
        """
        import random
        
        # Define all question types
        question_types = [
            "SYNONYM",
            "SYNONYM",
            "SYNONYM",
            "ANTONYM",
            "ANTONYM",
            "ANTONYM",
            "PLURAL FORMS",
            "PREFIX/SUFFIX/AFFIXES",
            "ABBREVIATIONS/ACRONYMS",
            "PHRASAL VERBS",
            "COMPOUND WORDS",
            "PREPOSITIONS",
            "TENSES",
            "LINKERS/CONNECTORS"
        ]
        
        # Randomly assign units 1-7 to questions, ensuring all units are covered
        # With 14 questions and 7 units, each unit will appear exactly twice
        units = list(range(1, 8)) * 2  # [1,2,3,4,5,6,7,1,2,3,4,5,6,7]
        random.shuffle(units)
        
        # Build randomized topic mapping
        topic_mapping = ""
        for q_num in range(1, 15):
            unit_num = units[q_num - 1]
            question_type = question_types[q_num - 1]
            topic_mapping += f"- Question {q_num}: {question_type} question from Unit {unit_num} content\n"
        
        prompt = f"""You are a TN SSLC English exam question generator.

TEXTBOOK CONTENT FROM ALL 7 UNITS:
{textbook_context}

PREVIOUS EXAM STYLE REFERENCE (for difficulty calibration only):
{previous_paper_context}

Generate 14 original MCQ questions for Part I with the following STRICT requirements:

CRITICAL RULE: DISTRIBUTE QUESTIONS ACROSS ALL 7 UNITS WITH RANDOMIZATION!
Each question MUST specify which unit it is from in the unit_name field.
All 7 units must be covered (each unit appears exactly twice among the 14 questions).

RANDOMIZED TOPIC MAPPING WITH UNIT DISTRIBUTION:
{topic_mapping}

GENERATION RULES:
- Use vocabulary from the SPECIFIC UNIT mentioned above
- Look for [Unit X] markers in the context to identify unit content
- Paraphrase all words/definitions (never copy textbook sentences)
- Create 4 DISTINCT distractors for each MCQ (A, B, C, D)
- Ensure only 1 correct answer per question
- Difficulty must match Class 10 board level (moderate)
- All questions in Indian English

Response format: Return ONLY valid JSON array (no markdown, no explanations):
[
  {{
    "question_number": 1,
    "part": "I",
    "section": "Vocabulary",
    "question_text": "<synonym question here>",
    "marks": 1,
    "internal_choice": false,
    "unit_name": "Vocabulary Unit 1",
    "lesson_type": "vocabulary",
    "options": ["a) <word1>", "b) <word2>", "c) <word3>", "d) <word4>"],
    "correct_option": "<a/b/c/d>"
  }},
  {{
    "question_number": 2,
    "part": "I",
    "section": "Vocabulary",
    "question_text": "<synonym question from Unit 3>",
    "marks": 1,
    "internal_choice": false,
    "unit_name": "Vocabulary Unit 3",
    "lesson_type": "vocabulary",
    "options": ["a) <word1>", "b) <word2>", "c) <word3>", "d) <word4>"],
    "correct_option": "<a/b/c/d>"
  }},
  ...continue for all 14 questions with correct unit assignments...
]

Generate all 14 questions now, ensuring DIVERSE UNIT COVERAGE:"""

        try:
            logger.info("Calling LLM for Part I MCQ generation...")
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=4000,  # Increased for 14 questions with detailed JSON
                temperature=0.5
            )
            
            logger.info(f"LLM response received, length: {len(response)} chars")
            
            questions = self._parse_json_response(response)
            
            if not questions:
                logger.warning(f"Part I MCQ parsing returned empty. Raw response (first 500 chars): {response[:500]}")
                return []
            
            # Log unit distribution
            unit_counts = {}
            for q in questions:
                unit = q.get("unit_name", "Unknown")
                unit_counts[unit] = unit_counts.get(unit, 0) + 1
            logger.info(f"Generated {len(questions)} Part I MCQ questions with unit distribution: {unit_counts}")
            
            return questions
            
        except Exception as e:
            logger.error(f"Part I MCQ generation failed: {str(e)}", exc_info=True)
            return []

    async def generate_prose_questions(
        self,
        lesson_number: int,
        textbook_context: str,
        marks: int = 2,
        previous_paper_context: str = None,
        unit_number: int = None,
    ) -> Dict:
        """
        Generate prose comprehension question for given lesson.
        
        Args:
            lesson_number: Prose lesson number (1-6)
            textbook_context: Textbook content for lesson
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference from previous exams
            unit_number: Unit number (1-7). If None, a random unit is selected.
        """
        if unit_number is None:
            unit_number = self._get_random_unit()
        
        prompt = f"""You are a TN SSLC English exam question generator.

PROSE LESSON CONTEXT (Lesson {lesson_number}, Unit {unit_number}):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL prose comprehension question based on the lesson from Unit {unit_number}.

REQUIREMENTS:
- Question must assess understanding of lesson theme/character/incident
- Do NOT copy textbook sentences
- Paraphrase all content
- Do NOT reuse structure from previous exams
- Difficulty: Board-level ({marks} marks)
- Answer should be 30-50 words (for 2 marks) or 80-120 words (for 5 marks)
- MUST be from Unit {unit_number} content

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II" or "III",
  "section": "Prose",
  "question_text": "<question here>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Prose Unit {unit_number}",
  "lesson_type": "prose",
  "brief_answer_guide": "<30-50 word answer hint for evaluation>"
}}

Generate the question now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated prose question for Lesson {lesson_number}")
            return question
            
        except Exception as e:
            logger.error(f"Prose question generation failed: {str(e)}")
            return {}

    async def generate_poetry_questions(
        self,
        poem_name: str,
        textbook_context: str,
        marks: int = 2,
        previous_paper_context: str = None,
        unit_number: int = None,
    ) -> Dict:
        """
        Generate poetry comprehension question for given poem.
        
        Args:
            poem_name: Name of the poem
            textbook_context: Poetic lines and context
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference
            unit_number: Unit number (1-7). If None, a random unit is selected.
        """
        if unit_number is None:
            unit_number = self._get_random_unit()
        
        prompt = f"""You are a TN SSLC English exam question generator.

POEM CONTEXT ({poem_name}, Unit {unit_number}):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL poetry comprehension question based on this poem from Unit {unit_number}.

REQUIREMENTS:
- Question must focus on: meaning, imagery, tone, literary device, or theme
- Do NOT copy poetic lines or question structures from previous exams
- Paraphrase all content
- Difficulty: Board-level ({marks} marks)
- Answer should assess deeper understanding, not mere memorization
- MUST be from Unit {unit_number} content

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II" or "III",
  "section": "Poetry",
  "question_text": "<question here>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Poetry Unit {unit_number}: {poem_name}",
  "lesson_type": "poetry",
  "brief_answer_guide": "<answer hint for evaluation>"
}}

Generate the question now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated poetry question for '{poem_name}'")
            return question
            
        except Exception as e:
            logger.error(f"Poetry question generation failed: {str(e)}")
            return {}

    async def generate_grammar_questions(
        self,
        grammar_area: str,
        textbook_context: str,
        marks: int = 2,
        previous_paper_context: str = None,
        unit_number: int = None,
    ) -> Dict:
        """
        Generate grammar question for given area.
        
        Args:
            grammar_area: One of: voice, speech, punctuation, sentence_types, rearrangement
            textbook_context: Example sentences from lessons
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference
            unit_number: Unit number (1-7). If None, a random unit is selected.
        """
        if unit_number is None:
            unit_number = self._get_random_unit()
        
        grammar_instructions = {
            "voice": "Create an Active to Passive Voice transformation question. Provide a sentence in active voice; ask student to convert to passive.",
            "speech": "Create a Direct to Indirect Speech transformation question. Provide direct speech; ask student to convert to indirect.",
            "punctuation": "Create a punctuation correction question. Provide incorrectly punctuated sentence; ask student to correct.",
            "sentence_types": "Create a sentence type identification question. Ask student to identify if sentence is simple, compound, or complex.",
            "rearrangement": "Create a word order rearrangement question. Provide jumbled words; ask student to form correct sentence.",
        }
        
        prompt = f"""You are a TN SSLC English exam question generator.

TEXTBOOK CONTEXT (Grammar examples from Unit {unit_number}):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL grammar question for: {grammar_area.upper()} from Unit {unit_number}

GENERATION APPROACH:
{grammar_instructions.get(grammar_area, "Generate appropriate grammar question")}

REQUIREMENTS:
- Do NOT copy example sentences from textbook verbatim
- Paraphrase and adapt sentences from textbook context (Unit {unit_number})
- Do NOT reuse question structure from previous exams
- Difficulty: Board-level ({marks} marks)
- Provide clear instructions for student response
- MUST use examples from Unit {unit_number}

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II",
  "section": "Grammar",
  "question_text": "<question instruction with example>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Grammar Unit {unit_number}: {grammar_area.title()}",
  "lesson_type": "grammar",
  "grammar_area": "{grammar_area}",
  "brief_answer_guide": "<expected answer format>"
}}

Generate the question now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated grammar question for '{grammar_area}'")
            return question
            
        except Exception as e:
            logger.error(f"Grammar question generation failed: {str(e)}")
            return {}

    async def generate_supplementary_questions(
        self,
        story_name: str,
        textbook_context: str,
        marks: int = 5,
        previous_paper_context: str = None,
        unit_number: int = None,
    ) -> Dict:
        """
        Generate supplementary reader question.
        
        Args:
            story_name: Name of the supplementary story
            textbook_context: Story content
            marks: Question marks (typically 5)
            previous_paper_context: Style reference
            unit_number: Unit number (1-7)
        """
        if unit_number is None:
            unit_number = self._get_random_unit()
        
        prompt = f"""You are a TN SSLC English exam question generator.

SUPPLEMENTARY STORY: "{story_name}" (Unit {unit_number})
STORY CONTEXT:
{textbook_context}

PREVIOUS EXAM STYLE (for reference only):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL comprehension question about this supplementary story.

REQUIREMENTS:
- Question tests understanding of plot, characters, theme, or moral
- Answer should be 5-8 sentences (paragraph length)
- Difficulty appropriate for Class 10 board exam
- Do NOT copy from previous papers
- Use Indian English

Response format (valid JSON only):
{{
  "question_number": 37,
  "part": "III",
  "section": "Supplementary",
  "question_text": "<your original question about the story>",
  "marks": {marks},
  "internal_choice": true,
  "unit_name": "Supplementary Unit {unit_number}",
  "lesson_type": "supplementary",
  "story_name": "{story_name}",
  "brief_answer_guide": "<key points for answer>"
}}"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated supplementary question for '{story_name}'")
            return question
            
        except Exception as e:
            logger.error(f"Supplementary question generation failed: {str(e)}")
            return {}

    async def generate_writing_questions(
        self,
        writing_type: str,
        previous_paper_context: str = None,
        unit_number: int = None,
    ) -> Dict:
        """
        Generate writing skill question.
        
        Args:
            writing_type: Type of writing (letter, email, paragraph, dialogue, story)
            previous_paper_context: Style reference
            unit_number: Unit number (1-7)
        """
        if unit_number is None:
            unit_number = self._get_random_unit()
        
        writing_prompts = {
            "letter": "formal or informal letter (complaint, request, appreciation, or personal)",
            "email": "formal email for official communication",
            "paragraph": "descriptive or narrative paragraph on a given topic",
            "dialogue": "dialogue between two people on a relevant topic",
            "story": "short story based on given hints or beginning"
        }
        
        task_description = writing_prompts.get(writing_type, writing_type)
        
        prompt = f"""You are a TN SSLC English exam question generator.

WRITING TASK TYPE: {writing_type.upper()}
TASK DESCRIPTION: {task_description}

PREVIOUS EXAM STYLE (for reference only):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL writing task question.

REQUIREMENTS:
- Provide clear instructions and context for the writing task
- For letters/emails: provide sender/receiver context
- For paragraphs: give specific topic or theme
- For dialogues: specify participants and situation
- For stories: provide hints or opening line
- Word limit guidance: 100-150 words
- Difficulty appropriate for Class 10

Response format (valid JSON only):
{{
  "question_number": 39,
  "part": "III",
  "section": "Writing",
  "question_text": "<complete writing task with all instructions>",
  "marks": 5,
  "internal_choice": true,
  "unit_name": "Writing Unit {unit_number}",
  "lesson_type": "writing",
  "writing_type": "{writing_type}",
  "brief_answer_guide": "<key points/format for answer>"
}}"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated writing question for '{writing_type}'")
            return question
            
        except Exception as e:
            logger.error(f"Writing question generation failed: {str(e)}")
            return {}

    def _parse_json_response(self, response: str, single: bool = False):
        """Parse JSON response from LLM."""
        import json
        import re
        
        try:
            # Try direct JSON parsing
            return json.loads(response)
        except json.JSONDecodeError:
            try:
                # Try extracting JSON from markdown code blocks
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
                if json_match:
                    return json.loads(json_match.group(1))
                
                # Try extracting JSON array or object
                if response.strip().startswith('['):
                    end = response.rfind(']')
                    if end > 0:
                        return json.loads(response[:end+1])
                elif response.strip().startswith('{'):
                    end = response.rfind('}')
                    if end > 0:
                        return json.loads(response[:end+1])
                
                logger.warning(f"Could not parse LLM JSON response: {response[:200]}")
                return [] if not single else {}
                
            except Exception as e:
                logger.error(f"JSON parsing failed: {str(e)}")
                return [] if not single else {}


# Singleton instance
_question_generator = None


def get_question_generator() -> QuestionGenerator:
    """Get or create the question generator singleton."""
    global _question_generator
    if _question_generator is None:
        _question_generator = QuestionGenerator()
    return _question_generator
