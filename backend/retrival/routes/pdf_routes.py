"""
PDF Generation Module for ExamSmith.
Generates downloadable question paper PDFs.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Response
from typing import Optional
from datetime import datetime
import io
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models_db.question_paper import PaperStatus
from models_db.user import UserRole
from auth.dependencies import get_current_user, TokenPayload
from mongo.client import mongo_client
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/papers", tags=["PDF"])


# ===== Helper Functions =====

def get_papers_collection():
    """Get question papers collection."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_users_db', 'examsmith')
    return mongo_client.client[db_name]["question_papers"]


def get_pipeline_collection():
    """Get pipeline collection for published papers."""
    if not mongo_client.client:
        raise HTTPException(status_code=503, detail="Database unavailable")
    db_name = getattr(settings, 'mongodb_pipeline_db', '10_english')
    coll_name = getattr(settings, 'mongodb_pipeline_collection', 'generatedQuestionPapers')
    return mongo_client.client[db_name][coll_name]


def generate_text_pdf(
    title: str,
    questions: list,
    include_answers: bool = False,
    total_marks: int = 100,
    duration_minutes: int = 180
) -> bytes:
    """
    Generate a simple text-based PDF for a question paper.
    
    Uses ReportLab for PDF generation.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            alignment=TA_CENTER,
            spaceAfter=20
        )
        
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=20
        )
        
        option_style = ParagraphStyle(
            'Option',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=40,
            spaceAfter=3
        )
        
        part_header_style = ParagraphStyle(
            'PartHeader',
            parent=styles['Heading2'],
            fontSize=13,
            spaceBefore=15,
            spaceAfter=10
        )
        
        elements = []
        
        # Title
        elements.append(Paragraph(title, title_style))
        elements.append(Paragraph(
            f"Total Marks: {total_marks} | Time: {duration_minutes} minutes",
            subtitle_style
        ))
        elements.append(Spacer(1, 0.3*inch))
        
        # Group questions by part
        parts = {}
        for q in questions:
            part = q.get("part", "General")
            if part not in parts:
                parts[part] = []
            parts[part].append(q)
        
        # Generate questions for each part
        for part_name, part_questions in parts.items():
            elements.append(Paragraph(f"<b>{part_name}</b>", part_header_style))
            
            for q in part_questions:
                q_num = q.get("question_number", "")
                q_text = q.get("question_text", "")
                q_marks = q.get("marks", 1)
                q_type = q.get("question_type", "")
                
                # Question text with marks
                question_line = f"<b>{q_num}.</b> {q_text} <i>({q_marks} mark{'s' if q_marks > 1 else ''})</i>"
                elements.append(Paragraph(question_line, question_style))
                
                # MCQ options
                options = q.get("options") or q.get("choices")
                if options and isinstance(options, list):
                    for i, opt in enumerate(options):
                        option_letter = chr(65 + i)  # A, B, C, D
                        elements.append(Paragraph(f"({option_letter}) {opt}", option_style))
                
                # Answer (only for instructors)
                if include_answers:
                    answer = q.get("answer_key", "")
                    if answer:
                        elements.append(Paragraph(
                            f"<font color='green'><b>Answer:</b> {answer}</font>",
                            option_style
                        ))
                
                elements.append(Spacer(1, 0.15*inch))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
        
    except ImportError:
        # Fallback: Generate simple text if ReportLab not available
        logger.warning("ReportLab not installed, generating text file instead")
        return generate_text_file(title, questions, include_answers, total_marks, duration_minutes)


def generate_text_file(
    title: str,
    questions: list,
    include_answers: bool = False,
    total_marks: int = 100,
    duration_minutes: int = 180
) -> bytes:
    """
    Generate a simple text file (fallback if ReportLab not available).
    """
    lines = []
    lines.append("=" * 60)
    lines.append(title.center(60))
    lines.append(f"Total Marks: {total_marks} | Time: {duration_minutes} minutes".center(60))
    lines.append("=" * 60)
    lines.append("")
    
    # Group questions by part
    parts = {}
    for q in questions:
        part = q.get("part", "General")
        if part not in parts:
            parts[part] = []
        parts[part].append(q)
    
    for part_name, part_questions in parts.items():
        lines.append(f"\n{part_name}")
        lines.append("-" * 40)
        
        for q in part_questions:
            q_num = q.get("question_number", "")
            q_text = q.get("question_text", "")
            q_marks = q.get("marks", 1)
            
            lines.append(f"\n{q_num}. {q_text} ({q_marks} mark{'s' if q_marks > 1 else ''})")
            
            # MCQ options
            options = q.get("options") or q.get("choices")
            if options and isinstance(options, list):
                for i, opt in enumerate(options):
                    option_letter = chr(65 + i)
                    lines.append(f"   ({option_letter}) {opt}")
            
            if include_answers:
                answer = q.get("answer_key", "")
                if answer:
                    lines.append(f"   Answer: {answer}")
    
    lines.append("\n" + "=" * 60)
    lines.append("END OF PAPER".center(60))
    lines.append("=" * 60)
    
    return "\n".join(lines).encode('utf-8')


# ===== PDF Download Endpoint =====

@router.get("/{paper_id}/download-pdf")
async def download_paper_pdf(
    paper_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    """
    Download a question paper as PDF.
    
    - **Instructors/Admins**: Get PDF with answer keys (from question_papers collection)
    - **Students**: Get PDF without answer keys (from pipeline collection)
    """
    try:
        papers_collection = get_papers_collection()
        pipeline_collection = get_pipeline_collection()
        
        # Build query based on role
        is_instructor = current_user.role in [UserRole.ADMIN.value, UserRole.INSTRUCTOR.value, "ADMIN", "INSTRUCTOR"]
        
        paper = None
        questions = []
        
        if is_instructor:
            # Instructors: First try question_papers, then pipeline
            paper = papers_collection.find_one({"paper_id": paper_id})
            if paper:
                questions = paper.get("questions", [])
            else:
                # Try pipeline collection
                paper = pipeline_collection.find_one({"paper_id": paper_id})
                if paper:
                    questions = paper.get("questions", [])
        else:
            # Students: Only from pipeline, and only active papers
            paper = pipeline_collection.find_one({
                "paper_id": paper_id,
                "is_active": True
            })
            if paper:
                # Remove answer keys for students
                questions = []
                for q in paper.get("questions", []):
                    q_copy = dict(q)
                    q_copy.pop("answer_key", None)
                    q_copy.pop("correct_option", None)
                    questions.append(q_copy)
        
        if not paper:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paper not found or not accessible"
            )
        
        # Generate PDF
        title = paper.get("title", "TN SSLC English Model Paper")
        total_marks = paper.get("total_marks", 100)
        duration_minutes = paper.get("duration_minutes") or 180
        
        # Include answers only for instructors
        include_answers = is_instructor
        
        try:
            pdf_bytes = generate_text_pdf(
                title=title,
                questions=questions,
                include_answers=include_answers,
                total_marks=total_marks,
                duration_minutes=duration_minutes
            )
            media_type = "application/pdf"
            extension = "pdf"
        except Exception as e:
            logger.warning(f"PDF generation failed, using text fallback: {e}")
            pdf_bytes = generate_text_file(
                title=title,
                questions=questions,
                include_answers=include_answers,
                total_marks=total_marks,
                duration_minutes=duration_minutes
            )
            media_type = "text/plain"
            extension = "txt"
        
        # Generate filename
        safe_title = title.replace(" ", "_").replace("/", "-")[:50]
        filename = f"{safe_title}_{paper_id[:8]}.{extension}"
        
        logger.info(f"User {current_user.email} downloaded paper: {paper_id}")
        
        return Response(
            content=pdf_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"PDF download failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")
