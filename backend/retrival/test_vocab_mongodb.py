#!/usr/bin/env python3
"""
Quick test to verify vocabulary MongoDB queries work correctly.
This tests the metadata filters for vocabulary content.
"""

import asyncio
import logging
from retriever.concept_explanation import is_vocabulary_query, extract_unit_from_query
from mongo.client import mongo_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test queries
test_queries = [
    "Can you explain the Vocabulary E exercise in Unit 1?",
    "Help me understand: E. Use the following words to construct meaningful sentences on your own",
    "What does coward mean in Unit 1?",
    "gradual and praise - vocabulary exercise",
    "Explain exercise E: coward, gradual, praise, courageous, starvation",
]

def test_vocabulary_detection():
    """Test vocabulary query detection."""
    print("\n" + "="*60)
    print("VOCABULARY DETECTION TEST")
    print("="*60)
    
    for query in test_queries:
        is_vocab = is_vocabulary_query(query)
        unit = extract_unit_from_query(query)
        print(f"\nQuery: {query[:50]}...")
        print(f"  → Is Vocabulary: {is_vocab}")
        print(f"  → Unit: {unit if unit else 'Not specified (defaults to 1)'}")


def test_mongodb_filter():
    """Test that the vocabulary filter will find the right documents."""
    print("\n" + "="*60)
    print("MONGODB VOCABULARY FILTER TEST")
    print("="*60)
    
    collection = mongo_client.textbook_collection
    if collection is None:
        logger.error("❌ Cannot connect to MongoDB!")
        return
    
    # The filter we're using in the retriever
    vocab_filter = {
        "metadata.topic": "Prose",
        "metadata.sub_topic": "Vocabulary",
        "metadata.unit": 1,
        "metadata.lang": "en"
    }
    
    print(f"\nSearching with filter: {vocab_filter}")
    
    try:
        # Count documents
        count = collection.count_documents(vocab_filter)
        print(f"  → Found {count} documents matching the filter")
        
        if count > 0:
            # Show sample documents
            docs = list(collection.find(vocab_filter).sort("metadata.position", 1).limit(10))
            print(f"\n  Sample documents (sorted by position):")
            for i, doc in enumerate(docs, 1):
                content = doc.get("content", "")[:50]
                position = doc.get("metadata", {}).get("position")
                print(f"    {i}. Position {position}: {content}...")
        else:
            print("  ⚠️  No documents found! Checking available data...")
            
            # Debug: Check what's actually in the collection
            print("\n  Checking metadata structure...")
            sample = collection.find_one()
            if sample:
                metadata = sample.get("metadata", {})
                print(f"  Available fields in metadata: {list(metadata.keys())}")
                
                # Check Prose documents
                prose_count = collection.count_documents({"metadata.topic": "Prose"})
                vocab_count = collection.count_documents({"metadata.sub_topic": "Vocabulary"})
                unit1_count = collection.count_documents({"metadata.unit": 1})
                
                print(f"\n  Document counts:")
                print(f"    - With topic='Prose': {prose_count}")
                print(f"    - With sub_topic='Vocabulary': {vocab_count}")
                print(f"    - With unit=1: {unit1_count}")
    
    except Exception as e:
        logger.error(f"❌ MongoDB query failed: {str(e)}")


async def test_vocabulary_retrieval():
    """Test the actual vocabulary retrieval."""
    print("\n" + "="*60)
    print("VOCABULARY RETRIEVAL TEST")
    print("="*60)
    
    from retriever.concept_explanation import ConceptExplanationRetriever
    
    retriever = ConceptExplanationRetriever()
    
    test_query = "Can you explain the Vocabulary E exercise in Unit 1? Help me understand coward, gradual, praise, courageous, starvation"
    
    print(f"\nQuery: {test_query}")
    print("\nRetrieving...")
    
    try:
        context_blocks, citations = await retriever.retrieve(
            query=test_query,
            top_k=10
        )
        
        print(f"\n✅ Retrieved {len(context_blocks)} context block(s)")
        
        for i, block in enumerate(context_blocks, 1):
            print(f"\n  Block {i}:")
            print(f"  Content preview: {block[:100]}...")
            if len(block) > 100:
                print(f"  Full length: {len(block)} characters")
        
        print(f"\nCitations: {len(citations)}")
        for citation in citations:
            print(f"  - {citation.source}: {citation.lesson_name}")
    
    except Exception as e:
        logger.error(f"❌ Retrieval failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run tests
    test_vocabulary_detection()
    test_mongodb_filter()
    
    # Run async retrieval test
    asyncio.run(test_vocabulary_retrieval())
    
    print("\n" + "="*60)
    print("TESTS COMPLETE")
    print("="*60)
