"""
Debug script to check textbook retrieval and chat context.
"""

import sys
from pathlib import Path
import asyncio
import json

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from mongo.client import mongo_client
from retriever.concept_explanation import ConceptExplanationRetriever
from config import settings

def check_mongo_connection():
    """Check MongoDB connection and collections."""
    print("\n" + "=" * 70)
    print("MongoDB Connection Check")
    print("=" * 70)
    
    if not mongo_client.client:
        print("✗ MongoDB client not connected")
        return False
    
    print("✓ MongoDB client connected")
    
    # Check textbook collection
    print(f"\nTextbook Database: {settings.mongodb_db_textbook}")
    print(f"Textbook Collection: {settings.mongodb_collection_textbook}")
    
    textbook_coll = mongo_client.textbook_collection
    if textbook_coll is None:
        print("✗ Textbook collection unavailable")
        return False
    
    # Count documents
    doc_count = textbook_coll.count_documents({})
    print(f"\n✓ Textbook collection has {doc_count} documents")
    
    if doc_count == 0:
        print("⚠ WARNING: Textbook collection is EMPTY!")
        print("  You need to run the injection service to populate the textbook data")
        return False
    
    # Sample a document
    sample = textbook_coll.find_one()
    if sample:
        print(f"\nSample document structure:")
        print(f"  _id: {sample.get('_id')}")
        print(f"  content length: {len(sample.get('content', ''))}")
        print(f"  metadata: {json.dumps(sample.get('metadata', {}), default=str, indent=4)}")
        print(f"  embedding present: {'embedding' in sample}")
        if 'embedding' in sample:
            emb = sample.get('embedding', [])
            print(f"  embedding dimension: {len(emb)}")
    
    return True


def check_unit_5_content():
    """Check if Unit 5 content exists in textbook."""
    print("\n" + "=" * 70)
    print("Checking Unit 5 Content in Textbook")
    print("=" * 70)
    
    textbook_coll = mongo_client.textbook_collection
    if textbook_coll is None:
        print("✗ Textbook collection unavailable")
        return
    
    # Search for unit 5 content
    unit_5_docs = list(textbook_coll.find({"metadata.unit": 5}).limit(5))
    print(f"\nDocuments with metadata.unit = 5: {len(unit_5_docs)}")
    
    if unit_5_docs:
        for i, doc in enumerate(unit_5_docs, 1):
            content_preview = doc.get('content', '')[:200]
            print(f"\n[{i}] {doc.get('metadata', {}).get('lesson_name', 'Unknown')}")
            print(f"    Content: {content_preview}...")
    else:
        # Try other queries
        print("\nTrying alternative searches...")
        
        # Search by text
        text_search = list(textbook_coll.find(
            {"content": {"$regex": "unit 5|poem|poetry", "$options": "i"}}
        ).limit(5))
        print(f"Documents containing 'unit 5' or 'poem': {len(text_search)}")
        
        # List all unique units
        units = textbook_coll.distinct("metadata.unit")
        print(f"\nUnique units in textbook: {units}")
        
        # List all lesson names
        lessons = textbook_coll.distinct("metadata.lesson_name")
        print(f"\nLesson names: {lessons[:10]}...")


async def test_retrieval(query: str):
    """Test retrieval for a query."""
    print("\n" + "=" * 70)
    print(f"Testing Retrieval for: '{query}'")
    print("=" * 70)
    
    try:
        retriever = ConceptExplanationRetriever()
        
        context_blocks, citations = await retriever.retrieve(
            query=query,
            vector_weight=0.5,
            bm25_weight=0.5,
            top_k=5,
            filters={"metadata.lang": "en"}
        )
        
        print(f"\n✓ Retrieved {len(context_blocks)} context blocks")
        print(f"✓ Got {len(citations)} citations")
        
        if context_blocks:
            for i, block in enumerate(context_blocks, 1):
                print(f"\n[Block {i}] {block[:300]}...")
        else:
            print("\n⚠ No context blocks returned!")
            print("  Possible issues:")
            print("  1. Textbook collection is empty")
            print("  2. No vector/BM25 index created on MongoDB Atlas")
            print("  3. Embedding generation failed")
        
        if citations:
            print("\n\nCitations:")
            for c in citations:
                print(f"  - {c.lesson_name} (chunk: {c.chunk_id})")
    
    except Exception as e:
        print(f"\n✗ Retrieval failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    print("\n" + "=" * 70)
    print("ExamSmith Chat/Retrieval Debug Script")
    print("=" * 70)
    
    # Check MongoDB
    if not check_mongo_connection():
        print("\n⚠ Cannot proceed without MongoDB connection")
        return
    
    # Check Unit 5 content
    check_unit_5_content()
    
    # Test retrieval
    await test_retrieval("explain poem in unit 5")
    await test_retrieval("The Grumble Family poem")
    await test_retrieval("poetry themes and literary devices")
    
    print("\n" + "=" * 70)
    print("Debug Complete")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
