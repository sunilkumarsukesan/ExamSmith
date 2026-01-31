"""Find questions with object-type options."""
from pymongo import MongoClient
from config import settings
import json

client = MongoClient(settings.mongodb_uri)

pipeline_db = client[settings.mongodb_pipeline_db]
pipeline_coll = pipeline_db[settings.mongodb_pipeline_collection]

paper = pipeline_coll.find_one()
if paper:
    questions = paper.get("questions", [])
    
    print("=== CHECKING OPTIONS ===")
    for idx, q in enumerate(questions):
        options = q.get("options")
        if options and isinstance(options, list):
            # Check if any option is an object
            has_object = any(isinstance(opt, dict) for opt in options)
            if has_object:
                print(f"\nQuestion {idx+1} (#{q.get('question_number')}):")
                print(f"Type: {q.get('question_type')}")
                print(f"Text: {q.get('question_text')[:80]}...")
                print(f"Options:")
                for i, opt in enumerate(options[:3]):
                    print(f"  {i}: {type(opt).__name__} = {str(opt)[:100]}")

client.close()
