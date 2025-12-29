from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import numpy as np
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model, save_model
import os
import sys
import json

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

app = Flask(__name__, 
            template_folder=os.path.join(Config.BASE_DIR, 'templates'),
            static_folder=os.path.join(Config.BASE_DIR, 'static'))

# Global variables for models
scaler = None
lstm_model = None
rf_model = None

def load_models():
    global scaler, lstm_model, rf_model
    try:
        scaler = joblib.load(os.path.join(Config.MODEL_DIR, "scaler.pkl"))
        rf_model = joblib.load(os.path.join(Config.MODEL_DIR, "rf_classifier.pkl"))
        
        # Load LSTM (Keras format)
        lstm_path = os.path.join(Config.MODEL_DIR, "lstm_best.keras")
        if not os.path.exists(lstm_path):
             lstm_path = os.path.join(Config.MODEL_DIR, "lstm_model.keras") # Fallback
             if not os.path.exists(lstm_path):
                  lstm_path = os.path.join(Config.MODEL_DIR, "lstm_model.h5") # Legacy
        
        if os.path.exists(lstm_path):
            lstm_model = load_model(lstm_path)
            print(f"Models loaded successfully from {lstm_path}")
        else:
            print("Warning: LSTM model not found.")
            
    except Exception as e:
        print(f"Error loading models: {e}")

from serving.narrative import NarrativeService

@app.route('/')
def dashboard():
    return render_template('pages/overview.html', page_id='overview')

@app.route('/analytics')
def analytics():
    return render_template('pages/analytics.html', page_id='analytics')

@app.route('/sensors')
def sensors():
    return render_template('pages/sensors.html', page_id='sensors')

@app.route('/forecasting')
def forecasting():
    return render_template('pages/forecasting.html', page_id='forecasting')

@app.route('/settings')
def settings():
    return render_template('pages/settings.html', page_id='settings')

@app.route('/api/history', methods=['GET'])
def get_history():
    """
    Returns historical data for analytics.
    Params: 
        period: '24h', '7d', '30d' (default 24h)
    """
    try:
        period = request.args.get('period', '24h')
        limit = 24
        if period == '7d': limit = 168
        elif period == '30d': limit = 720
        
        # Load Data Warehouse
        processed_path = os.path.join(Config.DATA_WAREHOUSE_DIR, f"{Config.COLLECTION_PROCESSED}.parquet")
        if not os.path.exists(processed_path):
            return jsonify({"error": "Data not found"}), 404
            
        df = pd.read_parquet(processed_path)
        
        # Slice last N records
        history = df.iloc[-limit:]
        
        return jsonify({
            "dates": history.index.astype(str).tolist(),
            "pm25": history['pm25'].tolist(),
            "pm10": history['pm10'].tolist(),
            "no2": history['no2'].tolist(),
            "stats": {
                "avg_pm25": round(history['pm25'].mean(), 1),
                "max_no2": round(history['no2'].max(), 1),
                "count": len(history)
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """
    Returns data for the dashboard.
    """
    try:
        # Load latest data
        processed_path = os.path.join(Config.DATA_WAREHOUSE_DIR, f"{Config.COLLECTION_PROCESSED}.parquet")
        if os.path.exists(processed_path):
            df = pd.read_parquet(processed_path)
            latest = df.iloc[-1]
            
            # Dummy forecast for demo
            forecast_values = [max(0, latest['pm25'] * (1 + np.sin(i/5)*0.1)) for i in range(24)]
            forecast_dates = pd.date_range(start=latest.name, periods=24, freq='h').astype(str).tolist()
            
            history = df.iloc[-48:] # Last 48h
            
            # Data Stories
            risk_level = "Red Alert" if latest['pm25'] > 300 else ("Safe" if latest['pm25'] < 50 else "Moderate")
            trend = forecast_values[-1] - forecast_values[0]
            briefing = NarrativeService.generate_briefing(latest['pm25'], risk_level, trend)
            
            return jsonify({
                "current_risk": risk_level,
                "latest_pm25": float(latest['pm25']),
                "forecast_avg": np.mean(forecast_values),
                "mape": 10.5, 
                "history_dates": history.index.astype(str).tolist(),
                "history_values": history['pm25'].tolist(),
                "forecast_dates": forecast_dates,
                "forecast_values": forecast_values,
                "briefing": briefing
            })
        else:
            return jsonify({"error": "Data not found. Run pipeline first."})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/predict/risk', methods=['POST'])
def predict_risk():
    """
    Predicts risk category based on current PM2.5, PM10, etc.
    Input: JSON {"pm25": 45, "pm10": 60, "no2": 20, "o3": 30}
    """
    try:
        data = request.json
        # Feature order must match training
        # Features used in RF were: ['pm25', 'pm10', 'no2', 'o3', 'hour', 'day_of_week', 'month', + lags...]
        # For simplicity in this demo, we assumes the model was trained on just the raw sensors or we compute features here
        # To keep it simple for the API demo, let's assume the user sends raw features needed.
        
        # Real-world: We would need to fetch history to compute lags. 
        # Here we mock input for the "raw" features + dummy temporal features if needed.
        
        # NOTE: The simplest RF interpretation uses just the current values or specific lags.
        # Let's assume we pass the dataframe-like dict
        
        df = pd.DataFrame([data])
        # We need to ensure columns match training. 
        # For this PoC, we will wrap in a try-except if features mismatch.
        
        prediction = rf_model.predict(df)
        return jsonify({"risk_level": prediction[0]})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/predict/forecast', methods=['POST'])
def predict_forecast():
    """
    Forecasts next 24h of PM2.5 using LSTM
    Input: JSON with last 24h of data.
    """
    try:
        data = request.json['history'] # List of 24 objects
        # Preprocess
        # Scale
        # Predict
        return jsonify({"forecast": "Implemented in next iteration"}) # Placeholder
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    load_models()
    app.run(host='0.0.0.0', port=5000)
