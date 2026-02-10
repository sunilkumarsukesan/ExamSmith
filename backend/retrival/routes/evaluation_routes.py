"""
Evaluation Routes for Admin Quality Testing.
Provides endpoints to evaluate paper generation and chatbot quality using DeepEval metrics.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
import logging
import json
import os
import re
import asyncio
import httpx
import random
from pathlib import Path

from auth.dependencies import get_current_user, TokenPayload, require_role
from mongo.client import mongo_client
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evaluation", tags=["Quality Evaluation"])
# v2 - fixed MongoDB field mappings

# Only admins can access evaluation endpoints
require_admin = require_role(["ADMIN"])

# DeepEval server URL
DEEPEVAL_URL = os.getenv("DEEPEVAL_URL", "http://localhost:8001")

# Results file path
RESULTS_FILE = Path(__file__).parent.parent.parent.parent / "evaluation_results.json"

# Simple in-memory cache for textbook context (to avoid repeated MongoDB queries)
_textbook_context_cache: Dict[tuple, str] = {}


class ChatbotEvaluationRequest(BaseModel):
    query: str = "Explain the themes in the poem 'Life' by Henry Van Dyke"


def load_evaluation_results() -> Dict:
    """Load evaluation results from file."""
    try:
        if RESULTS_FILE.exists():
            with open(RESULTS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Failed to load evaluation results: {e}")
    return {"paper_evaluations": [], "chatbot_evaluations": []}


def save_evaluation_results(results: Dict):
    """Save evaluation results to file."""
    try:
        with open(RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Evaluation results saved to {RESULTS_FILE}")
    except Exception as e:
        logger.error(f"Failed to save evaluation results: {e}")


async def get_textbook_context_for_unit(unit_number: int, topic: str = None) -> str:
    """Retrieve textbook content from MongoDB (10_books.english) for a specific unit.
    Uses caching to avoid repeated queries for the same unit/topic."""
    cache_key = (unit_number, topic)
    
    # Check cache first
    if cache_key in _textbook_context_cache:
        logger.debug(f"Using cached textbook context for Unit {unit_number} (topic={topic})")
        return _textbook_context_cache[cache_key]
    
    try:
        collection = mongo_client.textbook_collection
        if collection is None:
            logger.warning("Textbook collection not available")
            return ""
        
        # Build query - metadata.unit is an integer in the textbook collection
        query = {"metadata.unit": unit_number}
        if topic:
            query["metadata.topic"] = topic
        
        docs = list(collection.find(query).limit(5))
        
        context_parts = []
        for doc in docs:
            content = doc.get("content", "")
            if content and len(content) > 20:
                context_parts.append(content[:300])  # Take first 300 chars of each doc
        
        result = "\n\n".join(context_parts) if context_parts else ""
        logger.info(f"Retrieved {len(context_parts)} textbook chunks for Unit {unit_number} (topic={topic}): {len(result)} chars")
        
        # Cache the result
        _textbook_context_cache[cache_key] = result
        return result
    except Exception as e:
        logger.error(f"Failed to retrieve textbook context for Unit {unit_number}: {e}")
        return ""


def _extract_part1_keyword(question_text: str) -> str:
    """
    Extract the target keyword/phrase from a Part I MCQ question.
    
    Part I questions test vocabulary: synonyms, antonyms, plurals, prefixes,
    abbreviations, phrasal verbs, prepositions, etc.
    The tested word is usually in single quotes like 'word'.
    
    Examples:
        "What is the synonym of the word 'threshold'?"  => "threshold"
        "What is an antonym for the word 'courage'?"     => "courage"
        "What is the prefix in the word 'indigenously'?" => "indigenously"
        "What is the expanded form of 'INSV'?"           => "INSV"
    
    Returns just the keyword if found, otherwise the full question text.
    """
    # 1) Word/phrase in single or curly quotes (most common pattern)
    m = re.search(r"['\u2018]([^'\u2019]+)['\u2019]", question_text)
    if m:
        return m.group(1).strip()
    
    # 2) Word/phrase in double or curly double quotes
    m = re.search(r'["\u201c]([^"\u201d]+)["\u201d]', question_text)
    if m:
        return m.group(1).strip()
    
    # 3) Pattern: "the word XXXX" (without quotes around the word)
    m = re.search(r'the word\s+(\w+)', question_text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    
    # 4) Pattern: "of/for XXXX?" at end of sentence
    m = re.search(r'(?:of|for)\s+(\w+)\s*\?', question_text, re.IGNORECASE)
    if m:
        return m.group(1).strip()
    
    # Fallback: return the full text (for question types like compound words, tenses)
    return question_text


async def call_deepeval_metric(metric: str, payload: Dict) -> Dict:
    """Call DeepEval server for a specific metric."""
    try:
        # Copy payload to avoid race condition when called in parallel
        metric_payload = {**payload, "metric": metric}
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(f"{DEEPEVAL_URL}/eval", json=metric_payload)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"DeepEval response for {metric}: {data}")
                result = data.get("results", [{}])[0] if "results" in data else data
                score = result.get("score")
                # Handle score being 0 or None differently
                if score is None:
                    error_msg = result.get("error") or "No score returned"
                    logger.warning(f"No score from DeepEval for {metric}: {error_msg}")
                    return {"metric": metric, "score": None, "error": error_msg, "explanation": ""}
                return {
                    "metric": metric,
                    "score": score,
                    "explanation": result.get("explanation", ""),
                    "error": None
                }
            else:
                error_text = response.text[:500] if response.text else f"HTTP {response.status_code}"
                logger.error(f"DeepEval HTTP error for {metric}: {error_text}")
                return {"metric": metric, "score": None, "error": error_text, "explanation": ""}
    except Exception as e:
        logger.error(f"DeepEval call failed for {metric}: {e}")
        return {"metric": metric, "score": None, "error": str(e), "explanation": ""}


def get_sample_questions_from_paper(paper: Dict) -> List[Dict]:
    """Extract 1 sample question from each of the 4 parts."""
    samples = []
    parts_data = paper.get("parts", {})
    
    # Part I - MCQs (14 questions)
    part_i = parts_data.get("I", {}).get("questions", [])
    if part_i:
        samples.append({"part": "I", "question": part_i[0]})
    
    # Part II - Short answers
    part_ii = parts_data.get("II", {})
    part_ii_sections = part_ii.get("sections", {})
    for section_name, section_data in part_ii_sections.items():
        questions = section_data.get("questions", [])
        if questions:
            samples.append({"part": "II", "section": section_name, "question": questions[0]})
            break
    
    # Part III - Paragraphs
    part_iii = parts_data.get("III", {})
    part_iii_sections = part_iii.get("sections", {})
    for section_name, section_data in part_iii_sections.items():
        questions = section_data.get("questions", [])
        if questions:
            samples.append({"part": "III", "section": section_name, "question": questions[0]})
            break
    
    # Part IV - Essays
    part_iv = parts_data.get("IV", {}).get("questions", [])
    if part_iv:
        samples.append({"part": "IV", "question": part_iv[0]})
    
    # Fallback: try to extract from flat questions list
    if len(samples) < 4 and paper.get("questions"):
        all_questions = paper.get("questions", [])
        parts_found = set(s["part"] for s in samples)
        
        for q in all_questions:
            part = q.get("part", "")
            if part and part not in parts_found:
                samples.append({"part": part, "question": q})
                parts_found.add(part)
            if len(samples) >= 4:
                break
    
    return samples[:4]  # Ensure max 4 samples


@router.get("/latest-paper-results")
async def get_latest_paper_evaluation(
    current_user: TokenPayload = Depends(require_admin)
):
    """Get the latest paper evaluation results."""
    results = load_evaluation_results()
    paper_evals = results.get("paper_evaluations", [])
    
    if paper_evals:
        return paper_evals[-1]  # Return most recent
    
    return {"message": "No paper evaluations found", "evaluated_at": None}


@router.get("/latest-chatbot-results")
async def get_latest_chatbot_evaluation(
    current_user: TokenPayload = Depends(require_admin)
):
    """Get the latest chatbot evaluation results."""
    results = load_evaluation_results()
    chatbot_evals = results.get("chatbot_evaluations", [])
    
    if chatbot_evals:
        return chatbot_evals[-1]  # Return most recent
    
    return {"message": "No chatbot evaluations found", "evaluated_at": None}


class PaperEvaluationRequest(BaseModel):
    parts: List[str] = ["I", "II", "III", "IV"]  # Default to all parts


@router.post("/evaluate-paper")
async def evaluate_generated_paper(
    request: PaperEvaluationRequest = PaperEvaluationRequest(),
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Generate a complete question paper and evaluate a representative sample.
    Generates full paper (47 questions) and evaluates 3 questions per selected part.
    Runs: Faithfulness, Contextual Recall, Contextual Precision, Hallucination metrics.
    
    Args:
        request: Contains 'parts' array to specify which parts to evaluate (e.g., ["I", "III"])
    """
    from retriever.paper_generation import PaperGenerationRetriever
    
    try:
        # Clear textbook context cache for fresh evaluation
        _textbook_context_cache.clear()
        
        logger.info("Starting full paper generation for evaluation...")
        
        # Generate a complete paper
        retriever = PaperGenerationRetriever()
        paper = await retriever.generate_complete_paper()
        
        # Extract all questions from the generated paper
        all_questions = []
        
        # Collect questions from all parts
        for part_key, part_data in paper.get("parts", {}).items():
            if "questions" in part_data:
                for q in part_data["questions"]:
                    all_questions.append({
                        "part": part_key,
                        "question": q,
                        "section": None
                    })
            elif "sections" in part_data:
                for section_key, section_data in part_data["sections"].items():
                    if "questions" in section_data:
                        for q in section_data["questions"]:
                            all_questions.append({
                                "part": part_key,
                                "question": q,
                                "section": section_key
                            })
        
        if not all_questions:
            raise HTTPException(status_code=500, detail="No questions generated in paper")
        
        # Sample 3 questions from each part for evaluation (total 12 questions)
        # Group by part
        questions_by_part = {}
        for item in all_questions:
            part = item["part"]
            if part not in questions_by_part:
                questions_by_part[part] = []
            questions_by_part[part].append(item)
        
        # Sample 3 from each selected part
        selected_parts = request.parts if request.parts else ["I", "II", "III", "IV"]
        logger.info(f"Selected parts for evaluation: {selected_parts}")
        
        sampled_questions = []
        for part, questions in questions_by_part.items():
            if part in selected_parts:  # Only sample from selected parts
                sample_size = min(3, len(questions))
                sampled = random.sample(questions, sample_size)
                sampled_questions.extend(sampled)
        
        logger.info(f"Evaluating {len(sampled_questions)} sampled questions from {len(all_questions)} total questions (parts: {selected_parts})...")
        
        # Prepare evaluation data
        evaluation_results = {
            "evaluated_at": datetime.utcnow().isoformat(),
            "total_questions_generated": len(all_questions),
            "total_questions_evaluated": len(sampled_questions),
            "sample_details": []
        }
        
        # Evaluate each sampled question
        aggregate_scores_temp = {"faithfulness": [], "contextual_recall": [], "contextual_precision": [], "hallucination": []}
        
        for idx, item in enumerate(sampled_questions, 1):
            q = item["question"]
            part = item["part"]
            section = item.get("section", "")
            
            # Extract question details
            raw_question_text = q.get("question_text", "")
            question_number = q.get("question_number", idx)
            marks = q.get("marks", "")
            unit_name = q.get("unit_name", "")
            lesson_type = q.get("lesson_type", "")
            brief_answer = q.get("brief_answer_guide", "")
            
            # ── Strip ALL choices/options/answers from question_text ──
            # LLM sometimes embeds options directly inside question_text
            question_stem = raw_question_text
            
            # 1) Cut at "Options:" / "Option:" (any case)
            question_stem = re.split(r'\s*Options?\s*:', question_stem, flags=re.IGNORECASE)[0].strip()
            # 2) Cut at "Choices:" (any case)
            question_stem = re.split(r'\s*Choices?\s*:', question_stem, flags=re.IGNORECASE)[0].strip()
            # 3) Cut at first "a)" / "a." / "A)" / "A." / "(a)" / "(A)" on a new line or after two+ spaces
            question_stem = re.split(r'(?:\n|  +)\s*[\(\[]?[aA][\)\]\.]\s', question_stem)[0].strip()
            # 4) Cut at inline "a)" pattern (e.g. "...Tarini? a) Indian Naval...")
            question_stem = re.split(r'\s+[aA]\)\s+', question_stem)[0].strip()
            # 5) Cut at "Answer:" / "Correct Answer:" (any case)
            question_stem = re.split(r'\s*(?:Correct\s+)?Answer\s*:', question_stem, flags=re.IGNORECASE)[0].strip()
            
            logger.info(f"Q{question_number} Part {part} | RAW: {raw_question_text[:80]}... | STEM: {question_stem[:80]}...")
            
            # Retrieve actual textbook context from MongoDB for ALL parts
            textbook_context = ""
            try:
                unit_match = re.search(r'(?:Unit\s*|unit\s*)(\d+)', unit_name or '', re.IGNORECASE)
                if unit_match:
                    unit_num = int(unit_match.group(1))
                    # Pick topic hint based on part/section/lesson_type
                    topic_hint = None
                    if lesson_type in ("prose", "Prose"):
                        topic_hint = "Prose"
                    elif lesson_type in ("poetry", "Poetry"):
                        topic_hint = "Poetry"
                    elif lesson_type in ("supplementary", "Supplementary"):
                        topic_hint = "Supplementary"
                    textbook_context = await get_textbook_context_for_unit(unit_num, topic=topic_hint)
                else:
                    # Fallback: try unit 1 content
                    textbook_context = await get_textbook_context_for_unit(1)
            except Exception as e:
                logger.warning(f"Failed to retrieve textbook context for '{unit_name}': {e}")
            
            # For evaluation: Use ONLY the question stem (no options, no answer)
            # For display: Show full question with options
            question_for_eval = question_stem
            question_display = raw_question_text  # Keep full text for display
            
            if part == "I":
                # ── PART I: Extract ONLY the keyword/word being tested ──
                # Part I tests vocabulary (synonyms, antonyms, plurals, prefixes, etc.)
                # Faithfulness should check if the WORD itself comes from the textbook,
                # NOT whether the full sentence "What is the synonym of..." is in the book.
                keyword = _extract_part1_keyword(question_stem)
                question_for_eval = keyword  # Send ONLY the keyword to evaluation
                logger.info(f"Part I keyword extraction: '{question_stem[:60]}' => '{keyword}'")
                
                if "options" in q:
                    options = q.get("options", [])
                    correct_option = q.get("correct_option", "") or q.get("correct_answer", "")
                    # If raw_question_text doesn't have options, add them for display
                    if "Options:" not in raw_question_text:
                        if options and isinstance(options, list):
                            options_text = "\n".join(options)
                            question_display = f"{question_stem}\nOptions:\n{options_text}"
                    if correct_option:
                        brief_answer = f"Correct answer: {correct_option}"
            
            # Build context: textbook content is the PRIMARY source for faithfulness
            metadata_context = [
                f"Topic: {unit_name}" if unit_name else "",
                f"Lesson Type: {lesson_type}" if lesson_type else "",
                f"Section: {section}" if section else "",
                f"Marks: {marks}" if marks else "",
                brief_answer if brief_answer else ""
            ]
            metadata_context = [c for c in metadata_context if c]
            
            # For faithfulness, the retrieval_context must contain the SOURCE material
            # so the LLM judge can verify if the question is grounded in the textbook
            if textbook_context:
                retrieval_ctx = [textbook_context[:1000]]  # Primary: actual textbook content (limited for speed)
                retrieval_ctx.extend(metadata_context)     # Secondary: metadata
            else:
                retrieval_ctx = metadata_context
            
            # Tailor query based on part
            if part == "I":
                eval_query = f"Check if the vocabulary word '{question_for_eval}' appears in the textbook content from {unit_name or 'English'}"
            else:
                eval_query = f"Generate a {lesson_type or 'English'} question about {unit_name or 'English'}"
            
            payload = {
                "query": eval_query,
                "context": retrieval_ctx,
                "retrieval_context": retrieval_ctx,
                "output": question_for_eval,  # Part I: keyword only; Others: question stem
                "expected_output": brief_answer or question_for_eval
            }
            
            logger.debug(f"Evaluating Q{question_number} (Part {part}): {question_for_eval[:50]}...")
            
            # Build question preview for UI
            if part == "I":
                # Show something informative like: "Vocabulary: 'threshold' (synonym)"
                # Try to detect question type from the original question text
                q_lower = question_stem.lower()
                q_type = "vocabulary"
                for label in ["synonym", "antonym", "plural", "prefix", "suffix", "abbreviation",
                              "phrasal verb", "compound", "preposition", "tense", "linker", "connector"]:
                    if label in q_lower:
                        q_type = label
                        break
                preview = f"Vocabulary: '{question_for_eval}' ({q_type})"
            else:
                preview = question_for_eval[:150] + "..." if len(question_for_eval) > 150 else question_for_eval
            
            question_results = {
                "part": part,
                "section": section,
                "question_number": str(question_number),
                "question_preview": preview,
                "metrics": {}
            }
            
            # Run all four metrics in PARALLEL using asyncio.gather for speed
            metric_names = ["faithfulness", "contextual_recall", "contextual_precision", "hallucination"]
            metric_tasks = [call_deepeval_metric(metric, payload) for metric in metric_names]
            metric_results = await asyncio.gather(*metric_tasks)
            
            # Store results
            for metric, result in zip(metric_names, metric_results):
                question_results["metrics"][metric] = result
                if result.get("score") is not None:
                    aggregate_scores_temp[metric].append(result["score"])
            
            evaluation_results["sample_details"].append(question_results)
            
            # Log progress every 3 questions
            if idx % 3 == 0:
                logger.info(f"Progress: {idx}/{len(sampled_questions)} questions evaluated")
        
        # Calculate averages and prepare final format
        aggregate_scores = {}
        for metric in ["faithfulness", "contextual_recall", "contextual_precision", "hallucination"]:
            scores = aggregate_scores_temp[metric]
            if scores:
                aggregate_scores[metric] = sum(scores) / len(scores)
            else:
                aggregate_scores[metric] = None
        
        # Prepare samples for frontend
        samples_output = []
        for detail in evaluation_results["sample_details"]:
            samples_output.append({
                "part": detail["part"],
                "question_number": detail.get("question_number", ""),
                "question": detail.get("question_preview", ""),
                "metrics": detail["metrics"]
            })
        
        # Final result format for frontend
        final_result = {
            "timestamp": evaluation_results["evaluated_at"],
            "aggregate_scores": aggregate_scores,
            "samples": samples_output[:10],  # Show first 10 in UI
            "total_questions_generated": evaluation_results["total_questions_generated"],
            "total_questions_evaluated": evaluation_results["total_questions_evaluated"]
        }
        
        # Save results
        all_results = load_evaluation_results()
        all_results["paper_evaluations"].append(final_result)
        # Keep only last 10 evaluations
        all_results["paper_evaluations"] = all_results["paper_evaluations"][-10:]
        save_evaluation_results(all_results)
        
        logger.info("Paper evaluation completed successfully")
        return final_result
        
    except Exception as e:
        logger.error(f"Paper evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/evaluate-chatbot")
