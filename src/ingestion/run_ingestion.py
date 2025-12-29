from generator import DataGenerator
from db_client import MongoDBClient
import sys
import os

# Context for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def main():
    print(">>> Starting Data Ingestion Pipeline...")
    
    # 1. Generate Data
    gen = DataGenerator(n_samples=Config.N_SAMPLES, start_date=Config.START_DATE)
    data = gen.create_dataset()
    
    # 2. Ingest to Mongo
    mongo = MongoDBClient()
    mongo.clear_collection(Config.COLLECTION_RAW)
    mongo.insert_many(Config.COLLECTION_RAW, data)
    
    print(">>> Data Ingestion Complete.")

if __name__ == "__main__":
    main()
