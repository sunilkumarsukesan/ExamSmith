"""Check attempts and evaluations in the database."""
from mongo.client import mongo_client
from config import settings

client = mongo_client.client
db = client[settings.mongodb_users_db]  # examsmith database

# Check attempts with their statuses
attempts = list(db.attempts.find())
print('Total attempts:', len(attempts))
for a in attempts:
    print(f"  - {a.get('attempt_id')}: status={a.get('status')}, student_id={a.get('student_id')}")

# Check evaluations
evals = list(db.evaluations.find())
print('\nTotal evaluations:', len(evals))
for e in evals:
    print(f"  - attempt_id={e.get('attempt_id')}, score={e.get('final_score')}/{e.get('total_marks')}")
