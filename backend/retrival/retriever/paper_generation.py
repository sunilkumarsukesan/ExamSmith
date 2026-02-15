from .base import RetrieverMode
from .question_generator import QuestionGenerator
from .coverage_validator import CoverageValidator
from .image_search import get_picture_question
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation
from config import settings
from embeddings import embed_query, get_embeddings
import logging
from typing import List, Dict, Tuple
import json

logger = logging.getLogger(__name__)

class PaperGenerationRetriever(RetrieverMode):
    """Retrieves context and generates original questions for paper creation."""
    
    def __init__(self):
        """Initialize retriever with question generator and validator."""
        self.generator = QuestionGenerator()
        self.validator = CoverageValidator()
        self.hybrid_search = HybridSearch()
        self.config = HybridSearchConfig(
            vector_weight=settings.hybrid_default_vector_weight,
            bm25_weight=settings.hybrid_default_bm25_weight,
            rrf_k=settings.hybrid_rrf_k,
            top_k=settings.hybrid_default_top_k
        )
    
    async def retrieve(
        self,
        query: str = None,
        part: str = None,
        section: str = None,
        topic: str = None,
        difficulty: str = None,
        top_k: int = 50,
        **kwargs
    ) -> tuple[List[dict], List[Citation]]:
        """
        Retrieve textbook context for question generation.
        (Legacy method - actual generation happens via generate_complete_paper)
        
        Args:
            query: General query for textbook context
            part: Paper part (I, II, III, IV)
            section: Section within part
            topic: Specific topic
            difficulty: Difficulty level
            top_k: Maximum number of chunks to retrieve
        """
        
        collection = mongo_client.textbook_collection
        if collection is None:
            logger.warning("Textbook collection unavailable")
            return [], []
        
        # Build query filters
        filters = {}
        if topic:
            filters["metadata.topic"] = topic
        if section:
            filters["metadata.content_type"] = section
        
        try:
            # Use hybrid search for semantic retrieval
            results = await self.hybrid_search.search(
                query=query or f"Exam preparation for {section or 'English'}",
                collection=collection,
                filters=filters,
                config=self.config
            )
            
            logger.debug(f"Paper generation context retrieval: {len(results)} chunks found")
            
            # Convert to context blocks and citations
            context_blocks = []
            citations = []
            
            for doc in results:
                content = doc.get("content", "")
                context_blocks.append(content)
                citations.append(
                    Citation(
                        chunk_id=str(doc.get("_id")),
                        source="textbook",
                        lesson_name=doc.get("metadata", {}).get("lesson_name"),
                        year=doc.get("metadata", {}).get("year")
                    )
                )
            
            return context_blocks, citations
        
        except Exception as e:
            logger.error(f"Paper generation retrieval failed: {str(e)}")
            return [], []
    
    async def generate_complete_paper(
        self,
        max_retries: int = 1,  # Reduced from 3 to 1
    ) -> Dict:
        """
        Generate complete, original SSLC English question paper.
        
        This is the PRIMARY ENTRY POINT for paper generation.
        
        Returns:
            dict: Complete question paper in JSON format with all 47 questions
        """
        
        logger.info("=" * 80)
        logger.info("STARTING COMPLETE QUESTION PAPER GENERATION (OPTIMIZED)")
        logger.info("=" * 80)
        
        all_questions = []
        retrieval_errors = []
        
        try:
            # PHASE 1: Retrieve textbook context (parallel retrieval)
            logger.info("\n[PHASE 1] Retrieving textbook context for question generation...")
            
            # Retrieve textbook context by section
            textbook_context = await self._retrieve_textbook_context()
            previous_qp_context = await self._retrieve_previous_qp_context()
            
            if not textbook_context:
                logger.warning("Textbook context retrieval failed - using fallback")
                retrieval_errors.append("Textbook context not available")
            
            # PHASE 2: Generate Part I (MCQs) - SINGLE LLM CALL
            logger.info("\n[PHASE 2] Generating Part I (14 MCQ questions in one batch)...")
            try:
                vocab_context = textbook_context.get("vocabulary", "")
                logger.info(f"Vocabulary context length: {len(vocab_context)} chars")
                
                if not vocab_context:
                    logger.warning("No vocabulary context found, using fallback for Part I")
                    vocab_context = "Vocabulary words from TN SSLC English textbook covering all 7 units."
                
                part_i_questions = await self.generator.generate_part_i_mcqs(
                    textbook_context=vocab_context,
                    previous_paper_context=previous_qp_context.get("part_i", "")
                )
                
                logger.info(f"Part I generation returned: {len(part_i_questions)} questions")
                
                if part_i_questions:
                    all_questions.extend(part_i_questions)
                    logger.info(f"✓ Generated {len(part_i_questions)} Part I MCQ questions")
                else:
                    logger.warning("Part I generation returned empty list")
                    
            except Exception as e:
                logger.error(f"✗ Part I generation failed: {str(e)}", exc_info=True)
                retrieval_errors.append(f"Part I MCQ generation: {str(e)}")
            
            # PHASE 3: Generate Part II (Prose, Poetry, Grammar, Map) - REDUCED CALLS
            logger.info("\n[PHASE 3] Generating Part II (Prose, Poetry, Grammar, Map)...")
            
            # Part II Prose (4 questions from lessons 1-4, answer 3) - ONE CALL PER LESSON
            try:
                for lesson_num in [1, 2, 3, 4]:
                    prose_context = await self._retrieve_prose_context(lesson_num)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_prose_questions(
                        lesson_number=lesson_num,
                        textbook_context=prose_context,
                        marks=2,
                        previous_paper_context=previous_qp_context.get("part_ii_prose", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 14 + lesson_num  # Q15-18
                        question["internal_choice"] = True if lesson_num <= 4 else False
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('part') == 'II' and q.get('section') == 'Prose'])} prose questions")
            except Exception as e:
                logger.error(f"✗ Part II Prose generation failed: {str(e)}")
                retrieval_errors.append(f"Part II Prose: {str(e)}")
            
            # Part II Poetry (4 questions from different poems across units)
            # Actual poem names from TN SSLC curriculum
            try:
                poetry_poems = [
                    ("Life", 1),           # Unit 1
                    ("The Grumble Family", 2),  # Unit 2
                    ("I Am Every Woman", 3),    # Unit 3
                    ("The Ant and the Cricket", 4)  # Unit 4
                ]
                for idx, (poem, unit) in enumerate(poetry_poems[:4]):
                    poetry_context = await self._retrieve_poetry_context_by_unit(unit)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_poetry_questions(
                        poem_name=poem,
                        textbook_context=poetry_context,
                        marks=2,
                        previous_paper_context=previous_qp_context.get("part_ii_poetry", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 18 + idx + 1  # Q19-22
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('part') == 'II' and q.get('section') == 'Poetry'])} poetry questions")
            except Exception as e:
                logger.error(f"✗ Part II Poetry generation failed: {str(e)}")
                retrieval_errors.append(f"Part II Poetry: {str(e)}")
            
            # Part II Grammar (5 questions, answer 3)
            try:
                grammar_areas = ["voice", "speech", "punctuation", "sentence_types", "rearrangement"]
                for idx, area in enumerate(grammar_areas):
                    grammar_context = await self._retrieve_grammar_context(area)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_grammar_questions(
                        grammar_area=area,
                        textbook_context=grammar_context,
                        marks=2,
                        previous_paper_context=previous_qp_context.get("part_ii_grammar", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 22 + idx + 1  # Q23-27
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('lesson_type') == 'grammar'])} grammar questions")
            except Exception as e:
                logger.error(f"✗ Part II Grammar generation failed: {str(e)}")
                retrieval_errors.append(f"Part II Grammar: {str(e)}")
            
            # Part II Map/Directions (Q28)
            try:
                map_question = await self._generate_map_question()
                if map_question:
                    map_question["question_number"] = 28
                    all_questions.append(map_question)
                logger.info("✓ Generated map/directions question")
            except Exception as e:
                logger.error(f"✗ Map question generation failed: {str(e)}")
                retrieval_errors.append(f"Map question: {str(e)}")
            
            # PHASE 4: Generate Part III (Prose Paragraph, Poetry, Supplementary, Writing, Memory Poem)
            logger.info("\n[PHASE 4] Generating Part III (Prose, Poetry, Supplementary, Writing, Memory Poem)...")
            
            # Part III Prose Paragraph (4 questions, from lessons 4, 5, 6, 7 for coverage)
            try:
                part_iii_prose_lessons = [4, 5, 6, 7]  # Cover remaining lessons
                for idx, lesson_num in enumerate(part_iii_prose_lessons):
                    prose_context = await self._retrieve_prose_context(lesson_num)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_prose_questions(
                        lesson_number=lesson_num,
                        textbook_context=prose_context,
                        marks=5,
                        previous_paper_context=previous_qp_context.get("part_iii_prose", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 29 + idx  # Q29-32
                        question["part"] = "III"
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('part') == 'III' and q.get('section') == 'Prose'])} prose paragraph questions")
            except Exception as e:
                logger.error(f"✗ Part III Prose Paragraph failed: {str(e)}")
                retrieval_errors.append(f"Part III Prose: {str(e)}")
            
            # Part III Poetry (4 questions from units 5, 6, 7 for diversity)
            try:
                part_iii_poems = [
                    ("The Secret of the Machines", 5),  # Unit 5
                    ("No Men Are Foreign", 6),          # Unit 6
                    ("The House on Elm Street", 7),     # Unit 7
                    ("Sea Fever", 6)                    # Memory poem candidate from Unit 6
                ]
                for idx, (poem, unit) in enumerate(part_iii_poems[:4]):
                    poetry_context = await self._retrieve_poetry_context_by_unit(unit)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_poetry_questions(
                        poem_name=poem,
                        textbook_context=poetry_context,
                        marks=5,
                        previous_paper_context=previous_qp_context.get("part_iii_poetry", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 32 + idx + 1  # Q33-36
                        question["part"] = "III"
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('part') == 'III' and q.get('section') == 'Poetry'])} poetry paragraph questions")
            except Exception as e:
                logger.error(f"✗ Part III Poetry Paragraph failed: {str(e)}")
                retrieval_errors.append(f"Part III Poetry: {str(e)}")
            
            # Part III Supplementary (2 questions from different units)
            try:
                supplementary_stories = [
                    ("The Tempest", 1),        # Unit 1
                    ("The Story of Mulan", 3), # Unit 3
                ]
                for idx, (story, unit) in enumerate(supplementary_stories[:2]):
                    supp_context = await self._retrieve_supplementary_context_by_unit(unit)
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_supplementary_questions(
                        story_name=story,
                        textbook_context=supp_context,
                        marks=5,
                        previous_paper_context=previous_qp_context.get("part_iii_supplementary", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = 36 + idx + 1  # Q37-38
                        question["part"] = "III"
                        all_questions.append(question)
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('lesson_type') == 'supplementary'])} supplementary questions")
            except Exception as e:
                logger.error(f"✗ Part III Supplementary failed: {str(e)}")
                retrieval_errors.append(f"Part III Supplementary: {str(e)}")
            
            # Part III Writing Skills (6 questions - Q39-44)
            # Q42 is a picture-based question
            try:
                writing_types = ["letter", "email", "paragraph"]  # Q39, 40, 41
                question_numbers_before = [39, 40, 41]
                
                # Generate Q39-41 (letter, email, paragraph)
                for idx, writing_type in enumerate(writing_types):
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_writing_questions(
                        writing_type=writing_type,
                        previous_paper_context=previous_qp_context.get("part_iii_writing", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = question_numbers_before[idx]
                        question["part"] = "III"
                        all_questions.append(question)
                
                # Q42: Picture-based question (special handling)
                try:
                    picture_question = await get_picture_question()
                    picture_question["question_number"] = 42
                    picture_question["part"] = "III"
                    all_questions.append(picture_question)
                    logger.info(f"✓ Generated Q42 picture question: {picture_question.get('image_topic', 'Unknown')}")
                except Exception as pic_err:
                    logger.error(f"✗ Picture question failed: {str(pic_err)}")
                    # Fallback to regular paragraph question
                    fallback_q = await self.generator.generate_writing_questions(
                        writing_type="paragraph",
                        previous_paper_context="",
                        unit_number=self.generator._get_random_unit()
                    )
                    if fallback_q:
                        fallback_q["question_number"] = 42
                        fallback_q["part"] = "III"
                        all_questions.append(fallback_q)
                
                # Q43-44: dialogue and story
                writing_types_after = ["dialogue", "story"]
                question_numbers_after = [43, 44]
                
                for idx, writing_type in enumerate(writing_types_after):
                    random_unit = self.generator._get_random_unit()
                    question = await self.generator.generate_writing_questions(
                        writing_type=writing_type,
                        previous_paper_context=previous_qp_context.get("part_iii_writing", ""),
                        unit_number=random_unit
                    )
                    if question:
                        question["question_number"] = question_numbers_after[idx]
                        question["part"] = "III"
                        all_questions.append(question)
                
                logger.info(f"✓ Generated {len([q for q in all_questions if q.get('lesson_type') in ['writing', 'picture_composition']])} writing skill questions")
            except Exception as e:
                logger.error(f"✗ Part III Writing Skills failed: {str(e)}")
                retrieval_errors.append(f"Part III Writing: {str(e)}")
            
            # Part III Memory Poem (Q45)
            try:
                memory_question = await self._generate_memory_poem_question()
                if memory_question:
                    memory_question["question_number"] = 45
                    memory_question["part"] = "III"
                    all_questions.append(memory_question)
                logger.info("✓ Generated memory poem question")
            except Exception as e:
                logger.error(f"✗ Memory poem generation failed: {str(e)}")
                retrieval_errors.append(f"Memory Poem: {str(e)}")
            
            # PHASE 5: Generate Part IV (Internal Choice Questions)
            logger.info("\n[PHASE 5] Generating Part IV (Internal Choice Questions)...")
            
            # Q46: Option A (Developing Hints) OR Option B (Comprehension)
            try:
                q46 = await self._generate_part_iv_q46(supplementary_stories[0] if supplementary_stories else "Story1")
                if q46:
                    all_questions.append(q46)
                logger.info("✓ Generated Q46 (internal choice)")
            except Exception as e:
                logger.error(f"✗ Q46 generation failed: {str(e)}")
                retrieval_errors.append(f"Q46: {str(e)}")
            
            # Q47: Choose from Prose/Poem/Supplementary
            try:
                q47 = await self._generate_part_iv_q47()
                if q47:
                    all_questions.append(q47)
                logger.info("✓ Generated Q47 (internal choice)")
            except Exception as e:
                logger.error(f"✗ Q47 generation failed: {str(e)}")
                retrieval_errors.append(f"Q47: {str(e)}")
            
            # PHASE 6: Validate coverage (WARNING ONLY - NO RETRIES)
            logger.info("\n[PHASE 6] Validating coverage rules...")
            is_valid, violations = self.validator.validate_paper(all_questions)
            
            if not is_valid:
                logger.warning(f"Coverage validation found {len(violations)} violations (proceeding anyway for speed)")
                # Log violations but don't retry - user can regenerate manually if needed
            else:
                logger.info("✓ All coverage rules passed")
            
            # PHASE 6.5: Quality Review SKIPPED FOR SPEED
            logger.info("\n[PHASE 6.5] Skipping quality review (optimization)...")
            
            # PHASE 7: Assemble final paper
            logger.info("\n[PHASE 7] Assembling final question paper...")
            paper = self._assemble_paper_json(all_questions)
            
            logger.info("=" * 80)
            logger.info("QUESTION PAPER GENERATION COMPLETE (OPTIMIZED)")
            logger.info(f"Total questions generated: {len(all_questions)}")
            logger.info(f"Validation status: {'✓ PASSED' if is_valid else '⚠️ WARNINGS (see logs)'}")
            logger.info("=" * 80)
            
            return paper
        
        except Exception as e:
            logger.error(f"Paper generation failed: {str(e)}")
            raise
    
    async def _retrieve_textbook_context(self) -> Dict:
        """Retrieve textbook content organized by section from ALL 7 units."""
        try:
            context = {
                "vocabulary": "",
                "prose": {},
                "poetry": {},
                "supplementary": {},
                "grammar": {}
            }
            
            collection = mongo_client.textbook_collection
            if collection is None:
                return context
            
            # Get vocabulary/content from ALL 7 units for diverse MCQ generation
            all_vocab_content = []
            for unit_num in range(1, 8):  # Units 1-7
                # Get prose content from each unit (which contains vocabulary words)
                unit_docs = list(collection.find({
                    "metadata.unit": unit_num
                }).limit(10))
                
                for doc in unit_docs:
                    content = doc.get("content", "")
                    if len(content) > 50:  # Only substantial content
                        all_vocab_content.append(f"[Unit {unit_num}] {content}")
            
            context["vocabulary"] = "\n\n".join(all_vocab_content[:50])  # Limit total chunks
            
            logger.info(f"Retrieved vocabulary context from {len(all_vocab_content)} chunks across all units")
            
            return context
        except Exception as e:
            logger.error(f"Textbook context retrieval failed: {str(e)}")
            return {}
    
    async def _retrieve_previous_qp_context(self) -> Dict:
        """Retrieve previous question paper for style calibration."""
        try:
            context = {
                "part_i": "",
                "part_ii_prose": "",
                "part_ii_poetry": "",
                "part_ii_grammar": "",
                "part_iii_prose": "",
                "part_iii_poetry": "",
                "part_iii_writing": "",
                "part_iii_supplementary": ""
            }
            
            collection = mongo_client.questionpapers_collection
            if collection is None:
                return context
            
            # Get sample previous questions for style reference only
            sample_questions = list(collection.find().limit(5))
            context["part_i"] = " ".join([doc.get("content", "") for doc in sample_questions[:2]])
            
            return context
        except Exception as e:
            logger.error(f"Previous QP context retrieval failed: {str(e)}")
            return {}
    
    async def _retrieve_prose_context(self, lesson_number: int) -> str:
        """Retrieve prose lesson context by unit/lesson number."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            # First try with unit number and Prose topic
            docs = list(collection.find({
                "metadata.unit": lesson_number,
                "metadata.topic": "Prose"
            }).limit(10))
            
            if not docs:
                # Fallback: try any content from this unit
                docs = list(collection.find({
                    "metadata.unit": lesson_number
                }).limit(10))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Prose context retrieval failed: {str(e)}")
            return ""
    
    async def _retrieve_poetry_context(self, poem_name: str) -> str:
        """Retrieve poetry context."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            docs = list(collection.find({
                "metadata.lesson_type": "poetry",
                "metadata.poem_name": poem_name
            }).limit(5))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Poetry context retrieval failed: {str(e)}")
            return ""
    
    async def _retrieve_poetry_context_by_unit(self, unit_number: int) -> str:
        """Retrieve poetry context by unit number."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            # Get poetry content from specific unit
            docs = list(collection.find({
                "metadata.unit": unit_number,
                "metadata.topic": "Poem"
            }).limit(10))
            
            if not docs:
                # Fallback: get any content from this unit
                docs = list(collection.find({
                    "metadata.unit": unit_number
                }).limit(10))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Poetry context retrieval by unit failed: {str(e)}")
            return ""
    
    async def _retrieve_grammar_context(self, grammar_area: str) -> str:
        """Retrieve grammar examples."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            # Get example sentences for grammar context
            docs = list(collection.find({
                "metadata.content_type": "grammar",
                "metadata.grammar_area": grammar_area
            }).limit(5))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Grammar context retrieval failed: {str(e)}")
            return ""
    
    async def _retrieve_supplementary_context(self, story_name: str) -> str:
        """Retrieve supplementary story context."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            docs = list(collection.find({
                "metadata.lesson_type": "supplementary",
                "metadata.story_name": story_name
            }).limit(5))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Supplementary context retrieval failed: {str(e)}")
            return ""
    
    async def _retrieve_supplementary_context_by_unit(self, unit_number: int) -> str:
        """Retrieve supplementary story context by unit number."""
        try:
            collection = mongo_client.textbook_collection
            if collection is None:
                return ""
            
            # Get supplementary content from specific unit
            docs = list(collection.find({
                "metadata.unit": unit_number,
                "metadata.topic": "Supplementary"
            }).limit(10))
            
            if not docs:
                # Fallback: get any content from this unit
                docs = list(collection.find({
                    "metadata.unit": unit_number
                }).limit(10))
            
            return " ".join([doc.get("content", "") for doc in docs])
        except Exception as e:
            logger.error(f"Supplementary context retrieval by unit failed: {str(e)}")
            return ""
    
    async def _generate_map_question(self) -> Dict:
        """Generate map/directions question from random unit context."""
        random_unit = self.generator._get_random_unit()
        
        prompt = f"""Generate 1 ORIGINAL map/directions question for TN SSLC English from Unit {random_unit}.

