"""Reset admin password."""
from pymongo import MongoClient
from config import settings
from auth.password import hash_password

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_users_db]
users = db['users']

email = 'admin@examsmith.com'
user = users.find_one({'email': email})
if user:
    new_password = 'admin123'
    new_hash = hash_password(new_password)
    users.update_one(
        {'email': email},
        {'$set': {'password_hash': new_hash, 'status': 'ACTIVE'}}
    )
    print(f'Admin password reset successfully!')
    print(f'Email: {email}')
    print(f'Password: {new_password}')
else:
    print(f'User {email} not found')

client.close()
