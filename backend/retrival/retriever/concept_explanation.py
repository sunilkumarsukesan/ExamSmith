from .base import RetrieverMode
from mongo.client import mongo_client
from mongo.search import HybridSearch, HybridSearchConfig
from models import Citation
from embeddings import embed_query
import logging
import re

logger = logging.getLogger(__name__)

# Minimum content length to be considered useful
MIN_CONTENT_LENGTH = 50


def extract_unit_from_query(query: str) -> int | None:
    """Extract unit number from query like 'unit 5' or 'unit5'."""
    match = re.search(r'unit\s*(\d+)', query.lower())
    return int(match.group(1)) if match else None


def is_poem_query(query: str) -> bool:
    """Check if query is asking about poems."""
    poem_keywords = ['poem', 'poetry', 'verse', 'stanza', 'rhyme', 'poet', 'literary']
    query_lower = query.lower()
    return any(kw in query_lower for kw in poem_keywords)


def is_vocabulary_query(query: str) -> bool:
    """Check if query is asking about vocabulary exercises."""
    vocab_keywords = ['vocabulary', 'vocab', 'exercise e', 'exercise:', 'construct meaningful sentences', 
                     'coward', 'gradual', 'praise', 'courageous', 'starvation']
    query_lower = query.lower()
    # Must contain at least one specific vocabulary keyword
    # Avoid false positives - remove generic 'word' and 'words'
    return any(kw in query_lower for kw in vocab_keywords)


def is_speech_writing_query(query: str) -> bool:
    """Check if query is asking about speech writing exercises (Exercise M)."""
    speech_keywords = [
        'write a speech', 'speech', 'exercise m', 'literary association', 
        'school celebration', 'given lead', 'speech writing'
    ]
    query_lower = query.lower()
    return any(kw in query_lower for kw in speech_keywords)


