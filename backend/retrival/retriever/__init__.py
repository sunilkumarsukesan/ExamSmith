"""
Retriever module for ExamSmith.

Contains specialized retrievers for different query types:
- ConceptExplanationRetriever: Explains concepts using textbook content
- QuestionSimilarityRetriever: Finds similar questions from previous papers
- PaperGenerationRetriever: Generates complete model question papers
- AnswerEvaluationRetriever: Evaluates student answers
- QualityReviewer: Post-processor for TN Board quality fixes
"""

from .base import RetrieverMode
from .concept_explanation import ConceptExplanationRetriever
from .question_similarity import QuestionSimilarityRetriever
from .paper_generation import PaperGenerationRetriever, get_paper_generator
from .answer_evaluation import AnswerEvaluationRetriever
from .coverage_validator import CoverageValidator, get_coverage_validator
from .question_generator import QuestionGenerator, get_question_generator
from .quality_reviewer import QualityReviewer, get_quality_reviewer

__all__ = [
    "RetrieverMode",
    "ConceptExplanationRetriever", 
    "QuestionSimilarityRetriever",
    "PaperGenerationRetriever",
    "get_paper_generator",
    "AnswerEvaluationRetriever",
    "CoverageValidator",
    "get_coverage_validator",
    "QuestionGenerator",
    "get_question_generator",
    "QualityReviewer",
    "get_quality_reviewer"
]
