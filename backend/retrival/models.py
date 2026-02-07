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
    blueprint: PaperBlueprint = Field(default_factory=PaperBlueprint)
    coverage_validation: Optional[dict] = None

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

# ===== Quality Review Models =====
class ReviewQuestionInput(BaseModel):
    """Input model for questions to be reviewed by quality reviewer."""
    question_number: int = 0
    part: str = ""
    section: str = ""
    question_text: str = ""
    marks: int = 0
    internal_choice: bool = False
    unit_name: str = ""
    lesson_type: str = ""
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    poem_name: Optional[str] = None
    story_name: Optional[str] = None
    grammar_area: Optional[str] = None
    choice_group: Optional[str] = None
    lesson_number: Optional[int] = None

class ReviewPaperRequest(BaseModel):
    """Request model for /review-paper endpoint."""
    questions: List[ReviewQuestionInput]

class ReviewPaperResponse(BaseModel):
    """Response model for /review-paper endpoint."""
    request_id: str
    status: str = "reviewed"
    questions: List[dict]
    review_report: dict

# ===== Error Response =====
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ===== Question Revision (Human-in-the-Loop) =====
class ReviseQuestionRequest(BaseModel):
    """Request model for question revision"""
    original_question: dict
    teacher_feedback: str = Field(..., min_length=5, max_length=1000)
    paper_id: str


class ReviseQuestionResponse(BaseModel):
    """Response model for question revision"""
    success: bool
    revised_question: dict
    message: str


class RegenerateAllRequest(BaseModel):
    """Request model for regenerating all questions"""
    paper_id: str
    questions: List[dict]
    teacher_feedback: str = Field(..., min_length=5, max_length=1000)


class RegenerateAllResponse(BaseModel):
    """Response model for regenerating all questions"""
    success: bool
    questions: List[dict]
    message: str


class RevisionHistoryResponse(BaseModel):
    """Response model for revision history"""
    paper_id: str
    revisions: List[dict]
    total_revisions: int


# ===== Chat Models (Student Learning Assistant) =====
class ChatMessage(BaseModel):
    """Individual chat message"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SelectedQuestion(BaseModel):
    """Question selected by student for chat context"""
    question_number: int
    question_text: str
    student_answer: Optional[str] = None
    correct_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    source_unit: Optional[str] = None
    unit_name: Optional[str] = None
    lesson_type: Optional[str] = None


class ChatRequest(BaseModel):
    """Request model for student chat"""
    query: str = Field(..., min_length=1, max_length=2000)
    selected_questions: List[SelectedQuestion] = Field(default_factory=list)
    session_id: Optional[str] = None  # For continuing existing session
    chat_history: List[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Response model for student chat (non-streaming)"""
    session_id: str
    message: str
    sources: List[Citation] = Field(default_factory=list)
    remaining_quota: int
    

class ChatSession(BaseModel):
    """Chat session for persistence"""
    session_id: str
    user_id: str
    title: Optional[str] = None
    selected_questions: List[SelectedQuestion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    

class ChatQuotaResponse(BaseModel):
    """Response for quota check"""
    remaining: int
    limit: int
    reset_date: str