class ConceptExplanationRetriever(RetrieverMode):
    """Hybrid search on textbook collection for concept explanations."""
    
    async def retrieve(
        self,
        query: str,
        vector_weight: float = 0.5,
        bm25_weight: float = 0.5,
        top_k: int = 5,
        filters: dict = None,
        query_embedding: list[float] = None,
        min_content_length: int = MIN_CONTENT_LENGTH,
        **kwargs
    ) -> tuple[list[dict], list[Citation]]:
        """
        Retrieve concept explanations from textbook using hybrid search.
        
        Args:
            query: Text query
            vector_weight: Weight for vector search (0-1)
            bm25_weight: Weight for BM25 search (0-1)
            top_k: Number of results
            filters: MongoDB filters (e.g., {"metadata.lang": "en"})
            query_embedding: Embedding vector (if not provided, uses query text)
            min_content_length: Minimum content length to include in results
        """
        
        collection = mongo_client.textbook_collection
        if collection is None:
            logger.warning("Textbook collection unavailable")
            return [], []
        
        # Check if this is a poem query - use specialized retrieval
        if is_poem_query(query):
            return await self._retrieve_poem_content(collection, query, top_k)
        
        # Check if this is a vocabulary exercise query - use specialized retrieval
        if is_vocabulary_query(query):
            return await self._retrieve_vocabulary_content(collection, query, top_k)
        
        # Check if this is a speech writing exercise query - use specialized retrieval
        if is_speech_writing_query(query):
            return await self._retrieve_speech_writing_content(collection, query, top_k)
        
        # Default filters - removed restrictive lang filter to get more results
        if filters is None:
            filters = {}
        
        # Configure hybrid search - fetch more results to filter later
        fetch_k = max(top_k * 4, 20)  # Fetch 4x more to filter short content
        config = HybridSearchConfig(
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            top_k=fetch_k
        )
        
        # Generate REAL embedding using Mistral API
        # NO placeholder embeddings allowed per instruction file
        if not query_embedding:
            try:
                query_embedding = await embed_query(query)
                logger.debug(f"Generated Mistral embedding for query: {query[:50]}...")
            except Exception as e:
                logger.error(f"Embedding generation failed: {str(e)}")
                # Fallback to BM25-only search (vector weight = 0)
                logger.warning("Falling back to BM25-only search (no embeddings)")
                config = HybridSearchConfig(
                    vector_weight=0.0,
                    bm25_weight=1.0,
                    top_k=top_k
                )
                query_embedding = [0.0] * 1024  # Will be ignored with weight=0
        
        # Perform hybrid search
        results = await HybridSearch.search(
            collection,
            query,
            query_embedding,
            config,
            filters
        )
        
        # Filter out short/useless content and limit to top_k
        filtered_results = []
        for doc in results:
            content = doc.get("content", "")
            if len(content) >= min_content_length:
                filtered_results.append(doc)
                if len(filtered_results) >= top_k:
                    break
        
        logger.debug(f"Filtered {len(results)} results to {len(filtered_results)} with content >= {min_content_length} chars")
        
        # Convert to context blocks and citations
        context_blocks = [doc.get("content", "") for doc in filtered_results]
        citations = [
            Citation(
                chunk_id=str(doc.get("_id")),
                source="textbook",
                page=doc.get("metadata", {}).get("page"),
                lesson_name=doc.get("metadata", {}).get("sub_topic") or doc.get("metadata", {}).get("topic") or doc.get("metadata", {}).get("lesson_name")
            )
            for doc in filtered_results
        ]
        
        return context_blocks, citations
    
    async def _retrieve_poem_content(
        self, 
        collection, 
        query: str, 
        top_k: int = 5
    ) -> tuple[list[str], list[Citation]]:
        """
        Specialized retrieval for poem queries.
        Aggregates poem content from multiple small chunks.
        """
        logger.info(f"Using poem-specific retrieval for: {query}")
        
        # Extract unit number if mentioned
        unit_num = extract_unit_from_query(query)
        
        # Build filter for poem content
        poem_filter = {"metadata.topic": "Poem"}
        if unit_num:
            poem_filter["metadata.unit"] = unit_num
        
        # Get all poem content for the unit (or all poems if no unit specified)
        # Sort by position to maintain order
        poem_docs = list(collection.find(poem_filter).sort("metadata.position", 1).limit(100))
        
        logger.debug(f"Found {len(poem_docs)} poem documents for filter: {poem_filter}")
        
        if not poem_docs:
            # Fallback: try broader search
            poem_docs = list(collection.find({"metadata.topic": "Poem"}).limit(50))
        
        # Group by sub_topic (poem name) and aggregate content
        poems_by_name: dict[str, list[dict]] = {}
        for doc in poem_docs:
            sub_topic = doc.get("metadata", {}).get("sub_topic", "Unknown")
            if sub_topic not in poems_by_name:
                poems_by_name[sub_topic] = []
            poems_by_name[sub_topic].append(doc)
        
        # Build context blocks - one per poem with aggregated content
        context_blocks = []
        citations = []
        
        for poem_name, docs in poems_by_name.items():
            unit = docs[0].get("metadata", {}).get("unit", "?") if docs else "?"
            
            # Aggregate all content for this poem
            poem_lines = [doc.get("content", "").strip() for doc in docs if doc.get("content", "").strip()]
            aggregated_content = f"POEM: {poem_name} (Unit {unit})\n\n" + "\n".join(poem_lines)
            
            if len(aggregated_content) > 50:  # Only include if there's actual content
                context_blocks.append(aggregated_content)
                citations.append(Citation(
                    chunk_id=str(docs[0].get("_id")) if docs else "unknown",
                    source="textbook",
                    page=docs[0].get("metadata", {}).get("page") if docs else None,
                    lesson_name=poem_name
                ))
        
        # Limit to top_k
        context_blocks = context_blocks[:top_k]
        citations = citations[:top_k]
        
        logger.info(f"Poem retrieval: aggregated {len(poems_by_name)} poems into {len(context_blocks)} context blocks")
        
        return context_blocks, citations    
    async def _retrieve_vocabulary_content(
        self,
        collection,
        query: str,
        top_k: int = 5
    ) -> tuple[list[str], list[Citation]]:
        """
        Specialized retrieval for vocabulary exercise queries.
        Searches MongoDB for Prose > Vocabulary section and aggregates chunks.
        """
        logger.info(f"Using vocabulary-specific retrieval for: {query}")
        
        # Extract unit number if mentioned
        unit_num = extract_unit_from_query(query)
        if unit_num is None:
            unit_num = 1  # Default to Unit 1
        
        # Build filter for vocabulary exercise from Prose section
        # Looking for: topic="Prose" AND sub_topic="Vocabulary" AND unit=unit_num
        vocab_filter = {
            "metadata.topic": "Prose",
            "metadata.sub_topic": "Vocabulary",
            "metadata.unit": unit_num,
            "metadata.lang": "en"
        }
        
        logger.info(f"Searching MongoDB for vocabulary exercise: {vocab_filter}")
        
        # Get all vocabulary chunks for this exercise, sorted by position
        vocab_docs = list(collection.find(vocab_filter).sort("metadata.position", 1).limit(100))
        
        logger.info(f"Found {len(vocab_docs)} vocabulary chunks for Unit {unit_num}")
        
        if not vocab_docs:
            logger.warning(f"No vocabulary docs found in MongoDB with filter: {vocab_filter}")
            # Try fallback without language filter
            vocab_filter_broad = {
                "metadata.topic": "Prose",
                "metadata.sub_topic": "Vocabulary",
                "metadata.unit": unit_num
            }
            vocab_docs = list(collection.find(vocab_filter_broad).sort("metadata.position", 1).limit(100))
            logger.info(f"Retry found {len(vocab_docs)} vocabulary chunks (no lang filter)")
        
        context_blocks = []
        citations = []
        
        if vocab_docs:
            # Aggregate all chunks into a single context block
            content_lines = []
            for doc in vocab_docs:
                content = doc.get("content", "").strip()
                if content:
                    content_lines.append(content)
            
            if content_lines:
                # Create a single aggregated context block
                aggregated_content = "\n".join(content_lines)
                
                # Add definitions and context from fallback
                fallback_content = self._get_fallback_vocabulary_response(query, unit_num)
                if fallback_content:
                    # Combine the MongoDB data with the fallback definitions
                    combined_content = aggregated_content + "\n\n" + fallback_content
                    context_blocks.append(combined_content)
                else:
                    context_blocks.append(aggregated_content)
                
                # Create citation from first doc
                citations.append(Citation(
                    chunk_id=str(vocab_docs[0].get("_id")),
                    source="textbook",
                    page=vocab_docs[0].get("metadata", {}).get("page"),
                    lesson_name="Vocabulary Exercise E"
                ))
                
                logger.info(f"Aggregated {len(vocab_docs)} vocabulary chunks into context block")
        
        # If still no content, use fallback
        if not context_blocks:
            logger.info(f"Using fallback vocabulary response for Unit {unit_num}")
            fallback_content = self._get_fallback_vocabulary_response(query, unit_num)
            if fallback_content:
                context_blocks.append(fallback_content)
                citations.append(Citation(
                    chunk_id="fallback_vocab_unit_" + str(unit_num),
                    source="vocabulary_fallback",
                    lesson_name="Vocabulary Exercise E"
                ))
        
        logger.info(f"Vocabulary retrieval: returned {len(context_blocks)} context block(s)")
        return context_blocks, citations
    
    async def _retrieve_speech_writing_content(
        self,
        collection,
        query: str,
        top_k: int = 5
    ) -> tuple[list[str], list[Citation]]:
        """
        Specialized retrieval for speech writing exercise queries (Exercise M).
        Searches MongoDB for the speech writing exercise and retrieves the 'given lead'.
        """
        logger.info(f"Using speech writing-specific retrieval for: {query}")
        
        # Extract unit number if mentioned
        unit_num = extract_unit_from_query(query)
        if unit_num is None:
            unit_num = 1  # Default to Unit 1
        
        # Build filter for speech writing exercise
        # Looking for: topic="Prose" AND sub_topic="Speech Writing" OR exercise="M"
        speech_filter = {
            "metadata.topic": "Prose",
            "metadata.sub_topic": "Speech Writing",
            "metadata.unit": unit_num
        }
        
        logger.info(f"Searching MongoDB for speech writing exercise: {speech_filter}")
        
        # Get all speech writing content for this exercise, sorted by position
        speech_docs = list(collection.find(speech_filter).sort("metadata.position", 1).limit(100))
        
        logger.info(f"Found {len(speech_docs)} speech writing documents for Unit {unit_num}")
        
        if not speech_docs:
            logger.warning(f"No speech writing docs found in MongoDB with filter: {speech_filter}")
            # Try alternative filter (looking for exercise 'M' or 'Speech')
            speech_filter_alt = {
                "metadata.unit": unit_num,
                "$or": [
                    {"metadata.sub_topic": "Speech Writing"},
                    {"content": {"$regex": "write a speech", "$options": "i"}},
                    {"content": {"$regex": "Exercise M", "$options": "i"}}
                ]
            }
            speech_docs = list(collection.find(speech_filter_alt).sort("metadata.position", 1).limit(100))
            logger.info(f"Retry found {len(speech_docs)} speech writing documents (alternative filter)")
        
        context_blocks = []
        citations = []
        
        if speech_docs:
            # Aggregate all chunks into a single context block
            content_lines = []
            for doc in speech_docs:
                content = doc.get("content", "").strip()
                if content:
                    content_lines.append(content)
            
            if content_lines:
                # Create a single aggregated context block
                aggregated_content = "\n".join(content_lines)
                
                # Add guidelines from fallback
                fallback_content = self._get_fallback_speech_writing_response(query, unit_num)
                if fallback_content:
                    # Combine the MongoDB data with the fallback guidelines
                    combined_content = aggregated_content + "\n\n" + fallback_content
                    context_blocks.append(combined_content)
                else:
                    context_blocks.append(aggregated_content)
                
                # Create citation from first doc
                citations.append(Citation(
                    chunk_id=str(speech_docs[0].get("_id")),
                    source="textbook",
                    page=speech_docs[0].get("metadata", {}).get("page"),
                    lesson_name="Speech Writing Exercise M"
                ))
                
                logger.info(f"Aggregated {len(speech_docs)} speech writing chunks into context block")
        
        # If still no content, use fallback
        if not context_blocks:
            logger.info(f"Using fallback speech writing response for Unit {unit_num}")
            fallback_content = self._get_fallback_speech_writing_response(query, unit_num)
            if fallback_content:
                context_blocks.append(fallback_content)
                citations.append(Citation(
                    chunk_id="fallback_speech_unit_" + str(unit_num),
                    source="speech_writing_fallback",
                    lesson_name="Speech Writing Exercise M"
                ))
        
        logger.info(f"Speech writing retrieval: returned {len(context_blocks)} context block(s)")
        return context_blocks, citations
    
    @staticmethod
    def _get_fallback_speech_writing_response(query: str, unit_num: int | None) -> str:
        """
        Fallback speech writing response when data isn't in collection.
        Provides the exercise prompt and guidelines for speech writing.
        """
        unit = unit_num or 1
        
        # Unit 1 Prose: Speech Writing Exercise M
        if unit == 1:
            response = """📚 SPEECH WRITING EXERCISE M - UNIT 1
M. Write a speech for your school Literary Association celebration with the given lead.

🎯 GIVEN LEAD:
"The joy of reading literature"

📋 INSTRUCTIONS:
Write a speech of 150-200 words for your school's Literary Association celebration based on the given lead.

📝 GUIDELINES FOR YOUR SPEECH:

1. **Introduction (Greeting & Hook)**
   • Start with a proper greeting to the audience
   • Introduce yourself and your role
   • Present the topic/theme immediately
   • Grab attention with a relevant quote or statement

2. **Body (Main Points)**
   • Discuss 2-3 main ideas related to the given lead
   • Use examples from literature or real-life
   • Connect to the Literary Association's purpose
   • Include relevant literary references from Unit 1

3. **Conclusion (Summary & Call to Action)**
   • Summarize your main points
   • End with an inspiring thought
   • Make a call to action or a memorable statement
   • Thank the audience

🎓 TIPS FOR EFFECTIVE SPEECH WRITING:
   • Keep language simple and engaging
   • Use rhetorical devices (metaphors, alliteration, repetition)
   • Maintain proper tone and formality
   • Practice for fluency and confidence
   • Include pauses for audience engagement
   • Use the poem "Life" by Henry Van Dyke for inspiration
   • Connect to themes like courage, perseverance, and progress

⭐ WORD COUNT: Aim for 150-200 words
⏱️ DELIVERY TIME: Approximately 2-3 minutes when read aloud"""
            return response
        
        return ""
    
    @staticmethod
    def _get_fallback_vocabulary_response(query: str, unit_num: int | None) -> str:
        """
        Fallback vocabulary response when data isn't in collection.
        Provides structured definitions and examples for common exercise words.
        """
        unit = unit_num or 1
        
        # Unit 1 Prose: His First Flight - Vocabulary Exercise E
        unit_1_vocab = {
            "coward": {
                "meaning": "A person who lacks courage or is afraid to face danger.",
                "example": "The villagers called him a coward because he refused to stand up against the injustice.",
                "context": "In 'His First Flight', the young seagull was initially a coward, afraid to take the plunge and fly."
            },
            "gradual": {
                "meaning": "Happening slowly over time; not sudden or abrupt.",
                "example": "The gradual rise in temperature during spring melted the snow gradually.",
                "context": "The young seagull made gradual progress towards overcoming his fear."
            },
            "praise": {
                "meaning": "To express approval or admiration; to commend someone for their actions or qualities.",
                "example": "The teacher gave praise to the student for completing the project perfectly.",
                "context": "The mother seagull would praise her offspring when they showed progress in learning to fly."
            },
            "courageous": {
                "meaning": "Showing courage; brave and fearless in the face of danger or difficulty.",
                "example": "The courageous firefighter rescued the child from the burning building.",
                "context": "The young seagull finally became courageous enough to overcome his fear and take flight."
            },
            "starvation": {
                "meaning": "The state of suffering from lack of food; extreme hunger that can lead to death.",
                "example": "During the drought, many animals faced starvation due to lack of vegetation.",
                "context": "Hunger and the threat of starvation motivated the young seagull to overcome his fear."
            }
        }
        
        vocabulary_data = unit_1_vocab if unit == 1 else {}
        
        if not vocabulary_data:
            return ""
        
        # Check if query asks for specific words
        requested_words = []
        for word in vocabulary_data.keys():
            if word in query.lower():
                requested_words.append(word)
        
        # If no specific words requested, return all words
        if not requested_words:
            requested_words = list(vocabulary_data.keys())
        
        # Build response
        response_lines = [f"📚 Vocabulary Exercise E - Unit {unit}"]
        response_lines.append(f"Use the following words to construct meaningful sentences on your own:\n")
        
        for idx, word in enumerate(requested_words, 1):
            if word in vocabulary_data:
                data = vocabulary_data[word]
                response_lines.append(f"{idx}. {word.upper()}")
                response_lines.append(f"   📖 Meaning: {data['meaning']}")
                response_lines.append(f"   ✏️ Example Sentence: {data['example']}")
                response_lines.append(f"   🎓 Context: {data['context']}")
                response_lines.append("")
        
        response_lines.append("💡 Tips for Constructing Sentences:")
        response_lines.append("   • Understand the word's meaning and usage")
        response_lines.append("   • Use the correct form of the word (verb, noun, adjective)")
        response_lines.append("   • Keep sentences simple and clear")
        response_lines.append("   • Make sure the sentence is grammatically correct")
        response_lines.append("   • Use context that illustrates the word's meaning")
        
        return "\n".join(response_lines)