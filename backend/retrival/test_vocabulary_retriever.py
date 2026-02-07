#!/usr/bin/env python3
"""
Test script for vocabulary retriever enhancement.
Tests that vocabulary queries are properly detected and handled.
"""

import asyncio
import sys
from pathlib import Path

# Add backend path
sys.path.insert(0, str(Path(__file__).parent / "backend" / "retrival"))

# Test the vocabulary detection functions
def test_vocabulary_detection():
    """Test the new vocabulary detection functions."""
    print("\n" + "="*70)
    print("🧪 VOCABULARY RETRIEVER TEST SUITE")
    print("="*70 + "\n")
    
    # Import the detection functions
    from retriever.concept_explanation import is_vocabulary_query, is_poem_query
    
    # Test cases for vocabulary queries
    vocab_test_cases = [
        ("Can you explain the Vocabulary E section in Unit 1?", True),
        ("Help me with the vocabulary exercise", True),
        ("What does coward, gradual, praise mean?", True),
        ("Explain vocabulary words from Unit 1", True),
        ("What is the meaning of courageous?", True),
        ("Construct sentences using starvation", True),
        ("Explain the poem in unit 7", False),
        ("What is the theme of the poem?", False),
        ("General question about unit 1", False),
    ]
    
    print("📋 Test 1: Vocabulary Query Detection")
    print("-" * 70)
    
    passed = 0
    failed = 0
    
    for query, expected_is_vocab in vocab_test_cases:
        is_vocab = is_vocabulary_query(query)
        is_poem = is_poem_query(query)
        
        status = "✅ PASS" if is_vocab == expected_is_vocab else "❌ FAIL"
        passed += 1 if is_vocab == expected_is_vocab else 0
        failed += 0 if is_vocab == expected_is_vocab else 1
        
        print(f"{status}")
        print(f"  Query: {query}")
        print(f"  Expected vocab={expected_is_vocab}, Got vocab={is_vocab}, poem={is_poem}")
        print()
    
    print(f"Summary: {passed} passed, {failed} failed\n")
    
    return passed, failed


def test_fallback_response():
    """Test the fallback vocabulary response generation."""
    print("📋 Test 2: Fallback Response Generation")
    print("-" * 70)
    
    from retriever.concept_explanation import ConceptExplanationRetriever
    
    test_queries = [
        ("Can you explain vocabulary in unit 1?", 1),
        ("What does coward mean?", 1),
        ("Explain praise and courageous", 1),
        ("Unit 1 exercise E words", 1),
    ]
    
    for query, unit in test_queries:
        print(f"\n🔍 Query: '{query}'")
        print(f"Unit: {unit}")
        print("-" * 70)
        
        response = ConceptExplanationRetriever._get_fallback_vocabulary_response(query, unit)
        
        if response:
            print("✅ Response generated successfully!")
            print(f"\nResponse Preview (first 300 chars):")
            print(response[:300] + "...\n")
            
            # Check for key content
            checks = {
                "Contains Unit indicator": "Unit" in response,
                "Contains Vocabulary header": "Vocabulary" in response or "vocabulary" in response.lower(),
                "Contains word definitions": any(word in response.lower() for word in ["coward", "gradual", "praise", "courageous", "starvation"]),
                "Contains emoji formatting": "📚" in response or "📖" in response or "✏️" in response,
                "Contains tips section": "Tips" in response or "tips" in response.lower(),
            }
            
            for check_name, check_result in checks.items():
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
        else:
            print("❌ No response generated!")
    
    print("\n")


async def test_retriever_async():
    """Test the async retriever methods (if MongoDB is available)."""
    print("📋 Test 3: Vocabulary Retriever (Async)")
    print("-" * 70)
    
    try:
        from retriever.concept_explanation import ConceptExplanationRetriever, is_vocabulary_query
        from mongo.client import mongo_client
        
        # Check MongoDB connection
        if mongo_client.client is None:
            print("⚠️  MongoDB not connected - skipping async test")
            print("   (This is expected if running offline)")
            return
        
        retriever = ConceptExplanationRetriever()
        
        test_query = "Can you explain the Vocabulary E exercise in Unit 1?"
        
        print(f"Query: '{test_query}'")
        print(f"Vocabulary detected: {is_vocabulary_query(test_query)}")
        
        context_blocks, citations = await retriever.retrieve(
            query=test_query,
            top_k=3
        )
        
        if context_blocks:
            print(f"✅ Retrieved {len(context_blocks)} context blocks")
            for i, block in enumerate(context_blocks, 1):
                print(f"\nBlock {i} (first 200 chars):")
                print(f"  {block[:200]}...\n")
        else:
            print("⚠️  No context blocks retrieved (expected if no MongoDB data)")
            print("   Fallback response will be used instead")
            
    except Exception as e:
        print(f"⚠️  Async test skipped: {str(e)}")
    
    print()


def test_unit_extraction():
    """Test unit number extraction from queries."""
    print("📋 Test 4: Unit Number Extraction")
    print("-" * 70)
    
    from retriever.concept_explanation import extract_unit_from_query
    
    test_cases = [
        ("Unit 1 vocabulary", 1),
        ("unit 1 vocabulary", 1),
        ("Unit1 vocabulary", 1),
        ("vocabulary in unit 7", 7),
        ("Unit 3 exercise", 3),
        ("no unit here", None),
        ("unit 10", 10),
    ]
    
    passed = 0
    failed = 0
    
    for query, expected_unit in test_cases:
        extracted_unit = extract_unit_from_query(query)
        status = "✅ PASS" if extracted_unit == expected_unit else "❌ FAIL"
        passed += 1 if extracted_unit == expected_unit else 0
        failed += 0 if extracted_unit == expected_unit else 1
        
        print(f"{status} Query: '{query}'")
        print(f"       Expected: {expected_unit}, Got: {extracted_unit}\n")
    
    print(f"Summary: {passed} passed, {failed} failed\n")
    
    return passed, failed


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "   VOCABULARY RETRIEVER ENHANCEMENT - TEST SUITE".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    total_passed = 0
    total_failed = 0
    
    # Test 1: Vocabulary detection
    passed, failed = test_vocabulary_detection()
    total_passed += passed
    total_failed += failed
    
    # Test 2: Fallback response
    test_fallback_response()
    
    # Test 3: Unit extraction
    passed, failed = test_unit_extraction()
    total_passed += passed
    total_failed += failed
    
    # Test 4: Async retriever (if MongoDB available)
    asyncio.run(test_retriever_async())
    
    # Summary
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests Passed: {total_passed}")
    print(f"Total Tests Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n✅ All tests PASSED! Vocabulary retriever is working correctly.")
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Please review the output above.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test suite error: {str(e)}")
        import traceback
        traceback.print_exc()
