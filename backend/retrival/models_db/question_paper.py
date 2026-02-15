"""
Question Paper Model for ExamSmith.
Defines paper lifecycle, status transitions, and DTOs.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum


class PaperStatus(str, Enum):
    """Question paper lifecycle status."""
    DRAFT = "DRAFT"           # Initial generation
    REVISED = "REVISED"       # After HITL revisions
    APPROVED = "APPROVED"     # Instructor approved
    PUBLISHED = "PUBLISHED"   # Available to students


class QuestionItem(BaseModel):
    """Individual question in a paper (flexible schema)."""
    question_id: Optional[str] = None
    question_number: Optional[Any] = None  # Can be int or str
    question_text: str
    question_type: Optional[str] = None  # Flexible type
    marks: Optional[int] = None
    options: Optional[List[str]] = None  # For MCQ
    answer_key: Optional[str] = None
    correct_option: Optional[str] = None  # For MCQ answers
    brief_answer_guide: Optional[str] = None  # For descriptive answers
    lesson_name: Optional[str] = None
    unit_name: Optional[str] = None
    lesson_type: Optional[str] = None
    part: Optional[str] = None  # Part I, II, III, IV
    section: Optional[str] = None
    internal_choice: Optional[bool] = None
    
    class Config:
        extra = "allow"  # Allow additional fields from generator


# ===== Database Model =====
class QuestionPaper(BaseModel):
    """Question paper document schema for MongoDB."""
    paper_id: str = Field(..., description="Unique paper identifier")
    title: str = Field(default="TN SSLC English Model Paper")
    book_id: Optional[str] = None  # Reference to source book
    status: PaperStatus = Field(default=PaperStatus.DRAFT)
    questions: List[Dict[str, Any]] = Field(default_factory=list)  # Flexible question structure
    answer_key: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Tracking
    created_by: str = Field(..., description="User ID of creator (instructor)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Revision tracking
    revised_by: List[Dict[str, Any]] = Field(default_factory=list)  # [{user_id, revised_at, feedback}]
    
    # Approval tracking
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    
    # Publishing
    published_by: Optional[str] = None
    published_at: Optional[datetime] = None
    
    # Metadata
    total_marks: int = 100
    duration_minutes: int = 180
    difficulty_distribution: Optional[Dict[str, float]] = None
    coverage_validation: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


# ===== Request DTOs =====
class QuestionPaperCreate(BaseModel):
    """Request model for generating a new paper."""
    book_id: Optional[str] = None
    difficulty_distribution: Optional[Dict[str, float]] = None


class QuestionPaperUpdate(BaseModel):
    """Request model for updating paper details."""
    title: Optional[str] = None
    questions: Optional[List[QuestionItem]] = None


class RevisionEntry(BaseModel):
    """Revision history entry."""
    question_id: str
    old_text: str
    new_text: str
    revised_at: datetime
    revised_by: str
    feedback: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request to approve a paper."""
    comments: Optional[str] = None


class PublishRequest(BaseModel):
    """Request to publish a paper to the pipeline."""
    notes: Optional[str] = None


# ===== Response DTOs =====
class QuestionPaperResponse(BaseModel):
    """Response model for question paper."""
    paper_id: str
    title: str
    status: PaperStatus
    questions: List[Dict[str, Any]]  # Flexible structure to handle various question formats
    created_by: str
    created_at: datetime
    total_marks: int
    duration_minutes: int
    
    # Only include if approved/published
    approved_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class QuestionPaperListResponse(BaseModel):
    """Response model for paper list."""
    papers: List[QuestionPaperResponse]
    total: int
    page: int = 1
    page_size: int = 10
