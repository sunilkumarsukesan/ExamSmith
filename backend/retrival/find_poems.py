"""Find actual poem content in textbook."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from mongo.client import mongo_client
coll = mongo_client.textbook_collection

# Search for documents tagged as Poem
print("=" * 70)
print("Searching for documents tagged as Poem")
print("=" * 70)

poem_content = list(coll.find({
    "$or": [
        {"metadata.topic": "Poem"},
        {"metadata.topic": {"$regex": "poem", "$options": "i"}}
    ]
}).limit(30))

print(f"Found {len(poem_content)} documents tagged as Poem\n")

for doc in poem_content[:15]:
    m = doc.get("metadata", {})
    content = doc.get("content", "")
    print(f"Unit {m.get('unit')}: {m.get('topic')} - {m.get('sub_topic')}")
    print(f"  Content ({len(content)} chars): {content[:300]}")
    print()

# Search for THE SECRET OF THE MACHINES (Unit 5 poem)
print("\n" + "=" * 70)
print("Searching for 'SECRET OF THE MACHINES'")
print("=" * 70)

secret_docs = list(coll.find({
    "content": {"$regex": "secret.*machine|machine.*secret", "$options": "i"}
}).limit(10))

print(f"Found {len(secret_docs)} documents\n")
for doc in secret_docs:
    content = doc.get("content", "")
    print(f"Content ({len(content)} chars): {content[:400]}")
    print()

# Search for any verse/stanza content
print("\n" + "=" * 70)
print("Searching for stanza/verse content")
print("=" * 70)

verse_docs = list(coll.find({
    "content": {"$regex": "stanza|verse|rhyme|poet", "$options": "i"},
}).limit(10))

print(f"Found {len(verse_docs)} documents with verse/stanza\n")
for doc in verse_docs[:5]:
    content = doc.get("content", "")
    m = doc.get("metadata", {})
    print(f"Unit {m.get('unit')}: {content[:400]}")
    print()
