"""Utility functions for the retrieval backend."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def format_citations(citations: List[Dict[str, Any]]) -> str:
    """Format citations for human-readable output."""
    formatted = []
    for citation in citations:
        if citation.get("source") == "textbook":
            formatted.append(
                f"📖 {citation.get('lesson_name', 'Unknown')} "
                f"(Page {citation.get('page', 'N/A')})"
            )
        elif citation.get("source") == "question_paper":
            formatted.append(
                f"📝 Question {citation.get('question_number', 'N/A')} "
                f"({citation.get('year', 'N/A')})"
            )
    return "\n".join(formatted)

def truncate_text(text: str, max_chars: int = 500) -> str:
    """Truncate text to maximum characters."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

def normalize_question_number(question_num: Any) -> str:
    """Normalize question number to string."""
    return str(question_num).strip()

def extract_marks_from_metadata(metadata: Dict) -> int:
    """Extract marks from question metadata."""
    return metadata.get("marks", 0)

def estimate_answer_time(marks: int) -> int:
    """Estimate time needed to answer based on marks."""
    # Rough estimate: 1 minute per mark + buffer
    return marks + 2

def validate_embedding_dimension(embedding: List[float], expected_dim: int = 1024) -> bool:
    """Validate embedding vector dimension."""
    return len(embedding) == expected_dim if embedding else False

def merge_context_blocks(blocks: List[str], separator: str = "\n\n") -> str:
    """Merge multiple context blocks into single string."""
    return separator.join([b.strip() for b in blocks if b.strip()])

def extract_question_metadata(question_doc: Dict) -> Dict[str, Any]:
    """Extract relevant question metadata."""
    question = question_doc.get("question", {})
    metadata = question_doc.get("metadata", {})
    
    return {
        "number": question.get("number"),
        "type": question.get("type"),
        "marks": metadata.get("marks"),
        "difficulty": metadata.get("difficulty"),
        "part": metadata.get("part"),
        "section": metadata.get("section"),
        "year": metadata.get("year"),
    }

def build_paper_structure() -> Dict[str, Any]:
    """Build the TN SSLC paper structure template."""
    return {
        "part_i": {
            "name": "Objective Type",
            "count": 14,
            "marks_each": 1,
            "total": 14,
            "description": "Multiple Choice Questions (14 × 1 = 14 marks)"
        },
        "part_ii": {
            "name": "Short Answer",
            "total": 20,
            "sections": {
                "prose": {"count": 3, "out_of": 4, "marks_each": 2, "total": 6},
                "poetry": {"count": 3, "out_of": 4, "marks_each": 2, "total": 6},
                "grammar": {"count": 3, "out_of": 5, "marks_each": 2, "total": 6},
                "map": {"count": 1, "marks_each": 2, "total": 2},
            }
        },
        "part_iii": {
            "name": "Long Answer",
            "total": 50,
            "sections": {
                "prose_paragraph": {"count": 2, "out_of": 4, "marks_each": 5, "total": 10},
                "poetry": {"count": 2, "out_of": 4, "marks_each": 5, "total": 10},
                "supplementary": {"count": 1, "out_of": 2, "marks_each": 5, "total": 5},
                "writing": {"count": 4, "out_of": 6, "marks_each": 5, "total": 20},
                "memory_poem": {"count": 1, "marks_each": 5, "total": 5},
            }
        },
        "part_iv": {
            "name": "Comprehension",
            "total": 16,
            "questions": {
                "question_46": {"marks": 8, "type": "comprehension"},
                "question_47": {"marks": 8, "type": "prose/poem"},
            }
        }
    }

def validate_paper_structure(questions: List[Dict]) -> bool:
    """Validate that questions match TN SSLC paper structure."""
    # Count questions by part
    part_i_count = len([q for q in questions if q.get("section") == "part_i"])
    
    # Part I should have exactly 14 MCQs
    if part_i_count != 14:
        logger.warning(f"Part I count mismatch: expected 14, got {part_i_count}")
        return False
    
    return True