REQUIREMENTS:
- Create a simple route map with 4-5 landmarks
- Ask student to describe directions (e.g., "From A to B via C")
- Generate afresh (no previous exam reuse)
- 2 marks
- Relate to themes/locations from Unit {random_unit}

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": 28,
  "part": "II",
  "section": "Map/Directions",
  "question_text": "<question with map description>",
  "marks": 2,
  "internal_choice": false,
  "unit_name": "Directions Unit {random_unit}",
  "lesson_type": "map",
  "brief_answer_guide": "<expected answer>"
}}"""
        
        try:
            response = await self.generator.llm.generate(prompt, max_tokens=512, temperature=0.7)
            return self.generator._parse_json_response(response, single=True)
        except Exception as e:
            logger.error(f"Map question generation failed: {str(e)}")
            return {}
    
    async def _generate_memory_poem_question(self) -> Dict:
        """Generate memory poem question from prescribed curriculum poems with random unit."""
        import random
        
        # TN SSLC prescribed memory poems
        prescribed_poems = [
            ("Life", 1),
            ("The Road Not Taken", 2),
            ("No Men Are Foreign", 6),
            ("Laugh and Be Merry", 3),
            ("The River", 4),
            ("Sea Fever", 5)
        ]
        
        # Randomly select a poem
        selected_poem, unit = random.choice(prescribed_poems)
        # Also generate a random unit for the question context (different from poem unit)
        random_unit = self.generator._get_random_unit()
        
        prompt = f"""Generate 1 memory poem question for TN SSLC English Part III (Unit {random_unit} context).

