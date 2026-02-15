"""Check what the API is returning for the exam."""
from pymongo import MongoClient
from config import settings
import json

client = MongoClient(settings.mongodb_uri)

# Check pipeline collection
pipeline_db = client[settings.mongodb_pipeline_db]
pipeline_coll = pipeline_db[settings.mongodb_pipeline_collection]

# Get the paper
paper = pipeline_coll.find_one()
if paper:
    print('=== PIPELINE PAPER ===')
    print(f'paper_id: {paper.get("paper_id")}')
    print(f'total_marks: {paper.get("total_marks")}')
    print(f'total_questions: {paper.get("total_questions")}')
    print(f'questions count: {len(paper.get("questions", []))}')
    
    # Check questions
    questions = paper.get("questions", [])
    print(f'\n=== SAMPLE QUESTIONS ===')
    print(f'Question 1: {json.dumps(questions[0], indent=2, default=str)[:500]}')
    print(f'\nQuestion 15: {json.dumps(questions[14], indent=2, default=str)[:500]}')
    print(f'\nQuestion 30: {json.dumps(questions[29], indent=2, default=str)[:500]}')
    
    # Count empty question_text
    empty_count = sum(1 for q in questions if not q.get('question_text', '').strip())
    print(f'\n=== EMPTY QUESTIONS: {empty_count} out of {len(questions)} ===')
else:
    print('No papers in pipeline')

client.close()
