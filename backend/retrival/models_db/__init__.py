# Models module for ExamSmith
# Contains Pydantic models for database entities

from models_db.user import (
    User, UserCreate, UserUpdate, UserResponse, UserRole, UserStatus,
    LoginRequest, LoginResponse, TokenResponse
)
from models_db.question_paper import (
    QuestionPaper, QuestionPaperCreate, QuestionPaperUpdate,
    QuestionPaperResponse, PaperStatus
)
from models_db.pipeline_paper import (
    PipelinePaper, PipelinePaperCreate, PipelinePaperResponse,
    PipelinePaperDetailResponse, PipelineQuestion, QuestionType
)
from models_db.attempt import (
    Attempt, AttemptCreate, AttemptSubmit, AttemptResponse, 
    AttemptAnswer, AttemptListResponse
)
from models_db.evaluation import (
    Evaluation, EvaluationResponse, EvaluationSummary,
    MCQEvaluation, DescriptiveEvaluation
)

__all__ = [
    # User models
    "User", "UserCreate", "UserUpdate", "UserResponse", 
    "UserRole", "UserStatus", "LoginRequest", "LoginResponse", "TokenResponse",
    # Question paper models
    "QuestionPaper", "QuestionPaperCreate", "QuestionPaperUpdate",
    "QuestionPaperResponse", "PaperStatus",
    # Pipeline paper models
    "PipelinePaper", "PipelinePaperCreate", "PipelinePaperResponse",
    "PipelinePaperDetailResponse", "PipelineQuestion", "QuestionType",
    # Attempt models
    "Attempt", "AttemptCreate", "AttemptSubmit", "AttemptResponse", 
    "AttemptAnswer", "AttemptListResponse",
    # Evaluation models
    "Evaluation", "EvaluationResponse", "EvaluationSummary",
    "MCQEvaluation", "DescriptiveEvaluation"
]
