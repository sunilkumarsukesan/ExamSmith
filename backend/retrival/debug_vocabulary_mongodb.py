#!/usr/bin/env python3
"""
Debug script to verify vocabulary data in MongoDB.
Run this to ensure your vocabulary exercise is properly stored and accessible.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

import logging
from mongo.client import mongo_client

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_vocabulary_in_mongodb():
    """Check if vocabulary exercise data exists in MongoDB."""
    
    print("\n" + "="*70)
    print("VOCABULARY MONGODB DATA CHECK")
    print("="*70)
    
    collection = mongo_client.textbook_collection
    
    if collection is None:
        logger.error("❌ Cannot connect to MongoDB collection!")
        logger.error("   Make sure MONGODB_URI is set in environment variables")
        return False
    
    print("\n✅ MongoDB connection successful")
    
    # Check for vocabulary data with your exact metadata structure
    vocab_filter = {
        "metadata.topic": "Prose",
        "metadata.sub_topic": "Vocabulary",
        "metadata.unit": 1,
    }
    
    print(f"\n🔍 Searching for vocabulary data...")
    print(f"   Filter: {vocab_filter}")
    
    count = collection.count_documents(vocab_filter)
    print(f"\n📊 Found {count} documents")
    
    if count > 0:
        print(f"\n✅ Great! Your vocabulary data is in MongoDB!")
        
        # Get all vocabulary documents sorted by position
        docs = list(collection.find(vocab_filter).sort("metadata.position", 1).limit(20))
        
        print(f"\n📋 Vocabulary Documents (in order):")
        print("-" * 70)
        
        for doc in docs:
            content = doc.get("content", "").strip()
            position = doc.get("metadata", {}).get("position")
            sub_topic = doc.get("metadata", {}).get("sub_topic", "N/A")
            
            # Truncate long content for display
            content_display = content[:60] + "..." if len(content) > 60 else content
            
            print(f"\n  Position {position}: {content_display}")
            print(f"    └─ Full: {content}")
        
        print("\n" + "-" * 70)
        
        # Verify we have all 5 vocabulary words
        required_words = ['coward', 'gradual', 'praise', 'courageous', 'starvation']
        found_words = {}
        
        for doc in docs:
            content = doc.get("content", "").lower()
            for word in required_words:
                if word in content and word not in found_words:
                    found_words[word] = doc.get("metadata", {}).get("position")
        
        print(f"\n🎯 Required Vocabulary Words Status:")
        all_found = True
        for word in required_words:
            if word in found_words:
                print(f"   ✅ {word.upper()} (at position {found_words[word]})")
            else:
                print(f"   ❌ {word.upper()} - NOT FOUND")
                all_found = False
        
        if all_found:
            print(f"\n✨ All 5 vocabulary words found in MongoDB!")
        else:
            print(f"\n⚠️  Some vocabulary words are missing from MongoDB")
        
        return all_found
    
    else:
        logger.warning("\n❌ NO VOCABULARY DATA FOUND in MongoDB!")
        logger.warning("   Your vocabulary exercise data has not been ingested yet.")
        logger.warning("   You need to run the ingestion pipeline to add this data.")
        
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check that the vocabulary data is in your source files")
        print("   2. Run the ingestion pipeline: python backend/injection/main.py")
        print("   3. Verify MongoDB connection and database names")
        
        # Check if there's ANY data at all
        print("\n📊 Checking overall collection stats...")
        total_docs = collection.count_documents({})
        prose_docs = collection.count_documents({"metadata.topic": "Prose"})
        
        print(f"   Total documents in collection: {total_docs}")
        print(f"   Documents with topic='Prose': {prose_docs}")
        
        if prose_docs > 0:
            print(f"\n   📝 There IS data for 'Prose' topic, but no 'Vocabulary' sub_topic")
            print(f"   Check if sub_topic field exists in your data")
        
        return False


def check_metadata_fields():
    """Check what fields exist in the collection."""
    
    print("\n" + "="*70)
    print("MONGODB METADATA STRUCTURE CHECK")
    print("="*70)
    
    collection = mongo_client.textbook_collection
    
    if collection is None:
        return
    
    # Get a sample document
    sample = collection.find_one({})
    
    if sample:
        print("\n✅ Found sample document in collection")
        
        metadata = sample.get("metadata", {})
        print(f"\n📋 Available metadata fields:")
        for key in sorted(metadata.keys()):
            value = metadata[key]
            # Truncate long values
            value_str = str(value)[:50] if len(str(value)) > 50 else str(value)
            print(f"   • {key}: {value_str}")
        
        # Check if required fields exist
        required_fields = ["topic", "sub_topic", "unit", "position"]
        print(f"\n🔍 Required fields for vocabulary search:")
        for field in required_fields:
            if field in metadata:
                print(f"   ✅ {field}: exists")
            else:
                print(f"   ❌ {field}: MISSING")
    else:
        print("\n❌ No documents found in collection!")


if __name__ == "__main__":
    print("\n🔍 EXAMSMITH VOCABULARY DATA VERIFICATION")
    print("="*70)
    
    # Check metadata structure first
    check_metadata_fields()
    
    # Then check for vocabulary data
    success = check_vocabulary_in_mongodb()
    
    print("\n" + "="*70)
    if success:
        print("✅ VOCABULARY RETRIEVAL READY - Your data is accessible!")
        print("="*70)
        sys.exit(0)
    else:
        print("⚠️  ACTION REQUIRED - Vocabulary data needs to be ingested")
        print("="*70)
        sys.exit(1)
