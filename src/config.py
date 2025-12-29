import os

class Config:
    # MongoDB
    MONGO_URI = "mongodb://localhost:27017/"
    DB_NAME = "air_quality_db"
    COLLECTION_RAW = "raw_readings"
    COLLECTION_PROCESSED = "processed_features"

    # Data Gen
    N_SAMPLES = 5000
    START_DATE = "2023-01-01"
    FREQ = "h" # Hourly

    # Paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_LAKE_DIR = os.path.join(BASE_DIR, "data", "raw")
    DATA_WAREHOUSE_DIR = os.path.join(BASE_DIR, "data", "processed")
    MODEL_DIR = os.path.join(BASE_DIR, "models")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    PLOT_DIR = os.path.join(STATIC_DIR, "plots")
    
    # Model Params
    LSTM_SEQ_LEN = 24  # Use past 24 hours to predict next
    LSTM_EPOCHS = 10
    LSTM_BATCH_SIZE = 32
    
    # Risk Levels
    RISK_THRESHOLDS = {
        "Safe": 50,
        "Normal": 100,
        "Moderate": 150,
        "Light Pollution": 200,
        "Heavy Pollution": 300,
        "Red Alert": 9999
    }
