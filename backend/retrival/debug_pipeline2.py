"""Debug pipeline papers."""
from mongo.client import mongo_client
from config import settings
import json

client = mongo_client.client
pipeline_db = client[settings.mongodb_pipeline_db]
pipeline_coll = pipeline_db[settings.mongodb_pipeline_collection]

papers = list(pipeline_coll.find())
print(f"Published papers: {len(papers)}")

for idx, p in enumerate(papers):
    print(f"\n--- Paper {idx + 1} ---")
    print(f"Keys: {list(p.keys())}")
    print(f"paper_id: {p.get('paper_id')}")
    print(f"title: {p.get('title')}")
    print(f"status: {p.get('status')}")
    print(f"total_questions: {p.get('total_questions')}")
    print(f"total_marks: {p.get('total_marks')}")
    
    questions = p.get('questions', [])
    print(f"Questions count: {len(questions)}")
    if questions:
        print(f"First question keys: {list(questions[0].keys()) if isinstance(questions[0], dict) else 'N/A'}")
