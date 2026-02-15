"""
Find substantial textbook content.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mongo.client import mongo_client

coll = mongo_client.textbook_collection

# Find documents with substantial content using regex length approximation
# MongoDB $expr with $strLenCP for string length
pipeline = [
    {"$addFields": {"content_length": {"$strLenCP": "$content"}}},
    {"$match": {"content_length": {"$gt": 300}}},
    {"$sort": {"content_length": -1}},
    {"$limit": 20}
]

docs = list(coll.aggregate(pipeline))
print(f"Found {len(docs)} documents with content > 300 chars\n")

for i, doc in enumerate(docs, 1):
    content = doc.get("content", "")
    unit = doc.get("metadata", {}).get("unit")
    topic = doc.get("metadata", {}).get("topic")
    sub_topic = doc.get("metadata", {}).get("sub_topic")
    length = doc.get("content_length", len(content))
    
    print(f"\n{'='*70}")
    print(f"[{i}] Unit: {unit} | Topic: {topic} | Sub-topic: {sub_topic}")
    print(f"Content Length: {length} chars")
    print("-" * 70)
    print(content[:600])
    if len(content) > 600:
        print("...")
