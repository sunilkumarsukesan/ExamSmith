"""Reset pipeline for republishing."""
from pymongo import MongoClient
from config import settings

client = MongoClient(settings.mongodb_uri)

# Delete from pipeline
pipeline_db = client[settings.mongodb_pipeline_db]
pipeline_coll = pipeline_db[settings.mongodb_pipeline_collection]
result = pipeline_coll.delete_many({})
print(f'Deleted {result.deleted_count} papers from pipeline')

# Reset paper status to APPROVED so it can be republished
db = client[settings.mongodb_users_db]
papers_coll = db['question_papers']
result = papers_coll.update_many(
    {'status': 'PUBLISHED'},
    {'$set': {'status': 'APPROVED', 'published_by': None, 'published_at': None}}
)
print(f'Reset {result.modified_count} papers to APPROVED status')

# Also delete any student attempts
attempts_coll = db['student_attempts']
result = attempts_coll.delete_many({})
print(f'Deleted {result.deleted_count} student attempts')

client.close()
print('\nDone! Now republish the paper from the Teacher UI.')
