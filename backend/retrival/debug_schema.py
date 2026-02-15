from mongo.client import mongo_client
import json

collection = mongo_client.questionpapers_collection
if collection is not None:
    count = collection.count_documents({})
    print(f'Total documents: {count}')
    
    if count > 0:
        doc = collection.find_one({})
        print(f'Document keys: {list(doc.keys())}')
        print(f'\nFull document (first 50 lines):')
        doc_str = json.dumps(doc, indent=2, default=str)
        lines = doc_str.split('\n')[:50]
        for line in lines:
            print(line)
    else:
        print('No documents in collection')
else:
    print('Collection is None')
