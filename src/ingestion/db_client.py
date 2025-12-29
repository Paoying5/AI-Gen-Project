import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import sys
import os
import json
import pandas as pd

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class MongoDBClient:
    def __init__(self):
        self.use_fallback = False
        try:
            self.client = pymongo.MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
            self.client.server_info() # Trigger connection to verify
            self.db = self.client[Config.DB_NAME]
            print(f"Connected to MongoDB: {Config.DB_NAME}")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            print(f"WARNING: Could not connect to MongoDB ({e}). Switching to Local JSON Fallback.")
            self.use_fallback = True
            os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data"), exist_ok=True)

    def insert_many(self, collection_name, data):
        if not self.use_fallback:
            collection = self.db[collection_name]
            if data:
                result = collection.insert_many(data)
                print(f"Inserted {len(result.inserted_ids)} records into {collection_name}")
                return result
        else:
            # Fallback: Write to Data Lake
            os.makedirs(Config.DATA_LAKE_DIR, exist_ok=True)
            file_path = os.path.join(Config.DATA_LAKE_DIR, f"{collection_name}.json")
            with open(file_path, 'w') as f:
                json.dump(data, f)
            print(f"Fallback: Saved {len(data)} records to Data Lake: {file_path}")

    def fetch_all(self, collection_name):
        if not self.use_fallback:
            collection = self.db[collection_name]
            data = list(collection.find({}, {'_id': 0}))
            return data
        else:
            # Fallback
            file_path = os.path.join(Config.DATA_LAKE_DIR, f"{collection_name}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    data = json.load(f)
                print(f"Fallback: Loaded {len(data)} records from Data Lake: {file_path}")
                return data
            else:
                return []

    def clear_collection(self, collection_name):
        if not self.use_fallback:
            self.db[collection_name].drop()
            print(f"Cleared collection: {collection_name}")
        else:
            file_path = os.path.join(Config.DATA_LAKE_DIR, f"{collection_name}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
