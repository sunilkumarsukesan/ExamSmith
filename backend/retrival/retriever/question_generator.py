"""
Question Generation Module

Generates original questions for each section of the TN SSLC English exam
using LLM with paraphrased textbook context.
"""

from typing import List, Dict, Tuple
import logging
from llm.factory import llm
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation

logger = logging.getLogger(__name__)


class QuestionGenerator:
    """Generates original exam questions from retrieved textbook content."""

    def __init__(self):
        self.llm = llm
        self.hybrid_search = HybridSearch()

    async def generate_part_i_mcqs(
        self,
        textbook_context: str,
        previous_paper_context: str,
    ) -> List[Dict]:
        """
        Generate 14 MCQ questions for Part I.
        
        Topics:
        - Q1-3: Synonyms
        - Q4-6: Antonyms
        - Q7: Plural Forms
        - Q8: Prefix/Suffix/Affixes
        - Q9: Abbreviations/Acronyms
        - Q10: Phrasal Verbs
        - Q11: Compound Words
        - Q12: Prepositions
        - Q13: Tenses
        - Q14: Linkers
        """
        
        prompt = f"""You are a TN SSLC English exam question generator.

TEXTBOOK VOCABULARY CONTEXT:
{textbook_context}

PREVIOUS EXAM STYLE REFERENCE (for difficulty calibration only):
{previous_paper_context}

Generate 14 original MCQ questions for Part I with the following STRICT requirements:

TOPIC MAPPING:
- Questions 1-3: Generate 3 DISTINCT SYNONYM questions
- Questions 4-6: Generate 3 DISTINCT ANTONYM questions
- Question 7: Generate 1 PLURAL FORMS question
- Question 8: Generate 1 PREFIX/SUFFIX/AFFIXES question
- Question 9: Generate 1 ABBREVIATIONS/ACRONYMS question
- Question 10: Generate 1 PHRASAL VERBS question
- Question 11: Generate 1 COMPOUND WORDS question
- Question 12: Generate 1 PREPOSITIONS question
- Question 13: Generate 1 TENSES question
- Question 14: Generate 1 LINKERS/CONNECTORS question

GENERATION RULES:
- Use vocabulary from TEXTBOOK CONTEXT only
- Paraphrase all words/definitions (never copy textbook sentences)
- Create 4 DISTINCT distractors for each MCQ (A, B, C, D)
- Ensure only 1 correct answer per question
- Do NOT copy any question structure from PREVIOUS EXAM STYLE REFERENCE
- Difficulty must match board level (moderate)
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
    "lesson_type": "glossary",
    "options": ["a) <word1>", "b) <word2>", "c) <word3>", "d) <word4>"],
    "correct_option": "<a/b/c/d>"
  }},
  ...
]

Generate all 14 questions now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=2048,
                temperature=0.7
            )
            
            questions = self._parse_json_response(response)
            logger.info(f"Generated {len(questions)} Part I MCQ questions")
            return questions
            
        except Exception as e:
            logger.error(f"Part I MCQ generation failed: {str(e)}")
            return []

    async def generate_prose_questions(
        self,
        lesson_number: int,
        textbook_context: str,
        marks: int = 2,
        previous_paper_context: str = None,
    ) -> Dict:
        """
        Generate prose comprehension question for given lesson.
        
        Args:
            lesson_number: Prose lesson number (1-6)
            textbook_context: Textbook content for lesson
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference from previous exams
        """
        
        prompt = f"""You are a TN SSLC English exam question generator.

PROSE LESSON CONTEXT (Lesson {lesson_number}):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL prose comprehension question based on the lesson.

REQUIREMENTS:
- Question must assess understanding of lesson theme/character/incident
- Do NOT copy textbook sentences
- Paraphrase all content
- Do NOT reuse structure from previous exams
- Difficulty: Board-level ({marks} marks)
- Answer should be 30-50 words (for 2 marks) or 80-120 words (for 5 marks)

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II" or "III",
  "section": "Prose",
  "question_text": "<question here>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Prose Lesson {lesson_number}",
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
    ) -> Dict:
        """
        Generate poetry comprehension question for given poem.
        
        Args:
            poem_name: Name of the poem
            textbook_context: Poetic lines and context
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference
        """
        
        prompt = f"""You are a TN SSLC English exam question generator.

POEM CONTEXT ({poem_name}):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL poetry comprehension question based on this poem.

REQUIREMENTS:
- Question must focus on: meaning, imagery, tone, literary device, or theme
- Do NOT copy poetic lines or question structures from previous exams
- Paraphrase all content
- Difficulty: Board-level ({marks} marks)
- Answer should assess deeper understanding, not mere memorization

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II" or "III",
  "section": "Poetry",
  "question_text": "<question here>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Poetry: {poem_name}",
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
    ) -> Dict:
        """
        Generate grammar question for given area.
        
        Args:
            grammar_area: One of: voice, speech, punctuation, sentence_types, rearrangement
            textbook_context: Example sentences from lessons
            marks: Question marks (2 or 5)
            previous_paper_context: Style reference
        """
        
        grammar_instructions = {
            "voice": "Create an Active to Passive Voice transformation question. Provide a sentence in active voice; ask student to convert to passive.",
            "speech": "Create a Direct to Indirect Speech transformation question. Provide direct speech; ask student to convert to indirect.",
            "punctuation": "Create a punctuation correction question. Provide incorrectly punctuated sentence; ask student to correct.",
            "sentence_types": "Create a sentence type identification question. Ask student to identify if sentence is simple, compound, or complex.",
            "rearrangement": "Create a word order rearrangement question. Provide jumbled words; ask student to form correct sentence.",
        }
        
        prompt = f"""You are a TN SSLC English exam question generator.

