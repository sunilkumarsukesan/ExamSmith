"""
Pipeline Paper Model for ExamSmith.
Represents published question papers that are visible to students.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class QuestionType(str, Enum):
    """Types of questions."""
    MCQ = "MCQ"
    SHORT_ANSWER = "SHORT_ANSWER"
    LONG_ANSWER = "LONG_ANSWER"
    FILL_BLANK = "FILL_BLANK"
    TRUE_FALSE = "TRUE_FALSE"


class PipelineQuestion(BaseModel):
    """A question in a pipeline paper."""
    question_id: str = Field(..., description="Unique question identifier")
    question_number: int = Field(..., description="Question number in paper")
    question_type: QuestionType = Field(..., description="Type of question")
    question_text: str = Field(..., description="The question text")
    marks: int = Field(default=1, description="Marks for this question")
    
    # MCQ specific
    options: Optional[List[str]] = Field(default=None, description="Options for MCQ")
    correct_option: Optional[int] = Field(default=None, description="Index of correct option (0-based)")
    
    # Answer key for evaluation
    answer_key: Optional[str] = Field(default=None, description="Expected answer or key")
    
    # Source reference
    source_unit: Optional[str] = Field(default=None, description="Unit/Chapter reference")
    source_topic: Optional[str] = Field(default=None, description="Topic reference")
    
    # Metadata
    difficulty: Optional[str] = Field(default=None, description="Easy/Medium/Hard")
    bloom_level: Optional[str] = Field(default=None, description="Bloom's taxonomy level")


class PipelinePaper(BaseModel):
    """A published question paper in the pipeline."""
    paper_id: str = Field(..., description="Unique paper identifier")
    title: str = Field(..., description="Paper title")
    description: Optional[str] = Field(default=None, description="Paper description")
    
    # Source information
    book_id: Optional[str] = Field(default=None, description="Source book ID")
    book_name: Optional[str] = Field(default=None, description="Source book name")
    
    # Paper content
    questions: List[PipelineQuestion] = Field(default_factory=list, description="List of questions")
    total_marks: int = Field(default=0, description="Total marks")
    total_questions: int = Field(default=0, description="Total number of questions")
    
    # Exam configuration
    duration_minutes: Optional[int] = Field(default=None, description="Exam duration (None = unlimited)")
    instructions: Optional[str] = Field(default=None, description="Exam instructions")
    
    # Publishing info
    published_by: str = Field(..., description="Instructor user ID who published")
    published_by_name: Optional[str] = Field(default=None, description="Instructor name")
    published_at: datetime = Field(default_factory=datetime.utcnow, description="Publication timestamp")
    
    # Status
    is_active: bool = Field(default=True, description="Whether paper is available for students")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None)

    class Config:
        use_enum_values = True


class PipelinePaperCreate(BaseModel):
    """Request model for creating/publishing a paper to pipeline."""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    book_id: Optional[str] = Field(default=None)
    book_name: Optional[str] = Field(default=None)
    questions: List[Dict[str, Any]] = Field(..., min_length=1)
    duration_minutes: Optional[int] = Field(default=None)
    instructions: Optional[str] = Field(default=None)


class PipelinePaperResponse(BaseModel):
    """Response model for pipeline paper (without answer keys for students)."""
    paper_id: str
    title: str
    description: Optional[str]
    book_name: Optional[str]
    total_marks: int
    total_questions: int
    duration_minutes: Optional[int]
    instructions: Optional[str]
    published_at: datetime
    published_by_name: Optional[str]
    is_active: bool


class PipelinePaperDetailResponse(BaseModel):
    """Detailed response with questions (for taking exam - no answer keys)."""
    paper_id: str
    title: str
    description: Optional[str]
    book_name: Optional[str]
    total_marks: int
    total_questions: int
    duration_minutes: Optional[int]
    instructions: Optional[str]
    published_at: datetime
    questions: List[Dict[str, Any]]  # Questions without answer_key and correct_option
