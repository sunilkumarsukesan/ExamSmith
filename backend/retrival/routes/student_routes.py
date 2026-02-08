"""
Student Routes for ExamSmith.
Handles exam pipeline, exam taking, and submissions.
STUDENT (or higher) role required for all endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import uuid
import logging
import sys
import json
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models_db.question_paper import PaperStatus, QuestionPaperResponse
from models_db.attempt import Attempt, AttemptCreate, AttemptSubmit, AttemptResponse, AttemptAnswer
from models_db.evaluation import (
    Evaluation, EvaluationResponse, EvaluationSummary,
    MCQEvaluation, DescriptiveEvaluation, SemanticDetails
)
from auth.dependencies import require_role, TokenPayload
from mongo.client import mongo_client
from config import settings
from services.response_formatter import format_chat_response

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/student", tags=["Student"])

# Any authenticated user can access student routes
require_student = require_role(["ADMIN", "INSTRUCTOR", "STUDENT"])


# ===== Helper Functions =====

def get_pipeline_collection():
    """Get pipeline collection for published papers (visible to students)."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_pipeline_db', '10_english')
    coll_name = getattr(settings, 'mongodb_pipeline_collection', 'generatedQuestionPapers')
    return mongo_client.client[db_name][coll_name]


def get_attempts_collection():
    """Get attempts collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    coll_name = getattr(settings, 'mongodb_attempts_collection', 'student_attempts')
    return mongo_client.client[db_name][coll_name]


def get_evaluations_collection():
    """Get evaluations collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    coll_name = getattr(settings, 'mongodb_evaluations_collection', 'evaluations')
    return mongo_client.client[db_name][coll_name]


