"""
Debug script to see full content being retrieved for chat.
"""

import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).parent))

from mongo.client import mongo_client
from retriever.concept_explanation import ConceptExplanationRetriever


async def test_retrieval():
    print("\n" + "=" * 70)
    print("Testing Textbook Retrieval - Full Content")
    print("=" * 70)
    
    retriever = ConceptExplanationRetriever()
    
    queries = [
        "explain poem in unit 5",
        "The Grumble Family poem meaning",
        "Life poem unit 5 themes",
    ]
    
    for query in queries:
        print(f"\n\nQuery: '{query}'")
        print("-" * 70)
        
        blocks, citations = await retriever.retrieve(
            query=query,
            top_k=3,
            filters={"metadata.lang": "en"}
        )
        
        print(f"Retrieved {len(blocks)} blocks:")
        
        for i, block in enumerate(blocks, 1):
            print(f"\n[Block {i}] (length: {len(block)} chars)")
            print(block[:800])
            if len(block) > 800:
                print("...")


def check_textbook_content():
    """Check what content exists for poems in the textbook."""
    print("\n" + "=" * 70)
    print("Checking Textbook Content for Poems")
    print("=" * 70)
    
    coll = mongo_client.textbook_collection
    if coll is None:
        print("Collection unavailable")
        return
    
    # Search for poem-related content
    poem_docs = list(coll.find(
        {"content": {"$regex": "poem|poetry|verse|stanza", "$options": "i"}}
    ).limit(10))
    
    print(f"\nFound {len(poem_docs)} documents with poem-related content:")
    
    for i, doc in enumerate(poem_docs, 1):
        content = doc.get("content", "")
        metadata = doc.get("metadata", {})
        print(f"\n[{i}] Unit: {metadata.get('unit')} | Lesson: {metadata.get('lesson_name', 'N/A')}")
        print(f"    Content ({len(content)} chars): {content[:300]}...")
    
    # Also check for specific unit 5 content
    print("\n" + "-" * 70)
    print("Unit 5 documents:")
    
    unit5_docs = list(coll.find({"metadata.unit": 5}).limit(10))
    print(f"Found {len(unit5_docs)} documents for Unit 5")
    
    for i, doc in enumerate(unit5_docs, 1):
        content = doc.get("content", "")
        print(f"\n[{i}] Content ({len(content)} chars): {content[:400]}...")


if __name__ == "__main__":
    check_textbook_content()
    asyncio.run(test_retrieval())
    
    print("\n" + "=" * 70)
    print("Done")
    print("=" * 70)
