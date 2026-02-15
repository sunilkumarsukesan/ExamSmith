"""
Instructor Routes for ExamSmith.
Handles question paper management, approval, and publishing.
INSTRUCTOR or ADMIN role required for all endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Optional, List
from datetime import datetime
import uuid
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models_db.question_paper import (
    QuestionPaper, QuestionPaperResponse, QuestionPaperListResponse,
    PaperStatus, ApprovalRequest, PublishRequest, RevisionEntry
)
from auth.dependencies import require_role, TokenPayload
from mongo.client import mongo_client
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/instructor", tags=["Instructor"])

# Instructor or Admin required
require_instructor = require_role(["ADMIN", "INSTRUCTOR"])


# ===== Helper Functions =====

def get_papers_collection():
    """Get question papers collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["question_papers"]


def get_revisions_collection():
    """Get revisions collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["revisions"]


def get_pipeline_collection():
    """Get pipeline collection for published papers (visible to students)."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_pipeline_db', '10_english')
    coll_name = getattr(settings, 'mongodb_pipeline_collection', 'generatedQuestionPapers')
    return mongo_client.client[db_name][coll_name]


def get_users_collection():
    """Get users collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["users"]


def paper_to_response(doc: dict) -> QuestionPaperResponse:
    """Convert MongoDB document to response model."""
    return QuestionPaperResponse(
        paper_id=doc["paper_id"],
        title=doc.get("title", "TN SSLC English Model Paper"),
        status=doc.get("status", PaperStatus.DRAFT.value),
        questions=doc.get("questions", []),
        created_by=doc["created_by"],
        created_at=doc["created_at"],
        total_marks=doc.get("total_marks", 100),
        duration_minutes=doc.get("duration_minutes", 180),
        approved_at=doc.get("approved_at"),
        published_at=doc.get("published_at")
    )


# ===== View Books =====

@router.get("/books")
async def get_available_books(
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Get list of available books for paper generation.
    
    **Instructor/Admin only**
    """
    try:
        # Get books from the textbook collection info
        return {
            "books": [
                {
                    "book_id": "tn_10th_english",
                    "title": "TN SSLC 10th Standard English",
                    "collection": settings.mongodb_collection_textbook,
                    "database": settings.mongodb_db_textbook
                }
            ],
            "message": "Books available for paper generation"
        }
    except Exception as e:
        logger.error(f"Get books failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get books")


# ===== Question Paper Management =====