def get_users_collection():
    """Get users collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["users"]


# ===== Pipeline Papers (Published) =====

@router.get("/pipeline-papers")
async def get_pipeline_papers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: TokenPayload = Depends(require_student)
):
    """
    Get all PUBLISHED papers available for students from the pipeline.
    
    This reads from the generatedQuestionPapers collection in 10_english database.
    Only papers that instructors have approved and published are visible here.
    """
    try:
        pipeline_coll = get_pipeline_collection()
        attempts_coll = get_attempts_collection()
        
        # Only active papers
        query = {"is_active": True}
        
        # Count total
        total = pipeline_coll.count_documents(query)
        
        # Fetch papers (without answer keys for students)
        cursor = pipeline_coll.find(query).skip(skip).limit(limit).sort("published_at", -1)
        
        papers = []
        for doc in cursor:
            paper_id = doc["paper_id"]
            
            # Check if student already attempted this paper
            existing_attempt = attempts_coll.find_one({
                "student_id": current_user.user_id,
                "paper_id": paper_id,
                "status": {"$in": ["submitted", "evaluated"]}
            })
            
            papers.append({
                "paper_id": paper_id,
                "title": doc.get("title", "TN SSLC English Model Paper"),
                "description": doc.get("description"),
                "book_name": doc.get("book_name"),
                "total_marks": doc.get("total_marks", 100),
                "total_questions": doc.get("total_questions", 0),
                "duration_minutes": doc.get("duration_minutes"),  # None = unlimited
                "published_at": doc.get("published_at"),
                "published_by_name": doc.get("published_by_name"),
                "already_attempted": existing_attempt is not None,
                "attempt_status": existing_attempt.get("status") if existing_attempt else None
            })
        
        return {
            "papers": papers,
            "total": total,
            "page": (skip // limit) + 1,
            "page_size": limit
        }
        
    except Exception as e:
        logger.error(f"Get pipeline papers failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get papers")


@router.get("/papers/{paper_id}")
async def get_paper_for_exam(
    paper_id: str,
    current_user: TokenPayload = Depends(require_student)
):
    """
    Get a paper for taking an exam.
    
    Returns questions WITHOUT answer keys.
    Only active published papers from pipeline are accessible.
    """
    try:
        pipeline_coll = get_pipeline_collection()
        
        doc = pipeline_coll.find_one({
            "paper_id": paper_id,
            "is_active": True
        })
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found or not available"
            )
        
        # Remove answer keys from questions for student view
        questions = []
        for q in doc.get("questions", []):
            # Handle options based on question type
            options = q.get("options")
            q_type = q.get("question_type")
            
            # For internal choice questions, keep options as objects (they contain sub-questions)
            if q.get("internal_choice") or q_type == "INTERNAL_CHOICE":
                # Keep options as-is for internal choice (array of dicts with question_text)
                pass
            elif options and isinstance(options, list):
                # For regular MCQ, ensure options are strings
                string_options = []
                for opt in options:
                    if isinstance(opt, dict):
                        # Extract text from object
                        string_options.append(opt.get("option_text", opt.get("question_text", opt.get("text", str(opt)))))
                    elif isinstance(opt, str):
                        string_options.append(opt)
                    else:
                        string_options.append(str(opt))
                options = string_options
            
            q_copy = {
                "question_id": q.get("question_id"),
                "question_number": q.get("question_number"),
                "question_type": q_type,
                "question_text": q.get("question_text"),
                "marks": q.get("marks", 1),
                "options": options,
                "internal_choice": q.get("internal_choice", False),
                "source_unit": q.get("source_unit"),
                "difficulty": q.get("difficulty")
            }
            # Do NOT include: correct_option, answer_key
            questions.append(q_copy)
        
        return {
            "paper_id": doc["paper_id"],
            "title": doc.get("title", "TN SSLC English Model Paper"),
            "description": doc.get("description"),
            "instructions": doc.get("instructions"),
            "total_marks": doc.get("total_marks", 100),
            "total_questions": doc.get("total_questions", len(questions)),
            "duration_minutes": doc.get("duration_minutes"),  # None = unlimited
            "questions": questions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get paper for exam failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get paper")


# ===== Exam Attempts =====

@router.post("/start-exam", response_model=AttemptResponse)
async def start_exam(
    request: AttemptCreate,
    current_user: TokenPayload = Depends(require_student)
):
    """
    Start a new exam attempt.
    
    Creates an attempt record and returns the attempt ID.
    Note: No re-attempts allowed - once submitted, student cannot retake.
    """
    try:
        pipeline_coll = get_pipeline_collection()
        attempts_coll = get_attempts_collection()
        users_coll = get_users_collection()
        
        # Verify paper exists and is active in pipeline
        paper = pipeline_coll.find_one({
            "paper_id": request.paper_id,
            "is_active": True
        })
        
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found or not available"
            )
        
        # Check if student already submitted this paper (NO RE-ATTEMPTS)
        already_submitted = attempts_coll.find_one({
            "student_id": current_user.user_id,
            "paper_id": request.paper_id,
            "status": {"$in": ["submitted", "evaluated"]}
        })
        
        if already_submitted:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already attempted this exam. Re-attempts are not allowed."
            )
        
        # Check if student has an in-progress attempt
        existing = attempts_coll.find_one({
            "student_id": current_user.user_id,
            "paper_id": request.paper_id,
            "status": "in_progress"
        })
        
        if existing:
            # Return existing in-progress attempt
            return AttemptResponse(
                attempt_id=existing["attempt_id"],
                student_id=existing["student_id"],
                paper_id=existing["paper_id"],
                paper_title=existing.get("paper_title"),
                status=existing["status"],
                started_at=existing["started_at"]
            )
        
        # Get student info
        student = users_coll.find_one({"user_id": current_user.user_id})
        student_name = student.get("name", "Unknown") if student else "Unknown"
        student_email = student.get("email", "") if student else ""
        
        # Create new attempt
        attempt = Attempt(
            attempt_id=str(uuid.uuid4()),
            student_id=current_user.user_id,
            student_name=student_name,
            student_email=student_email,
            paper_id=request.paper_id,
            paper_title=paper.get("title"),
            started_at=datetime.utcnow(),
            status="in_progress"
        )
        
        attempts_coll.insert_one(attempt.model_dump())
        
        logger.info(f"Student {current_user.email} started exam: {request.paper_id}")
        
        return AttemptResponse(
            attempt_id=attempt.attempt_id,
            student_id=attempt.student_id,
            paper_id=attempt.paper_id,
            paper_title=attempt.paper_title,
            status=attempt.status,
            started_at=attempt.started_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start exam failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start exam")


@router.post("/submit-paper")
async def submit_paper(
    attempt_id: str,
    request: AttemptSubmit,
    current_user: TokenPayload = Depends(require_student)
):
    """
    Submit exam answers.
    
    Stores answers and triggers evaluation.
    Once submitted, cannot be changed or retaken.
    """
    try:
        attempts_coll = get_attempts_collection()
        
        # Find attempt
        attempt = attempts_coll.find_one({
            "attempt_id": attempt_id,
            "student_id": current_user.user_id
        })
        
        if not attempt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attempt not found"
            )
        
        if attempt["status"] == "submitted" or attempt["status"] == "evaluated":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Exam already submitted. Re-attempts are not allowed."
            )
        
        # Calculate time taken
        started_at = attempt["started_at"]
        submitted_at = datetime.utcnow()
        time_taken = int((submitted_at - started_at).total_seconds())
        
        # Update attempt with answers
        attempts_coll.update_one(
            {"attempt_id": attempt_id},
            {
                "$set": {
                    "answers": [a.model_dump() for a in request.answers],
                    "status": "submitted",
                    "submitted_at": submitted_at,
                    "time_taken_seconds": time_taken
                }
            }
        )
        
        logger.info(f"Student {current_user.email} submitted exam: {attempt_id}")
        
        # Trigger evaluation
        evaluation_result = await evaluate_attempt(
            attempt_id, 
            attempt["paper_id"],
            current_user.user_id,
            request.answers
        )
        
        return {
            "message": "Exam submitted successfully",
            "attempt_id": attempt_id,
            "submitted_at": submitted_at.isoformat(),
            "time_taken_seconds": time_taken,
            "evaluation_id": evaluation_result.get("evaluation_id")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit exam")


async def evaluate_attempt(
    attempt_id: str,
    paper_id: str,
    student_id: str,
    answers: List[AttemptAnswer]
) -> dict:
    """
    Evaluate student answers.
    
    MCQ: Exact match with answer key
    Descriptive: Semantic evaluation using embeddings
    
    Final Score = Score from answer key match + Score from textbook match
    """
    try:
        pipeline_coll = get_pipeline_collection()
        evaluations_coll = get_evaluations_collection()
        
        # Get paper with answer keys from pipeline
        paper = pipeline_coll.find_one({"paper_id": paper_id})
        if not paper:
            return {"error": "Paper not found"}
        
        # Build answer key lookup from pipeline questions
        answer_key_map = {}
        for q in paper.get("questions", []):
            q_id = q.get("question_id") or str(q.get("question_number"))
            answer_key_map[q_id] = {
                "answer": q.get("answer_key", ""),
                "correct_option": q.get("correct_option"),
                "marks": q.get("marks", 1),
                "type": q.get("question_type", "SHORT_ANSWER"),
                "question_text": q.get("question_text", ""),
                "options": q.get("options", [])
            }
        
        # Evaluate each answer
        mcq_evaluations = []
        descriptive_evaluations = []
        mcq_score = 0.0
        mcq_total = 0.0
        descriptive_score = 0.0
        descriptive_total = 0.0
        
        for ans in answers:
            q_id = ans.question_id
            key_info = answer_key_map.get(q_id, {})
            correct_answer = key_info.get("answer", "")
            correct_option = key_info.get("correct_option")
            marks = key_info.get("marks", 1)
            q_type = key_info.get("type", "SHORT_ANSWER")
            options = key_info.get("options", [])
            
            if q_type == "MCQ":
                # MCQ: Check if selected option matches correct option
                student_option = ans.student_answer.strip()
                
                # Handle both index-based and text-based answers
                if correct_option is not None:
                    # Compare option index
                    try:
                        is_correct = int(student_option) == correct_option
                    except ValueError:
                        # Compare option text
                        is_correct = student_option.upper() == str(correct_answer).upper()
                else:
                    is_correct = student_option.upper() == str(correct_answer).upper()
                
                marks_awarded = marks if is_correct else 0
                mcq_score += marks_awarded
                mcq_total += marks
                
                # Get correct answer text for display
                correct_answer_text = correct_answer
                if correct_option is not None and options:
                    correct_answer_text = options[correct_option] if correct_option < len(options) else correct_answer
                
                mcq_evaluations.append(MCQEvaluation(
                    question_id=q_id,
                    question_number=str(ans.question_number),
                    student_answer=ans.student_answer,
                    correct_answer=correct_answer_text,
                    is_correct=is_correct,
                    marks_awarded=marks_awarded,
                    marks_possible=marks
                ))
            else:
                # Descriptive: Semantic evaluation
                # TODO: Call embeddings API for semantic scoring
                # For now, using keyword matching as placeholder
                
                student_text = ans.student_answer.strip().lower()
                expected_text = str(correct_answer).lower()
                
                # Simple keyword matching (placeholder for semantic)
                if not student_text:
                    score = 0.0
                    feedback = "No answer provided"
                elif len(student_text) < 10:
                    score = 0.1
                    feedback = "Answer too brief. Please provide more detail."
                else:
                    # Check for keyword overlap
                    expected_words = set(expected_text.split())
                    student_words = set(student_text.split())
                    common = expected_words.intersection(student_words)
                    
                    if len(expected_words) > 0:
                        keyword_score = len(common) / len(expected_words)
                    else:
                        keyword_score = 0.5  # No answer key, give partial credit
                    
                    # Length-based component
                    length_score = min(1.0, len(student_text) / max(len(expected_text), 50))
                    
                    # Combined score: 50% keyword match + 50% length/effort
                    score = 0.5 * keyword_score + 0.5 * length_score
                    score = min(1.0, max(0.1, score))  # Clamp between 0.1 and 1.0
                    
                    if score >= 0.8:
                        feedback = "Excellent answer with good coverage of key concepts."
                    elif score >= 0.6:
                        feedback = "Good answer. Consider including more specific details."
                    elif score >= 0.4:
                        feedback = "Partial answer. Review the expected concepts."
                    else:
                        feedback = "Answer needs improvement. Review the topic thoroughly."
                
                marks_awarded = score * marks
                descriptive_score += marks_awarded
                descriptive_total += marks
                
                descriptive_evaluations.append(DescriptiveEvaluation(
                    question_id=q_id,
                    question_number=str(ans.question_number),
                    student_answer=ans.student_answer,
                    expected_answer=correct_answer,
                    answer_key_similarity=score,
                    textbook_similarity=score,  # TODO: Implement textbook semantic search
                    final_score=score,
                    feedback=feedback,
                    marks_awarded=round(marks_awarded, 2),
                    marks_possible=marks
                ))
        
        # Calculate final score
        final_score = mcq_score + descriptive_score
        total_marks = mcq_total + descriptive_total
        percentage = (final_score / total_marks * 100) if total_marks > 0 else 0
        
        # Create evaluation record
        evaluation = Evaluation(
            evaluation_id=str(uuid.uuid4()),
            attempt_id=attempt_id,
            student_id=student_id,
            paper_id=paper_id,
            mcq_score=mcq_score,
            mcq_total=mcq_total,
            descriptive_score=descriptive_score,
            descriptive_total=descriptive_total,
            final_score=final_score,
            total_marks=total_marks,
            percentage=round(percentage, 2),
            mcq_evaluations=mcq_evaluations,
            descriptive_evaluations=descriptive_evaluations,
            semantic_details=SemanticDetails(
                evaluation_method="hybrid"
            ),
            evaluated_at=datetime.utcnow()
        )
        
        evaluations_coll.insert_one(evaluation.model_dump())
        
        # Update attempt status
        attempts_coll = get_attempts_collection()
        attempts_coll.update_one(
            {"attempt_id": attempt_id},
            {"$set": {"status": "evaluated"}}
        )
        
        return {"evaluation_id": evaluation.evaluation_id}
        
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        return {"error": str(e)}


# ===== View Results =====

@router.get("/my-attempts")
async def get_my_attempts(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: TokenPayload = Depends(require_student)
):
    """
    Get all exam attempts for the current student.
    """
    try:
        attempts_coll = get_attempts_collection()
        
        query = {"student_id": current_user.user_id}
        if status_filter:
            query["status"] = status_filter
        
        cursor = attempts_coll.find(query).sort("started_at", -1)
        
        attempts = []
        for doc in cursor:
            attempts.append({
                "attempt_id": doc["attempt_id"],
                "paper_id": doc["paper_id"],
                "paper_title": doc.get("paper_title"),
                "status": doc["status"],
                "started_at": doc["started_at"],
                "submitted_at": doc.get("submitted_at"),
                "time_taken_seconds": doc.get("time_taken_seconds")
            })
        
        return {"attempts": attempts, "total": len(attempts)}
        
    except Exception as e:
        logger.error(f"Get attempts failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get attempts")


@router.get("/results/{attempt_id}")
async def get_result(
    attempt_id: str,
    current_user: TokenPayload = Depends(require_student)
):
    """
    Get detailed evaluation results for a specific attempt.
    
    Returns: Score + correct answers + student answers compared
    """
    try:
        evaluations_coll = get_evaluations_collection()
        attempts_coll = get_attempts_collection()
        pipeline_coll = get_pipeline_collection()
        
        # Get evaluation
        evaluation = evaluations_coll.find_one({
            "attempt_id": attempt_id,
            "student_id": current_user.user_id
        })
        
        if not evaluation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Evaluation not found"
            )
        
        # Get attempt for additional context
        attempt = attempts_coll.find_one({"attempt_id": attempt_id})
        
        # Get paper for question texts
        paper = pipeline_coll.find_one({"paper_id": evaluation["paper_id"]})
        
        # Build detailed comparison
        question_results = []
        
        # Add MCQ results
        for mcq in evaluation.get("mcq_evaluations", []):
            q_text = ""
            options = []
            if paper:
                for q in paper.get("questions", []):
                    if q.get("question_id") == mcq["question_id"]:
                        q_text = q.get("question_text", "")
                        options = q.get("options", [])
                        break
            
            question_results.append({
                "question_id": mcq["question_id"],
                "question_number": mcq["question_number"],
                "question_type": "MCQ",
                "question_text": q_text,
                "options": options,
                "student_answer": mcq["student_answer"],
                "correct_answer": mcq["correct_answer"],
                "is_correct": mcq["is_correct"],
                "marks_awarded": mcq["marks_awarded"],
                "marks_possible": mcq["marks_possible"],
                "feedback": "Correct!" if mcq["is_correct"] else "Incorrect"
            })
        
        # Add descriptive results
        for desc in evaluation.get("descriptive_evaluations", []):
            q_text = ""
            if paper:
                for q in paper.get("questions", []):
                    if q.get("question_id") == desc["question_id"]:
                        q_text = q.get("question_text", "")
                        break
            
            question_results.append({
                "question_id": desc["question_id"],
                "question_number": desc["question_number"],
                "question_type": "DESCRIPTIVE",
                "question_text": q_text,
                "student_answer": desc["student_answer"],
                "correct_answer": desc.get("expected_answer", ""),
                "score_percentage": round(desc["final_score"] * 100, 1),
                "marks_awarded": desc["marks_awarded"],
                "marks_possible": desc["marks_possible"],
                "feedback": desc.get("feedback", ""),
                "answer_key_similarity": round(desc.get("answer_key_similarity", 0) * 100, 1),
                "textbook_similarity": round(desc.get("textbook_similarity", 0) * 100, 1)
            })
        
        # Sort by question number
        question_results.sort(key=lambda x: int(x["question_number"]) if x["question_number"].isdigit() else 0)
        
        return {
            "evaluation_id": evaluation["evaluation_id"],
            "attempt_id": evaluation["attempt_id"],
            "paper_id": evaluation["paper_id"],
            "paper_title": attempt.get("paper_title") if attempt else None,
            
            # Summary scores
            "summary": {
                "mcq_score": evaluation["mcq_score"],
                "mcq_total": evaluation["mcq_total"],
                "descriptive_score": round(evaluation["descriptive_score"], 2),
                "descriptive_total": evaluation["descriptive_total"],
                "final_score": round(evaluation["final_score"], 2),
                "total_marks": evaluation["total_marks"],
                "percentage": round(evaluation["percentage"], 1)
            },
            
            # Timing
            "started_at": attempt.get("started_at") if attempt else None,
            "submitted_at": attempt.get("submitted_at") if attempt else None,
            "time_taken_seconds": attempt.get("time_taken_seconds") if attempt else None,
            "evaluated_at": evaluation["evaluated_at"],
            
            # Detailed question-by-question comparison
            "question_results": question_results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get result failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get result")


@router.get("/my-results")
async def get_my_results(
    current_user: TokenPayload = Depends(require_student)
):
    """
    Get summary of all evaluation results for current student.
    """
    try:
        evaluations_coll = get_evaluations_collection()
        
        cursor = evaluations_coll.find({
            "student_id": current_user.user_id
        }).sort("evaluated_at", -1)
        
        results = []
        for doc in cursor:
            results.append(EvaluationSummary(
                evaluation_id=doc["evaluation_id"],
                attempt_id=doc["attempt_id"],
                paper_id=doc["paper_id"],
                final_score=doc["final_score"],
                total_marks=doc["total_marks"],
                percentage=doc["percentage"],
                evaluated_at=doc["evaluated_at"]
            ))
        
        return {"results": results, "total": len(results)}
        
    except Exception as e:
        logger.error(f"Get my results failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get results")


# ===== Chat Learning Assistant (Students & Admins only) =====

from models import ChatRequest, ChatResponse, ChatQuotaResponse, SelectedQuestion
import json
import asyncio

# Role restriction for chat - Students and Admins only (NOT instructors)
require_chat_access = require_role(["ADMIN", "STUDENT"])

CHAT_DAILY_LIMIT = 20


def get_chat_sessions_collection():
    """Get chat sessions collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return mongo_client.chat_sessions_collection


