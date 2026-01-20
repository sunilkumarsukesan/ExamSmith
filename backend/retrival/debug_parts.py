from mongo.client import mongo_client

collection = mongo_client.questionpapers_collection
if collection is not None:
    # Get unique part values
    parts = collection.distinct('metadata.part')
    print('Unique parts in database:')
    for part in sorted(parts):
        count = collection.count_documents({'metadata.part': part})
        print(f'  "{part}": {count} questions')
else:
    print('Collection is None')
