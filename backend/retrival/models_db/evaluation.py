"""
Evaluation Model for ExamSmith.
Stores AI-evaluated results for student attempts.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MCQEvaluation(BaseModel):
    """MCQ question evaluation result."""
    question_id: str
    question_number: str
    student_answer: str
    correct_answer: str
    is_correct: bool
    marks_awarded: float
    marks_possible: float


class DescriptiveEvaluation(BaseModel):
    """Descriptive question evaluation result."""
    question_id: str
    question_number: str
    student_answer: str
    expected_answer: Optional[str] = None
    
    # Semantic evaluation scores
    answer_key_similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity to answer key")
    textbook_similarity: float = Field(..., ge=0.0, le=1.0, description="Similarity to textbook content")
    final_score: float = Field(..., ge=0.0, le=1.0, description="Weighted final score")
    
    # Feedback
    feedback: str = ""
    missing_concepts: List[str] = Field(default_factory=list)
    
    # Marks
    marks_awarded: float
    marks_possible: float


class SemanticDetails(BaseModel):
    """Detailed semantic evaluation information."""
    textbook_chunks_used: List[str] = Field(default_factory=list)
    embedding_model: str = "mistral-embed"
    evaluation_method: str = "hybrid"  # hybrid = answer_key + textbook


# ===== Database Model =====
class Evaluation(BaseModel):
    """Evaluation document schema for MongoDB."""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    attempt_id: str = Field(..., description="Reference to attempt")
    student_id: str = Field(..., description="User ID of student")
    paper_id: str = Field(..., description="Question paper ID")
    
    # Scores
    mcq_score: float = Field(0.0, description="Total MCQ marks obtained")
    mcq_total: float = Field(0.0, description="Total MCQ marks possible")
    descriptive_score: float = Field(0.0, description="Total descriptive marks obtained")
    descriptive_total: float = Field(0.0, description="Total descriptive marks possible")
    final_score: float = Field(0.0, description="Overall score obtained")
    total_marks: float = Field(100.0, description="Total marks possible")
    percentage: float = Field(0.0, description="Percentage score")
    
    # Detailed results
    mcq_evaluations: List[MCQEvaluation] = Field(default_factory=list)
    descriptive_evaluations: List[DescriptiveEvaluation] = Field(default_factory=list)
    semantic_details: Optional[SemanticDetails] = None
    
    # Timing
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)
    evaluation_time_ms: Optional[int] = None
    
    class Config:
        use_enum_values = True


# ===== Response DTOs =====
class EvaluationResponse(BaseModel):
    """Response model for evaluation results."""
    evaluation_id: str
    attempt_id: str
    paper_id: str
    
    # Summary
    mcq_score: float
    mcq_total: float
    descriptive_score: float
    descriptive_total: float
    final_score: float
    total_marks: float
    percentage: float
    
    # Detailed (optional, can be heavy)
    mcq_evaluations: List[MCQEvaluation] = []
    descriptive_evaluations: List[DescriptiveEvaluation] = []
    
    evaluated_at: datetime


class EvaluationSummary(BaseModel):
    """Lightweight evaluation summary."""
    evaluation_id: str
    attempt_id: str
    paper_id: str
    final_score: float
    total_marks: float
    percentage: float
    evaluated_at: datetime