@router.get("/papers", response_model=QuestionPaperListResponse)
async def list_papers(
    status_filter: Optional[PaperStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    List question papers (optionally filtered by status).
    
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        
        # Build query
        query = {}
        if status_filter:
            query["status"] = status_filter.value
        
        # Count total
        total = collection.count_documents(query)
        
        # Fetch papers
        cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        papers = [paper_to_response(doc) for doc in cursor]
        
        return QuestionPaperListResponse(
            papers=papers,
            total=total,
            page=(skip // limit) + 1,
            page_size=limit
        )
        
    except Exception as e:
        logger.error(f"List papers failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list papers")


@router.get("/papers/{paper_id}", response_model=QuestionPaperResponse)
async def get_paper(
    paper_id: str,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Get a specific question paper by ID.
    
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        doc = collection.find_one({"paper_id": paper_id})
        
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )
        
        return paper_to_response(doc)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get paper")


@router.post("/save-paper", response_model=QuestionPaperResponse, status_code=status.HTTP_201_CREATED)
async def save_generated_paper(
    paper_data: dict,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Save a generated paper from the existing /generate-paper API.
    
    This endpoint stores the paper with lifecycle tracking.
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        
        # Generate paper ID if not present
        paper_id = paper_data.get("paper_id", str(uuid.uuid4()))
        
        # Create paper document
        paper = QuestionPaper(
            paper_id=paper_id,
            title=paper_data.get("title", "TN SSLC English Model Paper"),
            status=PaperStatus.DRAFT,
            questions=paper_data.get("questions", []),
            answer_key=paper_data.get("answer_key", []),
            created_by=current_user.user_id,
            created_at=datetime.utcnow(),
            total_marks=paper_data.get("total_marks", 100),
            duration_minutes=paper_data.get("estimated_time_minutes", 180),
            coverage_validation=paper_data.get("coverage_validation")
        )
        
        collection.insert_one(paper.model_dump())
        
        logger.info(f"Instructor {current_user.email} saved paper: {paper_id}")
        
        return paper_to_response(paper.model_dump())
        
    except Exception as e:
        logger.error(f"Save paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save paper")


# ===== Question Revision (HITL) =====

@router.put("/revise-question/{paper_id}")
async def revise_question(
    paper_id: str,
    question_id: str,
    old_text: str,
    new_text: str,
    feedback: Optional[str] = None,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Record a question revision (Human-in-the-Loop).
    
    This tracks revision history and updates paper status.
    **Instructor/Admin only**
    
    Note: The actual revision via AI is handled by the existing /revise-question endpoint.
    This endpoint tracks the revision for audit purposes.
    """
    try:
        papers_coll = get_papers_collection()
        revisions_coll = get_revisions_collection()
        
        # Find paper
        paper = papers_coll.find_one({"paper_id": paper_id})
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )
        
        # Create revision entry
        revision = RevisionEntry(
            question_id=question_id,
            old_text=old_text,
            new_text=new_text,
            revised_at=datetime.utcnow(),
            revised_by=current_user.user_id,
            feedback=feedback
        )
        
        # Store revision
        revisions_coll.insert_one({
            "paper_id": paper_id,
            **revision.model_dump()
        })
        
        # Update paper status and add to revised_by
        papers_coll.update_one(
            {"paper_id": paper_id},
            {
                "$set": {"status": PaperStatus.REVISED.value},
                "$push": {
                    "revised_by": {
                        "user_id": current_user.user_id,
                        "revised_at": datetime.utcnow(),
                        "feedback": feedback
                    }
                }
            }
        )
        
        logger.info(f"Instructor {current_user.email} revised question in paper: {paper_id}")
        
        return {
            "message": "Revision recorded",
            "paper_id": paper_id,
            "question_id": question_id,
            "new_status": PaperStatus.REVISED.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Revise question failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record revision")


@router.get("/revision-history/{paper_id}")
async def get_revision_history(
    paper_id: str,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Get revision history for a paper.
    
    **Instructor/Admin only**
    """
    try:
        revisions_coll = get_revisions_collection()
        
        cursor = revisions_coll.find({"paper_id": paper_id}).sort("revised_at", -1)
        
        revisions = []
        for doc in cursor:
            doc.pop("_id", None)
            revisions.append(doc)
        
        return {"paper_id": paper_id, "revisions": revisions}
        
    except Exception as e:
        logger.error(f"Get revision history failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get revision history")


# ===== Approval & Publishing =====

@router.post("/approve-paper/{paper_id}")
async def approve_paper(
    paper_id: str,
    request: ApprovalRequest = None,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Approve a paper (moves from DRAFT/REVISED to APPROVED).
    
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        
        # Find paper
        paper = collection.find_one({"paper_id": paper_id})
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )
        
        # Check current status
        current_status = paper.get("status", PaperStatus.DRAFT.value)
        if current_status == PaperStatus.PUBLISHED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot approve a published paper"
            )
        
        # Update to APPROVED
        collection.update_one(
            {"paper_id": paper_id},
            {
                "$set": {
                    "status": PaperStatus.APPROVED.value,
                    "approved_by": current_user.user_id,
                    "approved_at": datetime.utcnow(),
                    "approval_comments": request.comments if request else None
                }
            }
        )
        
        logger.info(f"Instructor {current_user.email} approved paper: {paper_id}")
        
        return {
            "message": "Paper approved",
            "paper_id": paper_id,
            "status": PaperStatus.APPROVED.value,
            "approved_at": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Approve paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve paper")


@router.post("/publish-to-pipeline/{paper_id}")
async def publish_paper(
    paper_id: str,
    request: PublishRequest = None,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Publish an approved paper to the student pipeline.
    
    Only APPROVED papers can be published.
    Published papers are copied to the generatedQuestionPapers collection
    and become visible to students.
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        pipeline_coll = get_pipeline_collection()
        users_coll = get_users_collection()
        
        # Find paper
        paper = collection.find_one({"paper_id": paper_id})
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )
        
        # Check current status - only APPROVED can be published
        current_status = paper.get("status", PaperStatus.DRAFT.value)
        if current_status != PaperStatus.APPROVED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only APPROVED papers can be published. Current status: {current_status}"
            )
        
        # Check if already exists in pipeline
        existing = pipeline_coll.find_one({"paper_id": paper_id})
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Paper already exists in pipeline"
            )
        
        # Get instructor name
        instructor = users_coll.find_one({"user_id": current_user.user_id})
        instructor_name = instructor.get("name", "Unknown") if instructor else "Unknown"
        
        # Prepare questions for pipeline (include answer keys for evaluation)
        pipeline_questions = []
        for idx, q in enumerate(paper.get("questions", [])):
            # Check if this is an internal choice question
            internal_choice = q.get("internal_choice", False)
            
            # Determine question type
            if internal_choice:
                # Internal choice questions are rendered specially
                q_type = "INTERNAL_CHOICE"
            elif q.get("options") and isinstance(q.get("options", [None])[0], str):
                # Has string options = MCQ
                q_type = "MCQ"
            elif q.get("part") == "I":
                q_type = "MCQ"
            elif q.get("lesson_type") == "memory":
                q_type = "MEMORY"
            elif q.get("marks", 1) >= 5:
                q_type = "LONG_ANSWER"
            else:
                q_type = "SHORT_ANSWER"
            
            # For internal choice, keep options as-is (they contain full sub-questions)
            # For MCQ, ensure options are strings
            options = q.get("options")
            if not internal_choice and options and isinstance(options, list):
                # Convert to strings for regular MCQ
                options = [str(opt) if not isinstance(opt, dict) else opt.get("text", str(opt)) for opt in options]
            
            pipeline_q = {
                "question_id": q.get("question_id", f"q_{idx+1}"),
                "question_number": q.get("question_number", idx + 1),
                "question_type": q_type,
                "question_text": q.get("question_text", "Choose one of the following:" if internal_choice else ""),
                "marks": q.get("marks", 1),
                "options": options,
                "correct_option": q.get("correct_option"),
                "answer_key": q.get("brief_answer_guide", q.get("answer_key", "")),
                "source_unit": q.get("unit_name", q.get("unit")),
                "source_topic": q.get("lesson_type", q.get("topic")),
                "part": q.get("part"),
                "section": q.get("section"),
                "internal_choice": internal_choice,
                "difficulty": q.get("difficulty"),
                "bloom_level": q.get("bloom_level")
            }
            pipeline_questions.append(pipeline_q)
        
        # Use the paper's total_marks (should be 100 as per TN SSLC pattern)
        # Don't recalculate - the original paper already has correct total
        total_marks = paper.get("total_marks", 100)
        
        # Create pipeline paper document
        pipeline_paper = {
            "paper_id": paper_id,
            "title": paper.get("title", "TN SSLC English Model Paper"),
            "description": paper.get("description", "Generated model question paper"),
            "book_id": paper.get("book_id", "tn_10th_english"),
            "book_name": paper.get("book_name", "TN SSLC 10th Standard English"),
            "questions": pipeline_questions,
            "total_marks": total_marks,
            "total_questions": len(pipeline_questions),
            "duration_minutes": paper.get("duration_minutes"),  # None = unlimited
            "instructions": paper.get("instructions", "Answer all questions. Read each question carefully."),
            "published_by": current_user.user_id,
            "published_by_name": instructor_name,
            "published_at": datetime.utcnow(),
            "is_active": True,
            "created_at": paper.get("created_at", datetime.utcnow()),
            "original_paper_id": paper_id
        }
        
        # Insert into pipeline collection
        pipeline_coll.insert_one(pipeline_paper)
        
        # Update original paper status
        collection.update_one(
            {"paper_id": paper_id},
            {
                "$set": {
                    "status": PaperStatus.PUBLISHED.value,
                    "published_by": current_user.user_id,
                    "published_at": datetime.utcnow(),
                    "publish_notes": request.notes if request else None
                }
            }
        )
        
        logger.info(f"Instructor {current_user.email} published paper: {paper_id} to pipeline")
        
        return {
            "message": "Paper published to student pipeline",
            "paper_id": paper_id,
            "status": PaperStatus.PUBLISHED.value,
            "published_at": datetime.utcnow().isoformat(),
            "pipeline_db": settings.mongodb_pipeline_db,
            "pipeline_collection": settings.mongodb_pipeline_collection
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Publish paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to publish paper")


@router.post("/unpublish/{paper_id}")
async def unpublish_paper(
    paper_id: str,
    current_user: TokenPayload = Depends(require_instructor)
):
    """
    Unpublish a paper (moves back to APPROVED and removes from pipeline).
    
    **Instructor/Admin only**
    """
    try:
        collection = get_papers_collection()
        pipeline_coll = get_pipeline_collection()
        
        # Find paper
        paper = collection.find_one({"paper_id": paper_id})
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found"
            )
        
        # Check current status
        if paper.get("status") != PaperStatus.PUBLISHED.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PUBLISHED papers can be unpublished"
            )
        
        # Remove from pipeline collection
        pipeline_coll.delete_one({"paper_id": paper_id})
        
        # Move back to APPROVED
        collection.update_one(
            {"paper_id": paper_id},
            {
                "$set": {"status": PaperStatus.APPROVED.value},
                "$unset": {"published_by": "", "published_at": "", "publish_notes": ""}
            }
        )
        
        logger.info(f"Instructor {current_user.email} unpublished paper: {paper_id}")
        
        return {
            "message": "Paper unpublished and removed from pipeline",
            "paper_id": paper_id,
            "status": PaperStatus.APPROVED.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unpublish paper failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unpublish paper")
