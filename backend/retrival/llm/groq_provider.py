from groq import Groq
from .base import LLMProvider
from config import settings
import json
import logging

logger = logging.getLogger(__name__)

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str = None, model: str = None):
        self.client = Groq(api_key=api_key or settings.groq_api_key)
        self.model = model or settings.groq_model
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
    ) -> str:
        """Use Groq to generate response."""
        try:
            message = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return message.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation failed: {str(e)}")
            raise
    
    async def evaluate_answer(
        self,
        official_answer: str,
        student_answer: str,
        evidence_chunks: list[str],
    ) -> dict:
        """Evaluate semantic match between student & official answer."""
        prompt = f"""You are an English exam evaluator for TN SSLC (10th Standard).

OFFICIAL ANSWER:
{official_answer}

STUDENT ANSWER:
{student_answer}

SUPPORTING TEXTBOOK EVIDENCE:
{chr(10).join([f"- {chunk[:200]}" for chunk in evidence_chunks])}

Evaluate the student answer against the official answer. Be fair but strict.
Respond ONLY with valid JSON (no markdown, no extra text):
{{
    "match_percentage": <0-100 integer>,
    "missing_points": [<list of key points not covered>],
    "extra_points": [<correct additional points>],
    "improvements": "<detailed actionable feedback for student>"
}}"""
        
        try:
            response = await self.generate(prompt, max_tokens=512, temperature=0.3)
            # Parse JSON response
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq evaluation response: {response}")
            return {
                "match_percentage": 0,
                "missing_points": [],
                "extra_points": [],
                "improvements": "Evaluation error - please retry"
            }
        except Exception as e:
            logger.error(f"Answer evaluation failed: {str(e)}")
            raise
    
    async def generate_paper(
        self,
        blueprint: dict,
        questions: list[dict],
    ) -> dict:
        """Generate paper structure with selected questions."""
        prompt = f"""You are a TN SSLC English paper generator.

BLUEPRINT:
{json.dumps(blueprint, indent=2)}

AVAILABLE QUESTIONS:
{json.dumps(questions, indent=2)}

Generate a question paper following the TN SSLC structure strictly.
Return JSON with selected questions mapped to blueprint sections:
{{
    "part_i": [<14 MCQ question numbers>],
    "part_ii": {{
        "prose": [<3 selected from 4>],
        "poetry": [<3 selected from 4>],
        "grammar": [<3 selected from 5>],
        "map": <1 map question>
    }},
    "part_iii": {{
        "prose_paragraph": [<2 selected from 4>],
        "poetry": [<2 selected from 4>],
        "supplementary": [<1 selected from 2>],
        "writing": [<4 selected from 6>],
        "memory_poem": <1 memory poem>
    }},
    "part_iv": {{
        "question_46": <comprehension question>,
        "question_47": <prose/poem/supplementary question>
    }}
}}"""
        
        try:
            response = await self.generate(prompt, max_tokens=1024, temperature=0.5)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Paper generation failed: {str(e)}")
            raise
