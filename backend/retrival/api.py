from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from models import (
    AskRequest, AskResponse,
    SimilarQuestionsRequest, SimilarQuestionsResponse,
    GeneratePaperRequest, GeneratePaperResponse, PaperBlueprint,
    EvaluateAnswerRequest, EvaluateAnswerResponse,
    ReviseQuestionRequest, ReviseQuestionResponse,
    RegenerateAllRequest, RegenerateAllResponse,
    RevisionHistoryResponse
)
from retriever.concept_explanation import ConceptExplanationRetriever
from retriever.question_similarity import QuestionSimilarityRetriever
from retriever.paper_generation import PaperGenerationRetriever
from retriever.answer_evaluation import AnswerEvaluationRetriever
from retriever.question_reviser import get_question_reviser
from llm.factory import get_llm
from observability import track_retrieval, metrics
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# ===== /ask Endpoint =====
@router.post("/ask", response_model=AskResponse)
@track_retrieval("concept_explanation")
async def ask(request: AskRequest) -> AskResponse:
    """
    Student doubts and concept explanations using hybrid search on textbook.
    """
    try:
        # Retrieve relevant context
        retriever = ConceptExplanationRetriever()
        context_blocks, citations = await retriever.retrieve(
            query=request.question,
            vector_weight=request.hybrid_search.vector_weight,
            bm25_weight=request.hybrid_search.bm25_weight,
            top_k=request.hybrid_search.top_k
        )
        
        if not context_blocks:
            return AskResponse(
                answer="No relevant content found in the textbook.",
                sources=[],
                context_preview="",
                retrieval_mode="concept_explanation"
            )
        
        # Generate answer using Groq
        context_text = "\n\n".join(context_blocks)
        prompt = f"""You are an English teacher for TN SSLC (10th Standard).
A student has asked the following question:

STUDENT QUESTION:
{request.question}

RELEVANT TEXTBOOK CONTENT:
{context_text}

Provide a clear, concise explanation using ONLY the provided textbook content.
Do not hallucinate or add information outside the textbook.
Answer in a way that a 10th standard student can understand."""

        llm = get_llm()
        answer = await llm.generate(prompt, max_tokens=512, temperature=0.7)
        
        return AskResponse(
            answer=answer,
            sources=citations,
            context_preview=context_text[:200],
            retrieval_mode="concept_explanation"
        )
    
    except Exception as e:
        logger.error(f"Ask endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== /similar-questions Endpoint =====
@router.post("/similar-questions", response_model=SimilarQuestionsResponse)
@track_retrieval("question_similarity")
async def similar_questions(request: SimilarQuestionsRequest) -> SimilarQuestionsResponse:
    """
    Find similar exam questions from question paper collection.
    """
    try:
        retriever = QuestionSimilarityRetriever()
        context_blocks, citations = await retriever.retrieve(
            query=request.question_text,
            top_k=request.top_k,
            difficulty=request.difficulty
        )
        
        if not context_blocks:
            return SimilarQuestionsResponse(questions=[], total_found=0)
        
        # Build question results
        questions = []
        for i, (block, citation) in enumerate(zip(context_blocks, citations)):
            from mongo.client import mongo_client
            qp_collection = mongo_client.questionpapers_collection
            
            # Fetch full question details
            doc = qp_collection.find_one({"_id": citation.chunk_id})
            if doc:
                question = doc.get("question", {})
                questions.append({
                    "question_number": citation.question_number,
                    "question_text": block,
                    "question_type": question.get("type", "unknown"),
                    "answer_key": question.get("answer", {}).get("text"),
                    "marks": doc.get("metadata", {}).get("marks"),
                    "year": citation.year,
                    "similarity_score": 0.85 - (i * 0.05),  # Mock scores
                    "choices": question.get("choices")
                })
        
        return SimilarQuestionsResponse(questions=questions, total_found=len(questions))
    
    except Exception as e:
        logger.error(f"Similar questions endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== /generate-paper Endpoint =====
@router.post("/generate-paper", response_model=GeneratePaperResponse)
@track_retrieval("paper_generation")
async def generate_paper(request: GeneratePaperRequest) -> GeneratePaperResponse:
    """
    Generate a TN SSLC model question paper with ORIGINAL questions.
    
    Uses LLM-based question generation with paraphrased context.
    Enforces coverage rules and returns complete paper in JSON format.
    """
    try:
        paper_id = str(uuid.uuid4())
        retriever = PaperGenerationRetriever()
        
        logger.info(f"Paper generation request received (ID: {paper_id})")
        
        # Call the new generation method
        paper = await retriever.generate_complete_paper()
        
        # Extract questions for response
        all_questions = []
        
        # Collect questions from all parts
        for part_key, part_data in paper.get("parts", {}).items():
            if "questions" in part_data:
                all_questions.extend(part_data["questions"])
            elif "sections" in part_data:
                for section_key, section_data in part_data["sections"].items():
                    if "questions" in section_data:
                        all_questions.extend(section_data["questions"])
        
        logger.info(f"Paper generation complete: {len(all_questions)} questions")
        
        # Log sample question for debugging
        if all_questions:
            logger.info(f"Sample question structure: {all_questions[0]}")
        
        # Build response with proper Pydantic model
        response = GeneratePaperResponse(
            paper_id=paper_id,
            status="generated",
            questions=all_questions,
            total_marks=100,
            estimated_time_minutes=180,
            blueprint=PaperBlueprint(),  # Use Pydantic model with defaults
            coverage_validation=paper.get("coverage_validation") or {}
        )
        
        logger.info(f"Response questions count: {len(response.questions)}")
        return response
    
    except Exception as e:
        logger.error(f"Generate paper endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== /evaluate-answer Endpoint =====
@router.post("/evaluate-answer", response_model=EvaluateAnswerResponse)
@track_retrieval("answer_evaluation")
async def evaluate_answer(request: EvaluateAnswerRequest) -> EvaluateAnswerResponse:
    """
    Evaluate a student's answer against official answer key.
    """
    try:
        # Retrieve official answer and evidence
        retriever = AnswerEvaluationRetriever()
        context_blocks, citations = await retriever.retrieve(
            question_id=request.question_id,
            question_text=request.question_text
        )
        
        if not context_blocks:
            raise HTTPException(status_code=404, detail="Question not found")
        
        official_answer = context_blocks[0] if context_blocks else ""
        evidence_chunks = context_blocks[1:] if len(context_blocks) > 1 else []
        
        # Use Groq to evaluate
        llm = get_llm()
        evaluation = await llm.evaluate_answer(
            official_answer=official_answer,
            student_answer=request.student_answer,
            evidence_chunks=evidence_chunks
        )
        
        from models import EvaluationFeedback
        feedback = EvaluationFeedback(
            match_percentage=evaluation.get("match_percentage", 0),
            missing_points=evaluation.get("missing_points", []),
            extra_points=evaluation.get("extra_points", []),
            improvements=evaluation.get("improvements", ""),
            evidence_chunks=evidence_chunks[:3]  # Top 3 evidence chunks
        )
        
        return EvaluateAnswerResponse(
            question=request.question_text,
            student_answer=request.student_answer,
            official_answer=official_answer,
            feedback=feedback,
            confidence=min(0.95, max(0.5, evaluation.get("match_percentage", 0) / 100))
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluate answer endpoint failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== /review-paper Endpoint =====
@router.post("/review-paper")
async def review_paper(request: dict):
    """
    Apply quality review fixes to a generated question paper.
    
    Applies TN Board alignment rules:
    1. MCQ Quality Rules (proper distractors)
    2. Grammar Ambiguity Elimination
    3. Retrieval De-dependency Reduction
    4. Writing Skills Context Simplification
    5. Structure Validation
    
    Request body:
    - questions: List of question objects to review
    
    Returns:
    - Fixed questions with review report
    """
    request_id = str(uuid.uuid4())
    logger.info(f"Quality review request received (ID: {request_id})")
    
    try:
        questions_data = request.get("questions", [])
        if not questions_data:
            raise HTTPException(
                status_code=400,
                detail="No questions provided for review"
            )
        
        # Convert to ReviewQuestionInput objects
        from models import ReviewQuestionInput
        questions = []
        for q in questions_data:
            questions.append(ReviewQuestionInput(
                question_number=q.get("question_number", 0),
                part=q.get("part", ""),
                section=q.get("section", ""),
                question_text=q.get("question_text", ""),
                marks=q.get("marks", 0),
                internal_choice=q.get("internal_choice", False),
                unit_name=q.get("unit_name", ""),
                lesson_type=q.get("lesson_type", ""),
                options=q.get("options"),
                correct_answer=q.get("correct_answer"),
                poem_name=q.get("poem_name"),
                story_name=q.get("story_name"),
                grammar_area=q.get("grammar_area"),
                choice_group=q.get("choice_group"),
                lesson_number=q.get("lesson_number")
            ))
        
        # Apply quality review
        from retriever.quality_reviewer import get_quality_reviewer
        reviewer = get_quality_reviewer()
        fixed_questions, review_report = await reviewer.review_paper(questions)
        
        logger.info(f"Quality review complete: {review_report['total_fixes']} fixes")
        logger.info(f"retrieval.quality_review")
        
        return {
            "request_id": request_id,
            "status": "reviewed",
            "questions": [q.dict() for q in fixed_questions],
            "review_report": review_report
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Quality review failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quality review failed: {str(e)}"
        )


# ===== Metrics Endpoint =====
@router.get("/metrics")
async def get_metrics():
    """Get retrieval performance metrics."""
    return {
        "retrieval_stats": metrics.get_stats(),
        "timestamp": str(__import__("datetime").datetime.utcnow())
    }


# ===== Human-in-the-Loop: Question Revision Endpoints =====

@router.post("/revise-question", response_model=ReviseQuestionResponse)
async def revise_question(request: ReviseQuestionRequest):
    """
    Revise a question based on teacher feedback using RAG.
    
    This endpoint:
    1. Takes the original question and teacher's feedback
    2. Searches textbook for relevant context (semantic search)
    3. Searches question bank for similar questions
    4. Uses LLM to generate a revised question
    """
    try:
        logger.info(f"Revising question {request.original_question.get('question_number')} for paper {request.paper_id}")
        logger.info(f"Teacher feedback: {request.teacher_feedback}")
        
        reviser = get_question_reviser()
        revised_question = await reviser.revise_question(
            original_question=request.original_question,
            teacher_feedback=request.teacher_feedback,
            paper_id=request.paper_id
        )
        
        success = revised_question.get('is_revised', False) and 'revision_error' not in revised_question
        
        return ReviseQuestionResponse(
            success=success,
            revised_question=revised_question,
            message="Question revised successfully" if success else f"Revision failed: {revised_question.get('revision_error', 'Unknown error')}"
        )
        
    except Exception as e:
        logger.error(f"Error revising question: {e}", exc_info=True)
        return ReviseQuestionResponse(
            success=False,
            revised_question=request.original_question,
            message=f"Error revising question: {str(e)}"
        )


@router.get("/revision-history/{paper_id}", response_model=RevisionHistoryResponse)
async def get_revision_history(paper_id: str, question_number: Optional[int] = None):
    """
    Get revision history for a paper or specific question.
    
    Args:
        paper_id: The paper ID
        question_number: Optional question number to filter history
    """
    try:
        reviser = get_question_reviser()
        history = reviser.get_revision_history(paper_id, question_number)
        
        return RevisionHistoryResponse(
            paper_id=paper_id,
            revisions=history,
            total_revisions=len(history)
        )
        
    except Exception as e:
        logger.error(f"Error getting revision history: {e}")
        return RevisionHistoryResponse(
            paper_id=paper_id,
            revisions=[],
            total_revisions=0
        )


@router.post("/regenerate-all", response_model=RegenerateAllResponse)
async def regenerate_all_questions(request: RegenerateAllRequest):
    """
    Regenerate all questions in a paper based on teacher feedback.
    
    This applies the same feedback to all questions and regenerates them.
    Use with caution as it will replace all questions.
    """
    try:
        paper_id = request.paper_id
        questions = request.questions
        teacher_feedback = request.teacher_feedback
        
        if not questions:
            return RegenerateAllResponse(
                success=False,
                questions=[],
                message="No questions provided"
            )
        
        logger.info(f"Regenerating all {len(questions)} questions for paper {paper_id}")
        logger.info(f"Global feedback: {teacher_feedback}")
        
        reviser = get_question_reviser()
        revised_questions = []
        errors = []
        
        for question in questions:
            try:
                revised = await reviser.revise_question(
                    original_question=question,
                    teacher_feedback=teacher_feedback,
                    paper_id=paper_id
                )
                revised_questions.append(revised)
            except Exception as e:
                logger.error(f"Error revising question {question.get('question_number')}: {e}")
                errors.append(f"Q{question.get('question_number')}: {str(e)}")
                revised_questions.append(question)  # Keep original on error
        
        success = len(errors) == 0
        message = f"Regenerated {len(revised_questions)} questions" if success else f"Regenerated with {len(errors)} errors: {', '.join(errors[:3])}"
        
        return RegenerateAllResponse(
            success=success,
            questions=revised_questions,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Error regenerating all questions: {e}", exc_info=True)
        return RegenerateAllResponse(
            success=False,
            questions=request.questions,
            message=str(e)
        )

