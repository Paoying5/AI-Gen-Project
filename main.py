import pandas as pd
import numpy as np
import sys
sys.path.append("src/ingestion")  # thêm thư mục chứa generator.py vào path
from generator import DataGenerator
import os

from src.config import Config
from src.ingestion.run_etl import run_etl
from src.processing.pipeline import DatePipeline
from src.modeling.lstm import LstmModel
from src.modeling.classifier import AirQualityClassifier
from src.evaluation.metrics import ModelEvaluator

def run_enterprise_pipeline():
    print("========================================")
    print("   AIR QUALITY ENTERPRISE SYSTEM        ")
    print("========================================")

    # 1. Run ETL (Data Lake -> Warehouse)
    print("\n[Step 1] Running Enterprise ETL...")
    run_etl()

    # 2. Load Processed Data (Parquet)
    print("\n[Step 2] Loading Data from Warehouse...")
    processed_path = os.path.join(Config.DATA_WAREHOUSE_DIR, f"{Config.COLLECTION_PROCESSED}.parquet")
    df = pd.read_parquet(processed_path)
    print(f"Loaded {len(df)} records from {processed_path}")

    # 3. Model Training
    print("\n[Step 3] Training Advanced Models...")
    
    # Feature Engineering (re-apply pipeline logic if needed for new features, or assume ETL did it)
    # The current ETL does imputation. We still need lag features.
    pipeline = DatePipeline()
    df_features = pipeline.engineer_features(df)
    
    # LSTM Training
    print("--- Training LSTM ---")
    df_scaled = pipeline.scale_data(df_features, fit=True)
    X, y = pipeline.create_sequences(df_scaled[['pm25', 'pm10', 'no2', 'o3', 'pm25_roll_mean_24h']], Config.LSTM_SEQ_LEN)
    
    split_idx = int(len(X) * 0.9) # 90/10 split for final prod
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    lstm = LstmModel(input_shape=(X_train.shape[1], X_train.shape[2]))
    lstm.train(X_train, y_train, validation_data=(X_test, y_test))
    
    # RF Classification Training
    print("--- Training Risk Classifier (RF + SHAP) ---")
    classifier = AirQualityClassifier()
    df_cls = classifier.prepare_labels(df_features)
    X_cls = df_cls.drop(columns=['risk_label', 'pm25_diff'] if 'pm25_diff' in df_cls else ['risk_label'])
    X_cls = X_cls.select_dtypes(include=[np.number])
    
    classifier.train(X_cls, df_cls['risk_label'])
    
    print("\n>>> Enterprise Pipeline Complete.")
    print("    Start the Dashboard with: python src/serving/api.py")

if __name__ == "__main__":
    run_enterprise_pipeline()