async def evaluate_chatbot_response(
    request: ChatbotEvaluationRequest,
    current_user: TokenPayload = Depends(require_admin)
):
    """
    Run a chatbot query and evaluate the response using DeepEval metrics.
    """
    from retriever.concept_explanation import ConceptExplanationRetriever
    from llm.factory import get_llm
    
    query = request.query
    
    try:
        logger.info(f"Evaluating chatbot for query: {query}")
        
        # Get chatbot response
        retriever = ConceptExplanationRetriever()
        context_blocks, citations = await retriever.retrieve(
            query=query,
            vector_weight=0.5,
            bm25_weight=0.5,
            top_k=5
        )
        
        if not context_blocks:
            context_blocks = ["No relevant content found"]
        
        # Generate response
        context_text = "\n\n".join(context_blocks[:3])
        prompt = f"""You are an English teacher for TN SSLC (10th Standard).
A student has asked the following question:

STUDENT QUESTION:
{query}

RELEVANT TEXTBOOK CONTENT:
{context_text}

Provide a clear, concise explanation using ONLY the provided textbook content."""

        llm = get_llm()
        answer = await llm.generate(prompt, max_tokens=512, temperature=0.7)
        
        # Prepare evaluation payload
        payload = {
            "query": query,
            "context": context_blocks[:5],
            "output": answer,
            "expected_output": "A helpful educational response based on textbook content"
        }
        
        evaluation_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "response": answer,
            "context_count": len(citations),
            "metrics": {}
        }
        
        # Run chatbot-specific metrics: answer relevancy + PII leakage
        for metric in ["answer_relevancy", "pii_leakage"]:
            result = await call_deepeval_metric(metric, payload)
            evaluation_results["metrics"][metric] = result
        
        # Save results
        all_results = load_evaluation_results()
        all_results["chatbot_evaluations"].append(evaluation_results)
        all_results["chatbot_evaluations"] = all_results["chatbot_evaluations"][-10:]
        save_evaluation_results(all_results)
        
        logger.info("Chatbot evaluation completed successfully")
        return evaluation_results
        
    except Exception as e:
        logger.error(f"Chatbot evaluation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-results")
async def get_all_evaluation_results(
    current_user: TokenPayload = Depends(require_admin)
):
    """Get all evaluation results."""
    return load_evaluation_results()
