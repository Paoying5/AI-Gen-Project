from .generator import DataGenerator
from db_client import MongoDBClient
import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config
from src.processing.cleaner import DataCleaner

def run_etl():
    print(">>> Starting Enterprise ETL Pipeline...")
    
    # 1. Ingestion: Simulate Sensor Stream -> Data Lake (Raw)
    print("\n[Step 1] Ingesting Data to Data Lake...")
    gen = DataGenerator(n_samples=Config.N_SAMPLES, start_date=Config.START_DATE)
    data = gen.create_dataset()
    
    mongo = MongoDBClient()
    mongo.clear_collection(Config.COLLECTION_RAW)
    mongo.insert_many(Config.COLLECTION_RAW, data)
    
    # 2. Processing: Data Lake -> Data Warehouse (Cleaned)
    print("\n[Step 2] Processing & Cleaning...")
    df_raw = pd.DataFrame(data)
    
    cleaner = DataCleaner()
    
    # Impute Missing Values
    df_clean = cleaner.handle_missing_values(df_raw)
    
    # Handle Outliers (Optional logic, let's keep spikes for 'Red Alert' detection but maybe cap extreme errors)
    # df_clean = cleaner.remove_outliers(df_clean, ['pm25'], factor=5.0) 
    
    # Save to Parquet (Warehouse)
    cleaner.save_processed(df_clean, filename=f"{Config.COLLECTION_PROCESSED}.parquet")
    
    print("\n>>> ETL Complete. Data ready in Warehouse.")

if __name__ == "__main__":
    run_etl()
