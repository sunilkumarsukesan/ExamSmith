"""Debug script to check pipeline data."""
from pymongo import MongoClient
from config import settings
import json

client = MongoClient(settings.mongodb_uri)

# Check pipeline collection
pipeline_db = client[settings.mongodb_pipeline_db]
pipeline_coll = pipeline_db[settings.mongodb_pipeline_collection]

# Get a paper from pipeline
paper = pipeline_coll.find_one()
if paper:
    print('=== PIPELINE PAPER ===')
    print(f'paper_id: {paper.get("paper_id")}')
    print(f'total_marks: {paper.get("total_marks")}')
    print(f'total_questions: {paper.get("total_questions")}')
    print(f'questions count: {len(paper.get("questions", []))}')
    if paper.get('questions'):
        print('\n=== FIRST 3 QUESTIONS ===')
        for q in paper.get('questions')[:3]:
            print(json.dumps(q, indent=2, default=str))
else:
    print('No papers in pipeline')

# Also check original papers collection
print('\n\n=== ORIGINAL PAPER ===')
db = client[settings.mongodb_users_db]
papers_coll = db['question_papers']
orig = papers_coll.find_one()
if orig:
    print(f'paper_id: {orig.get("paper_id")}')
    print(f'total_marks: {orig.get("total_marks")}')
    print(f'questions count: {len(orig.get("questions", []))}')
    if orig.get('questions'):
        print('\n=== FIRST 3 ORIGINAL QUESTIONS ===')
        for q in orig.get('questions')[:3]:
            print(json.dumps(q, indent=2, default=str))
else:
    print('No papers in original collection')

client.close()