TEXTBOOK CONTEXT (Grammar examples):
{textbook_context}

PREVIOUS EXAM STYLE (for difficulty only - DO NOT copy):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL grammar question for: {grammar_area.upper()}

GENERATION APPROACH:
{grammar_instructions.get(grammar_area, "Generate appropriate grammar question")}

REQUIREMENTS:
- Do NOT copy example sentences from textbook verbatim
- Paraphrase and adapt sentences from textbook context
- Do NOT reuse question structure from previous exams
- Difficulty: Board-level ({marks} marks)
- Provide clear instructions for student response

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "II",
  "section": "Grammar",
  "question_text": "<question instruction with example>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Grammar: {grammar_area.title()}",
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

    async def generate_writing_questions(
        self,
        writing_type: str,
        previous_paper_context: str = None,
    ) -> Dict:
        """
        Generate writing skill question.
        
        Args:
            writing_type: One of: letter, email, paragraph, dialogue, story
            previous_paper_context: Style reference
        """
        
        writing_prompts = {
            "letter": "Generate a letter writing task (formal or informal). Provide context (to whom, for what purpose) and ask student to write.",
            "email": "Generate an email writing task. Provide scenario and ask student to write professional email.",
            "paragraph": "Generate a paragraph writing task. Provide a topic and ask student to write 8-10 sentence paragraph.",
            "dialogue": "Generate a dialogue writing task. Provide scenario and ask student to write conversation between two persons.",
            "story": "Generate a story writing task. Provide key words/outline and ask student to narrate story in 200-250 words.",
        }
        
        prompt = f"""You are a TN SSLC English exam question generator.

PREVIOUS EXAM STYLE (for reference only):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL {writing_type.upper()} WRITING question.

GENERATION APPROACH:
{writing_prompts.get(writing_type, "Generate appropriate writing question")}

REQUIREMENTS:
- Do NOT copy textbook writing samples
- Create UNIQUE prompt (do NOT reuse previous exam structures)
- Difficulty: Board-level (5 marks)
- Provide clear word count or format guidelines
- Task should assess writing skills, not copying

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "III",
  "section": "Writing Skills",
  "question_text": "<task instruction with context>",
  "marks": 5,
  "internal_choice": false,
  "unit_name": "Writing: {writing_type.title()}",
  "lesson_type": "writing",
  "writing_type": "{writing_type}",
  "word_count_limit": <word count or format guideline>,
  "brief_answer_guide": "<marking rubric or format requirements>"
}}

Generate the question now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated writing question for '{writing_type}'")
            return question
            
        except Exception as e:
            logger.error(f"Writing question generation failed: {str(e)}")
            return {}

    async def generate_supplementary_questions(
        self,
        story_name: str,
        textbook_context: str,
        marks: int = 5,
        previous_paper_context: str = None,
    ) -> Dict:
        """Generate supplementary story comprehension question."""
        
        prompt = f"""You are a TN SSLC English exam question generator.

SUPPLEMENTARY STORY CONTEXT ({story_name}):
{textbook_context}

PREVIOUS EXAM STYLE (for reference only):
{previous_paper_context or "Not provided"}

Generate 1 ORIGINAL comprehension question for this supplementary story.

REQUIREMENTS:
- Question must assess plot understanding, inference, or moral
- Do NOT copy story text verbatim
- Do NOT reuse previous exam patterns
- Difficulty: Board-level ({marks} marks)
- Answer should be 80-120 words

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": <to be assigned>,
  "part": "III",
  "section": "Supplementary",
  "question_text": "<question here>",
  "marks": {marks},
  "internal_choice": false,
  "unit_name": "Supplementary: {story_name}",
  "lesson_type": "supplementary",
  "brief_answer_guide": "<answer hint>"
}}

Generate the question now:"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.7
            )
            
            question = self._parse_json_response(response, single=True)
            logger.info(f"Generated supplementary question for '{story_name}'")
            return question
            
        except Exception as e:
            logger.error(f"Supplementary question generation failed: {str(e)}")
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
