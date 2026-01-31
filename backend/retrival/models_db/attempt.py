"""
Attempt Model for ExamSmith.
Tracks student exam submissions.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class AttemptAnswer(BaseModel):
    """Individual answer in an attempt."""
    question_id: str
    question_number: int
    question_type: str  # Accept any string for flexibility
    student_answer: str  # For MCQ, this is the selected option index as string
    time_spent_seconds: Optional[int] = None


class AttemptStatus(str):
    """Attempt status values."""
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    EVALUATED = "evaluated"


# ===== Database Model =====
class Attempt(BaseModel):
    """Student attempt document schema for MongoDB."""
    attempt_id: str = Field(..., description="Unique attempt identifier")
    student_id: str = Field(..., description="User ID of student")
    student_name: Optional[str] = Field(default=None, description="Student name")
    student_email: Optional[str] = Field(default=None, description="Student email")
    paper_id: str = Field(..., description="Question paper ID")
    paper_title: Optional[str] = Field(default=None, description="Paper title for reference")
    
    answers: List[AttemptAnswer] = Field(default_factory=list)
    
    # Timing
    started_at: datetime = Field(default_factory=datetime.utcnow)
    submitted_at: Optional[datetime] = None
    time_taken_seconds: Optional[int] = None
    
    # Status
    status: Literal["in_progress", "submitted", "evaluated"] = "in_progress"
    
    class Config:
        use_enum_values = True


# ===== Request DTOs =====
class AttemptCreate(BaseModel):
    """Request to start an exam attempt."""
    paper_id: str


class AttemptSubmit(BaseModel):
    """Request to submit an attempt."""
    answers: List[AttemptAnswer]


# ===== Response DTOs =====
class AttemptResponse(BaseModel):
    """Response model for attempt."""
    attempt_id: str
    student_id: str
    paper_id: str
    paper_title: Optional[str] = None
    status: str
    started_at: datetime
    submitted_at: Optional[datetime] = None


class AttemptListResponse(BaseModel):
    """List item for student's attempts."""
    attempt_id: str
    paper_id: str
    paper_title: Optional[str]
    status: str
    started_at: datetime
    submitted_at: Optional[datetime]
    score: Optional[float] = None
    total_marks: Optional[int] = None