def get_chat_messages_collection():
    """Get chat messages collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    return mongo_client.chat_messages_collection


def build_chat_context(selected_questions: List[dict], textbook_content: List[str]) -> str:
    """Build context from selected questions and textbook content."""
    context_parts = []
    
    if selected_questions:
        context_parts.append("=== QUESTIONS THE STUDENT IS ASKING ABOUT ===")
        for q in selected_questions:
            context_parts.append(f"\nQuestion {q.get('question_number', '?')}: {q.get('question_text', '')}")
            if q.get('student_answer'):
                context_parts.append(f"Student's Answer: {q['student_answer']}")
            if q.get('correct_answer'):
                context_parts.append(f"Correct Answer: {q['correct_answer']}")
            if q.get('is_correct') is not None:
                context_parts.append(f"Was Correct: {'Yes' if q['is_correct'] else 'No'}")
    
    if textbook_content:
        context_parts.append("\n\n=== RELEVANT TEXTBOOK CONTENT ===")
        for i, content in enumerate(textbook_content, 1):
            context_parts.append(f"\n[Source {i}]: {content}")
    
    return "\n".join(context_parts)


def build_chat_prompt(query: str, context: str, chat_history: List[dict]) -> str:
    """Build the chat prompt for the LLM."""
    
    # Check if this is a vocabulary question
    is_vocabulary_question = any(word in query.lower() for word in 
        ['vocabulary', 'vocab', 'exercise', 'construct meaningful sentences', 
         'coward', 'gradual', 'praise', 'courageous', 'starvation', 'unit 1', 'exercise e'])
    
    # Check if this is a speech writing question
    is_speech_writing_question = any(word in query.lower() for word in
        ['write a speech', 'speech', 'exercise m', 'literary association', 
         'school celebration', 'given lead', 'speech writing'])
    
    history_text = ""
    if chat_history:
        history_text = "\n=== PREVIOUS CONVERSATION ===\n"
        for msg in chat_history[-6:]:  # Last 6 messages for context
            role = "Student" if msg.get("role") == "user" else "Tutor"
            history_text += f"{role}: {msg.get('content', '')}\n"
    
    # Special instruction for vocabulary questions
    vocabulary_instruction = ""
    if is_vocabulary_question:
        vocabulary_instruction = """
