from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime

# ===== Hybrid Search =====
class HybridSearchRequest(BaseModel):
    vector_weight: float = Field(0.5, ge=0.0, le=1.0, description="Vector search weight (0-1)")
    bm25_weight: float = Field(0.5, ge=0.0, le=1.0, description="BM25 search weight (0-1)")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")

# ===== Citations =====
class Citation(BaseModel):
    chunk_id: str
    source: Literal["textbook", "question_paper"]
    page: Optional[int] = None
    lesson_name: Optional[str] = None
    year: Optional[int] = None
    question_number: Optional[str] = None

# ===== /ask Endpoint =====
class AskRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=500)
    hybrid_search: HybridSearchRequest = Field(default_factory=HybridSearchRequest)

class AskResponse(BaseModel):
    answer: str
    sources: List[Citation]
    context_preview: str  # First 200 chars of context for debugging
    retrieval_mode: str = "concept_explanation"

# ===== /similar-questions Endpoint =====
class SimilarQuestionsRequest(BaseModel):
    question_text: str = Field(..., min_length=10, max_length=500)
    top_k: int = Field(5, ge=1, le=20)
    difficulty: Optional[Literal["easy", "medium", "hard"]] = None

class QuestionResult(BaseModel):
    question_number: str
    question_text: str
    question_type: str
    answer_key: Optional[str]
    marks: Optional[int]
    year: Optional[int]
    similarity_score: float
    choices: Optional[List[str]] = None  # For MCQ
    # Tracking fields for validation
    poem_name: Optional[str] = None  # For poetry questions
    story_name: Optional[str] = None  # For supplementary questions
    grammar_area: Optional[str] = None  # For grammar questions (VOICE, SPEECH, etc.)
    choice_group: Optional[str] = None  # For internal choice (A, B, C)
    lesson_number: Optional[int] = None  # For prose lessons (1-6)

class SimilarQuestionsResponse(BaseModel):
    questions: List[QuestionResult]
    total_found: int

# ===== /generate-paper Endpoint =====
class PaperBlueprint(BaseModel):
    """TN SSLC paper structure."""
    part_i: dict = Field(default_factory=lambda: {"count": 14, "marks_each": 1})
    part_ii: dict = Field(default_factory=lambda: {
        "prose": {"count": 3, "out_of": 4, "marks_each": 2},
        "poetry": {"count": 3, "out_of": 4, "marks_each": 2},
        "grammar": {"count": 3, "out_of": 5, "marks_each": 2},
        "map": {"count": 1, "marks_each": 2},
    })
    part_iii: dict = Field(default_factory=lambda: {
        "prose_paragraph": {"count": 2, "out_of": 4, "marks_each": 5},
        "poetry": {"count": 2, "out_of": 4, "marks_each": 5},
        "supplementary": {"count": 1, "out_of": 2, "marks_each": 5},
        "writing": {"count": 4, "out_of": 6, "marks_each": 5},
        "memory_poem": {"count": 1, "marks_each": 5},
    })
    part_iv: dict = Field(default_factory=lambda: {
        "question_46": {"marks": 8, "type": "comprehension"},
        "question_47": {"marks": 8, "type": "prose/poem"},
    })

class GeneratePaperRequest(BaseModel):
    year: Optional[int] = None
    difficulty_distribution: Optional[dict] = None  # {"easy": 0.2, "medium": 0.5, "hard": 0.3}

class GeneratePaperResponse(BaseModel):
    paper_id: str
    status: str = "generated"
    questions: List[dict]
    total_marks: int = 100
    estimated_time_minutes: int = 180
    blueprint: PaperBlueprint

# ===== /evaluate-answer Endpoint =====
class EvaluateAnswerRequest(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=500)
    student_answer: str = Field(..., min_length=5, max_length=2000)
    question_id: Optional[str] = None
    expected_answer: Optional[str] = None

class EvaluationFeedback(BaseModel):
    match_percentage: float = Field(..., ge=0, le=100)
    missing_points: List[str]
    extra_points: List[str]
    improvements: str
    evidence_chunks: List[str]

class EvaluateAnswerResponse(BaseModel):
    question: str
    student_answer: str
    official_answer: Optional[str]
    feedback: EvaluationFeedback
    confidence: float = Field(..., ge=0, le=1)

# ===== Error Response =====
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)
