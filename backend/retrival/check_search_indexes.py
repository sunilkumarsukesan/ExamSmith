"""
Check MongoDB Atlas Search Indexes for ExamSmith.
These indexes are REQUIRED for the hybrid search to work.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from mongo.client import mongo_client
from config import settings

def check_indexes():
    """Check if required indexes exist on MongoDB Atlas."""
    print("\n" + "=" * 70)
    print("MongoDB Atlas Search Index Check")
    print("=" * 70)
    
    if not mongo_client.client:
        print("✗ MongoDB client not connected")
        return
    
    print(f"\nTextbook Database: {settings.mongodb_db_textbook}")
    print(f"Textbook Collection: {settings.mongodb_collection_textbook}")
    
    textbook_coll = mongo_client.textbook_collection
    if textbook_coll is None:
        print("✗ Textbook collection unavailable")
        return
    
    # Try to list search indexes (requires Atlas)
    print("\n" + "-" * 70)
    print("Checking Atlas Search Indexes...")
    print("-" * 70)
    
    try:
        # In MongoDB Atlas, search indexes can be listed with list_search_indexes
        indexes = list(textbook_coll.list_search_indexes())
        
        if indexes:
            print(f"\n✓ Found {len(indexes)} search indexes:")
            for idx in indexes:
                print(f"\n  Index Name: {idx.get('name')}")
                print(f"  Status: {idx.get('status')}")
                print(f"  Type: {idx.get('type', 'search')}")
        else:
            print("\n⚠ NO SEARCH INDEXES FOUND!")
            print_index_instructions()
    
    except Exception as e:
        if "not authorized" in str(e).lower() or "not supported" in str(e).lower():
            print(f"\n⚠ Cannot list search indexes programmatically: {e}")
            print("  This might be a permissions issue or standalone MongoDB (not Atlas)")
        else:
            print(f"\n⚠ Error checking indexes: {e}")
        
        print_index_instructions()
    
    # Check regular indexes
    print("\n" + "-" * 70)
    print("Checking Regular Indexes...")
    print("-" * 70)
    
    try:
        regular_indexes = list(textbook_coll.list_indexes())
        print(f"\n✓ Found {len(regular_indexes)} regular indexes:")
        for idx in regular_indexes:
            print(f"  - {idx.get('name')}: {idx.get('key')}")
    except Exception as e:
        print(f"\n✗ Error listing regular indexes: {e}")


def print_index_instructions():
    """Print instructions for creating search indexes on MongoDB Atlas."""
    print("\n" + "=" * 70)
    print("REQUIRED: Create Search Indexes on MongoDB Atlas")
    print("=" * 70)
    
    print("""
To enable the chat feature with textbook context, you need to create
TWO search indexes on your MongoDB Atlas cluster:

1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Select your cluster: examSmith
3. Go to "Atlas Search" tab
4. Click "Create Search Index"

=== INDEX 1: BM25 (Full-Text Search) ===

Index Name: BM25
Database: 10_books
Collection: english

JSON Definition:
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "content": {
        "type": "string",
        "analyzer": "lucene.standard"
      },
      "metadata": {
        "type": "document",
        "fields": {
          "lang": { "type": "string" },
          "unit": { "type": "number" },
          "lesson_name": { "type": "string" }
        }
      }
    }
  }
}

=== INDEX 2: Vector (Semantic Search) ===

Index Name: vector
Database: 10_books  
Collection: english

JSON Definition:
{
  "type": "vectorSearch",
  "fields": [
    {
      "path": "embedding",
      "numDimensions": 1024,
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "metadata.lang",
      "type": "filter"
    },
    {
      "path": "metadata.unit", 
      "type": "filter"
    }
  ]
}

=== IMPORTANT NOTES ===

1. The BM25 index enables keyword/full-text search
2. The vector index enables semantic similarity search
3. Both indexes are required for hybrid search to work
4. Index creation takes a few minutes - wait for status "Active"
5. Make sure the embedding dimension matches (1024 for Mistral)

After creating the indexes, restart the backend and test again.
""")


def test_simple_query():
    """Test a simple find query to verify data exists."""
    print("\n" + "=" * 70)
    print("Testing Simple MongoDB Query (no search index required)")
    print("=" * 70)
    
    textbook_coll = mongo_client.textbook_collection
    if textbook_coll is None:
        print("✗ Collection unavailable")
        return
    
    # Simple text regex search (no index required)
    try:
        results = list(textbook_coll.find(
            {"content": {"$regex": "poem", "$options": "i"}}
        ).limit(3))
        
        print(f"\n✓ Found {len(results)} documents containing 'poem'")
        
        for i, doc in enumerate(results, 1):
            content = doc.get('content', '')[:200]
            print(f"\n[{i}] {content}...")
    
    except Exception as e:
        print(f"\n✗ Query failed: {e}")


if __name__ == "__main__":
    check_indexes()
    test_simple_query()
    
    print("\n" + "=" * 70)
    print("Next Steps:")
    print("1. Create the BM25 and vector indexes on MongoDB Atlas")
    print("2. Wait for indexes to be 'Active' (few minutes)")
    print("3. Restart the backend: npm run dev")
    print("4. Test chat again with: 'explain poem in unit 5'")
    print("=" * 70 + "\n")