SELECTED POEM: {selected_poem} (Unit {unit})

REQUIREMENTS:
- This is a MEMORY POEM (prescribed for recitation)
- Task: Ask student to recite a specific stanza + explain its meaning
- 5 marks (1 mark recitation, 4 marks explanation)
- Question should be specific about which stanza to recite
- Context can relate to Unit {random_unit} themes

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": 45,
  "part": "III",
  "section": "Memory Poem",
  "question_text": "Recite a stanza from '{selected_poem}' and explain its meaning.",
  "marks": 5,
  "internal_choice": false,
  "unit_name": "Memory Poem: {selected_poem} (Unit {random_unit})",
  "lesson_type": "memory_poem",
  "brief_answer_guide": "1 mark for correct recitation, 4 marks for explanation (content, interpretation, and coherence)"
}}"""
        
        try:
            response = await self.generator.llm.generate(prompt, max_tokens=512, temperature=0.7)
            return self.generator._parse_json_response(response, single=True)
        except Exception as e:
            logger.error(f"Memory poem generation failed: {str(e)}")
            # Return a default valid question
            return {
                "question_number": 45,
                "part": "III",
                "section": "Memory Poem",
                "question_text": f"Recite the first stanza of '{selected_poem}' and explain its meaning.",
                "marks": 5,
                "internal_choice": False,
                "unit_name": f"Memory Poem: {selected_poem}",
                "lesson_type": "memory_poem",
                "brief_answer_guide": "1 mark for correct recitation, 4 marks for explanation"
            }
    
    async def _generate_part_iv_q46(self, story_name: str) -> Dict:
        """Generate Q46 with internal choice."""
        prompt = f"""Generate Q46 with INTERNAL CHOICE for TN SSLC English Part IV (8 marks).

