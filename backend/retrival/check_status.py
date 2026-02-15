from pymongo import MongoClient
from config import settings

c = MongoClient(settings.mongodb_uri)
db = c[settings.mongodb_users_db]
p = db['question_papers'].find_one()
if p:
    print(f'Status: {p.get("status")}')
    # Reset to APPROVED
    db['question_papers'].update_one({'paper_id': p['paper_id']}, {'$set': {'status': 'APPROVED'}})
    print('Reset to APPROVED')
c.close()
