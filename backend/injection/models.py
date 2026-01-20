from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class JobStatus(str, Enum):
    """Job status states (SUGGESTION)"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL_FAILURE = "partial_failure"

class InputDocument(BaseModel):
    """Input JSON schema with validation (SUGGESTION)"""
    content: str = Field(..., min_length=1, max_length=50000)
    embedding: List[float] = Field(default_factory=list)
    is_table: bool = False
    table_json: Optional[Dict[str, Any]] = None
    table_markdown: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    question: Optional[Dict[str, Any]] = None

    class Config:
        extra = 'allow'  # Allow additional fields

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        return v

class MongoDBDocument(BaseModel):
    """MongoDB document schema"""
    content: str
    content_hash: str
    embedding: List[float]
    is_table: bool
    table_json: Optional[Dict[str, Any]] = None
    table_markdown: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

class IngestJobResponse(BaseModel):
    """Job creation response"""
    job_id: str
    status: JobStatus
    created_at: datetime

class JobStatusResponse(BaseModel):
    """Job status response (SUGGESTION)"""
    job_id: str
    status: JobStatus
    total_records: int
    processed_records: int
    failed_records: int
    progress_percent: float
    created_at: datetime
    updated_at: datetime
