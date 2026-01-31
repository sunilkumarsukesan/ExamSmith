"""Quick script to reset a user's password."""
from pymongo import MongoClient
from config import settings
from auth.password import hash_password

client = MongoClient(settings.mongodb_uri)
db = client[settings.mongodb_users_db]
users = db['users']

# Find the user
email = 'instructor@test.com'
user = users.find_one({'email': email})
if user:
    # Reset password
    new_password = 'Instructor123!'
    new_hash = hash_password(new_password)
    users.update_one({'email': email}, {'$set': {'password_hash': new_hash}})
    print('Password reset successfully!')
    print(f'Email: {email}')
    print(f'New Password: {new_password}')
else:
    print(f'User {email} not found in database')

client.close()