SPECIAL INSTRUCTION FOR VOCABULARY EXERCISE QUESTIONS:
- If the student is asking about vocabulary exercises (like "E. Use the following words..."), provide DIRECT ANSWERS with:
  1. The specific vocabulary words with their definitions
  2. Meaningful example sentences for each word
  3. Context from the lesson where applicable
  4. Clear structure with one word per section
- DO NOT provide generic tips on how to construct sentences unless specifically asked
- ALWAYS provide the actual words and definitions being requested
- Use the vocabulary context provided to give lesson-specific examples

"""
    
    # Special instruction for speech writing questions
    speech_instruction = ""
    if is_speech_writing_question:
        speech_instruction = """
SPECIAL INSTRUCTION FOR SPEECH WRITING EXERCISE QUESTIONS:
- If the student is asking about speech writing exercise (Exercise M), provide:
  1. The EXACT "given lead" that they should base their speech on
  2. The exercise requirements and word count
  3. A clear breakdown of what should be in introduction, body, and conclusion
  4. Guidelines for effective speech writing with examples
  5. Tips for connecting to literary themes from Unit 1
- DO NOT provide generic speech-writing tips without first presenting the exercise details
- ALWAYS clearly highlight the "given lead" that the student must use
- Provide the specific prompt/lead from the textbook (e.g., "The joy of reading literature")
- Structure the response to help students understand what they need to do

