"""Debug: List all collections and their data."""
from mongo.client import mongo_client
from config import settings

client = mongo_client.client

# Check examsmith database
print("=== examsmith database ===")
db = client[settings.mongodb_users_db]
print(f"Database: {settings.mongodb_users_db}")
print(f"Collections: {db.list_collection_names()}")

for coll_name in db.list_collection_names():
    count = db[coll_name].count_documents({})
    print(f"  - {coll_name}: {count} documents")

# Check configured collection names
print(f"\nConfigured attempts collection: {settings.mongodb_attempts_collection}")
print(f"Configured evaluations collection: {settings.mongodb_evaluations_collection}")

# Check if attempts exist in any collection with "attempt" in name
for coll_name in db.list_collection_names():
    if "attempt" in coll_name.lower():
        docs = list(db[coll_name].find().limit(2))
        print(f"\n{coll_name} sample:")
        for d in docs:
            print(f"  - {d.get('attempt_id')}: status={d.get('status')}")
