#!/usr/bin/env python3
"""Quick test to verify vocabulary retriever is working."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "backend" / "retrival"))

async def test_vocabulary_retrieval():
    """Test vocabulary retrieval directly."""
    print("\n" + "="*70)
    print("🧪 VOCABULARY RETRIEVER - QUICK TEST")
    print("="*70 + "\n")
    
    from retriever.concept_explanation import (
        ConceptExplanationRetriever,
        is_vocabulary_query,
        extract_unit_from_query
    )
    
    # Test cases
    test_queries = [
        "Can you explain the Vocabulary E exercise in Unit 1?",
        "What does coward mean?",
        "Help me with vocabulary unit 1",
        "Explain praise and courageous from vocabulary",
    ]
    
    print("Testing Vocabulary Detection:")
    print("-" * 70)
    
    for query in test_queries:
        is_vocab = is_vocabulary_query(query)
        unit = extract_unit_from_query(query)
        print(f"✓ Query: '{query}'")
        print(f"  Vocab detected: {is_vocab} | Unit: {unit}\n")
    
    print("\nTesting Vocabulary Retrieval:")
    print("-" * 70)
    
    retriever = ConceptExplanationRetriever()
    
    query = "Can you explain the Vocabulary E exercise in Unit 1?"
    print(f"\nQuery: '{query}'\n")
    
    try:
        context_blocks, citations = await retriever.retrieve(
            query=query,
            top_k=1
        )
        
        if context_blocks:
            print(f"✅ Retrieved {len(context_blocks)} content block(s)\n")
            print("Content Preview:")
            print("-" * 70)
            for i, block in enumerate(context_blocks, 1):
                print(f"\nBlock {i}:")
                print(block[:500])
                if len(block) > 500:
                    print("...")
        else:
            print("❌ No content retrieved!")
            print("\nTesting Fallback Response:")
            fallback = ConceptExplanationRetriever._get_fallback_vocabulary_response(query, 1)
            if fallback:
                print("✅ Fallback response generated!\n")
                print(fallback[:500])
                if len(fallback) > 500:
                    print("...")
            else:
                print("❌ No fallback response!")
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("✅ Test Complete")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_vocabulary_retrieval())