"""
    
    prompt = f"""You are a friendly and encouraging English tutor for TN SSLC (10th Standard) students. Your role is to help students understand their exam answers and learn from their mistakes in a warm, supportive way.

PERSONALITY & TONE:
- Be warm, friendly, and encouraging like a helpful older sibling or favorite teacher
- Celebrate correct answers with enthusiasm
- Frame mistakes as learning opportunities, not failures
- Use encouraging phrases like "Great question!", "You're on the right track!", "Don't worry, this is a common confusion"
- Keep explanations conversational yet educational

EMOJI GUIDELINES (IMPORTANT - Use emojis throughout your response):
- 📚 For section headers and main topics
- 💡 For key concepts, ideas, or "aha moments"
- ✅ For correct answers or things to remember
- ❌ For common mistakes to avoid
- ⭐ For important points or tips
- 📝 For definitions or notes
- ✏️ For examples
- 🎯 For learning goals or objectives
- 💪 For encouragement
- 🤔 For thinking prompts or questions
- 🎭 For poetry and literary content
- ✍️ For grammar rules
- 📖 For textbook references
- 🔍 For analysis and deeper understanding
- 👉 For step-by-step instructions

RESPONSE STRUCTURE:
1. Start with a brief, friendly acknowledgment (1 sentence with emoji)
2. Provide the main explanation with clear sections
3. Include practical examples where helpful
4. End with encouragement or a helpful tip