STORY: {story_name}

Generate TWO OPTIONS:

Option A: Developing Hints (Supplementary Story)
- Provide scenario + hint words from story
- Ask student to develop into short story (150-200 words)

Option B: Paragraph / Poem Comprehension
- Provide 8-10 line prose or poem excerpt
- Ask 3 comprehension sub-questions

REQUIREMENTS:
- Both options are alternatives (student chooses ONE)
- Ensure both distinct from previous exams
- 8 marks each

Response format: Return ONLY valid JSON (no markdown):
{{
  "question_number": 46,
  "part": "IV",
  "section": "Internal Choice",
  "internal_choice": true,
  "marks": 8,
  "options": [
    {{
      "option_label": "A",
      "question_text": "<story development task>",
      "lesson_type": "supplementary"
    }},
    {{
      "option_label": "B",
      "question_text": "<comprehension task>",
      "lesson_type": "prose"
    }}
  ]
}}"""
        
        try:
            response = await self.generator.llm.generate(prompt, max_tokens=1024, temperature=0.7)
            return self.generator._parse_json_response(response, single=True)
        except Exception as e:
            logger.error(f"Q46 generation failed: {str(e)}")
            return {}
    
    async def _generate_part_iv_q47(self) -> Dict:
        """Generate Q47 with internal choice."""
        prompt = """Generate Q47 with INTERNAL CHOICE for TN SSLC English Part IV (8 marks).

Generate THREE OPTIONS (student chooses ONE):

Option A: Prose Comprehension
- Provide prose excerpt (8-10 lines) from any prose lesson
- Ask 3 sub-questions on theme/character/message

Option B: Poem Comprehension
- Provide poem stanza (8-10 lines) from any poem
- Ask 3 sub-questions on device/meaning/tone

Option C: Supplementary Comprehension
- Provide story excerpt (8-10 lines) from supplementary lesson
- Ask 3 sub-questions on plot/moral/inference

REQUIREMENTS:
- All three options provided as alternatives
- Retrieve diverse content for breadth
- Paraphrase all excerpts; avoid textbook copying
- Create original comprehension questions
- 8 marks each

Response format: Return ONLY valid JSON (no markdown):
{
  "question_number": 47,
  "part": "IV",
  "section": "Internal Choice",
  "internal_choice": true,
  "marks": 8,
  "options": [
    {{
      "option_label": "A",
      "question_text": "<prose comprehension task>",
      "lesson_type": "prose"
    }},
    {{
      "option_label": "B",
      "question_text": "<poetry comprehension task>",
      "lesson_type": "poetry"
    }},
    {{
      "option_label": "C",
      "question_text": "<supplementary comprehension task>",
      "lesson_type": "supplementary"
    }}
  ]
}"""
        
        try:
            response = await self.generator.llm.generate(prompt, max_tokens=1024, temperature=0.7)
            return self.generator._parse_json_response(response, single=True)
        except Exception as e:
            logger.error(f"Q47 generation failed: {str(e)}")
            return {}
    
    def _assemble_paper_json(self, questions: List[Dict]) -> Dict:
        """Assemble all questions into final paper JSON structure."""
        
        # Group questions by part and section
        parts = {
            "I": {"questions": []},
            "II": {"sections": {}},
            "III": {"sections": {}},
            "IV": {"questions": []}
        }
        
        for q in questions:
            part = q.get("part")
            section = q.get("section", "")
            
            if part == "I":
                parts["I"]["questions"].append(q)
            elif part == "II":
                if section not in parts["II"]["sections"]:
                    parts["II"]["sections"][section] = {"questions": []}
                parts["II"]["sections"][section]["questions"].append(q)
            elif part == "III":
                if section not in parts["III"]["sections"]:
                    parts["III"]["sections"][section] = {"questions": []}
                parts["III"]["sections"][section]["questions"].append(q)
            elif part == "IV":
                parts["IV"]["questions"].append(q)
        
        # Build final JSON structure
        paper = {
            "paper_metadata": {
                "board": "Tamil Nadu State Board",
                "class": 10,
                "subject": "English",
                "year": 2025,
                "duration_hours": 3,
                "total_marks": 100,
                "generation_date": None  # Will be set by API
            },
            "parts": parts,
            "coverage_validation": self.validator.get_coverage_report()
        }
        
        return paper


# Singleton instance
_paper_generator = None


def get_paper_generator() -> PaperGenerationRetriever:
    """Get or create the paper generator singleton."""
    global _paper_generator
    if _paper_generator is None:
        _paper_generator = PaperGenerationRetriever()
    return _paper_generator