FORMAT REQUIREMENTS:
- Use emojis at the start of each major section or point
- Use bullet points (• or -) for lists of concepts
- Use numbered steps (1. 2. 3.) for sequential explanations
- Keep paragraphs short (2-3 sentences each)
- Add line breaks between sections for readability
- Bold key terms using **term**
- For definitions: "📝 **Term** – Definition"
- For key points: "⭐ **Remember:** point"

CONTENT GUIDELINES:
1. If the student got an answer wrong, explain WHY gently and how to remember the correct answer
2. Use the textbook content provided for accurate, curriculum-aligned explanations
3. For poems or prose, explain meaning, themes, and literary devices
4. Make explanations clear and suitable for 10th standard students
5. If you don't have enough context, ask a clarifying question
6. Relate back to the TN SSLC English syllabus when relevant

{vocabulary_instruction}{speech_instruction}

TEXTBOOK CONTEXT AND VOCABULARY DATA:
{context}

{history_text}

STUDENT'S QUESTION: {query}

Provide a helpful, engaging response with emojis that makes learning enjoyable. Remember - you're not just teaching, you're inspiring! 💪"""
    
    return prompt


@router.get("/chat/quota")
async def get_chat_quota(
    current_user: TokenPayload = Depends(require_chat_access)
):
    """
    Get remaining chat quota for today.
    Only available to Students and Admins.
    """
    remaining = mongo_client.get_remaining_quota(current_user.user_id, CHAT_DAILY_LIMIT)
    today = datetime.now().strftime("%Y-%m-%d")
    
    return ChatQuotaResponse(
        remaining=remaining,
        limit=CHAT_DAILY_LIMIT,
        reset_date=today
    )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: TokenPayload = Depends(require_chat_access)
):
    """
    Streaming chat endpoint for student learning assistant.
    Uses Server-Sent Events for real-time token streaming.
    Only available to Students and Admins (NOT instructors).
    """
    from sse_starlette.sse import EventSourceResponse
    
    # Check rate limit
    allowed, remaining = mongo_client.check_and_increment_quota(
        current_user.user_id, CHAT_DAILY_LIMIT
    )
    
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "rate_limit_exceeded",
                "message": f"Daily chat limit of {CHAT_DAILY_LIMIT} reached. Try again tomorrow.",
                "remaining": 0,
                "reset_date": datetime.now().strftime("%Y-%m-%d")
            }
        )
    
    async def generate_stream():
        try:
            logger.info(f"Chat stream started for user: {current_user.user_id}")
            from langchain_groq import ChatGroq
            from retriever.concept_explanation import ConceptExplanationRetriever
            
            # Create or continue session
            session_id = request.session_id or str(uuid.uuid4())
            
            # Send session metadata first
            yield {
                "event": "meta",
                "data": json.dumps({"session_id": session_id, "remaining_quota": remaining}),
            }
            
            # Extract unit filters from selected questions
            unit_filters = set()
            for q in request.selected_questions:
                if q.source_unit:
                    unit_filters.add(q.source_unit)
                if q.unit_name:
                    unit_filters.add(q.unit_name)
            
            # Retrieve textbook content based on query and unit context
            textbook_content = []
            citations = []
            
            try:
                retriever = ConceptExplanationRetriever()
                
                # Build search query including question context
                search_query = request.query
                if request.selected_questions:
                    q_texts = [q.question_text for q in request.selected_questions if q.question_text]
                    if q_texts:
                        search_query = f"{request.query} {' '.join(q_texts[:2])}"
                
                # Check if this is a vocabulary question
                is_vocab_query = any(word in request.query.lower() for word in 
                    ['vocabulary', 'vocab', 'exercise', 'construct meaningful sentences', 
                     'coward', 'gradual', 'praise', 'courageous', 'starvation'])
                
                # Apply unit filter if we have specific units
                filters = {"metadata.lang": "en"} if not is_vocab_query else {}
                if unit_filters and not is_vocab_query:
                    # Try to extract numeric unit
                    for uf in unit_filters:
                        try:
                            if isinstance(uf, str) and uf.lower().startswith("unit"):
                                unit_num = int(uf.lower().replace("unit", "").strip())
                                filters["metadata.unit"] = unit_num
                                break
                            elif isinstance(uf, int):
                                filters["metadata.unit"] = uf
                                break
                        except:
                            pass
                
                context_blocks, citations = await retriever.retrieve(
                    query=search_query,
                    vector_weight=0.5,
                    bm25_weight=0.5,
                    top_k=5 if not is_vocab_query else 10,  # Get more results for vocab
                    filters=filters
                )
                textbook_content = context_blocks
                
            except Exception as e:
                logger.warning(f"Textbook retrieval failed: {e}")
            
            # Build context and prompt
            selected_q_dicts = [q.model_dump() for q in request.selected_questions]
            context = build_chat_context(selected_q_dicts, textbook_content)
            chat_history = [msg.model_dump() for msg in request.chat_history]
            prompt = build_chat_prompt(request.query, context, chat_history)
            
            # Stream using LangChain + Groq with astream
            llm = ChatGroq(
                api_key=settings.groq_api_key,
                model=settings.groq_model,
                temperature=0.7,
                max_tokens=1024,
                streaming=True
            )
            
            full_response = ""
            
            # Stream tokens as they arrive using astream
            async for chunk in llm.astream(prompt):
                token = chunk.content if hasattr(chunk, 'content') else str(chunk)
                if token:
                    full_response += token
                    yield {
                        "event": "token",
                        "data": json.dumps({"token": token}),
                    }
            
            # Save to chat history
            try:
                sessions_coll = get_chat_sessions_collection()
                messages_coll = get_chat_messages_collection()
                
                # Upsert session
                sessions_coll.update_one(
                    {"session_id": session_id},
                    {
                        "$set": {
                            "user_id": current_user.user_id,
                            "updated_at": datetime.utcnow(),
                            "selected_questions": selected_q_dicts
                        },
                        "$setOnInsert": {
                            "created_at": datetime.utcnow(),
                            "title": request.query[:50] + "..." if len(request.query) > 50 else request.query
                        }
                    },
                    upsert=True
                )
                
                # Save messages
                messages_coll.insert_many([
                    {
                        "message_id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "user_id": current_user.user_id,
                        "role": "user",
                        "content": request.query,
                        "created_at": datetime.utcnow()
                    },
                    {
                        "message_id": str(uuid.uuid4()),
                        "session_id": session_id,
                        "user_id": current_user.user_id,
                        "role": "assistant",
                        "content": full_response,
                        "created_at": datetime.utcnow(),
                        "sources": [{"chunk_id": str(c.chunk_id), "lesson_name": c.lesson_name} for c in citations]
                    }
                ])
            except Exception as e:
                logger.error(f"Failed to save chat history: {e}")
            
            # Send done event with sources
            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "sources": [
                            {"chunk_id": str(c.chunk_id), "lesson_name": c.lesson_name}
                            for c in citations
                        ],
                        "remaining_quota": remaining,
                    }
                ),
            }
            
        except Exception as e:
            logger.error(f"Chat stream error: {str(e)}")
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }
    
    return EventSourceResponse(generate_stream())


@router.get("/chat/sessions")
async def get_chat_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    current_user: TokenPayload = Depends(require_chat_access)
):
    """
    Get chat sessions for current user.
    """
    try:
        sessions_coll = get_chat_sessions_collection()
        
        cursor = sessions_coll.find({
            "user_id": current_user.user_id
        }).sort("updated_at", -1).skip(skip).limit(limit)
        
        sessions = []
        for doc in cursor:
            sessions.append({
                "session_id": doc["session_id"],
                "title": doc.get("title", "Chat"),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at")
            })
        
        total = sessions_coll.count_documents({"user_id": current_user.user_id})
        
        return {"sessions": sessions, "total": total}
        
    except Exception as e:
        logger.error(f"Get chat sessions failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat sessions")


@router.get("/chat/sessions/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    current_user: TokenPayload = Depends(require_chat_access)
):
    """
    Get messages for a specific chat session.
    """
    try:
        sessions_coll = get_chat_sessions_collection()
        messages_coll = get_chat_messages_collection()
        
        # Verify session belongs to user
        session = sessions_coll.find_one({
            "session_id": session_id,
            "user_id": current_user.user_id
        })
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        cursor = messages_coll.find({
            "session_id": session_id
        }).sort("created_at", 1)
        
        messages = []
        for doc in cursor:
            messages.append({
                "message_id": doc["message_id"],
                "role": doc["role"],
                "content": doc["content"],
                "created_at": doc.get("created_at"),
                "sources": doc.get("sources", [])
            })
        
        return {
            "session_id": session_id,
            "title": session.get("title"),
            "selected_questions": session.get("selected_questions", []),
            "messages": messages
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get session messages failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to get messages")
