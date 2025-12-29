import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller
from sklearn.preprocessing import MinMaxScaler
import joblib
import sys
import os

# Config path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DatePipeline:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))

    def check_stationarity(self, series, name="Series"):
        """
        Performs Augmented Dickey-Fuller test.
        Null Hypothesis (H0): Non-stationary (Unit Root Present)
        """
        result = adfuller(series.dropna())
        print(f"\nADF Test for {name}:")
        print(f"ADF Statistic: {result[0]}")
        print(f"p-value: {result[1]}")
        
        if result[1] < 0.05:
            print("=> Stationary (Reject H0)")
            return True
        else:
            print("=> Non-Stationary (Fail to Reject H0)")
            return False

    def engineer_features(self, df):
        """
        Adds rolling stats, lags, and date parts.
        """
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df.set_index('datetime', inplace=True)
        df.sort_index(inplace=True)

        # 1. Date parts
        df['hour'] = df.index.hour
        df['day_of_week'] = df.index.dayofweek
        df['month'] = df.index.month

        # 2. Lag Features (Previous hours)
        for col in ['pm25', 'pm10', 'no2', 'o3']:
            df[f'{col}_lag1'] = df[col].shift(1)
            df[f'{col}_lag24'] = df[col].shift(24) # Daily Seasonality

        # 3. Rolling Statistics
        df['pm25_roll_mean_24h'] = df['pm25'].rolling(window=24).mean()
        df['pm25_roll_std_24h'] = df['pm25'].rolling(window=24).std()

        df.dropna(inplace=True)
        return df

    def scale_data(self, df, fit=True):
        """
        MinMax Scaling for LSTM
        """
        feature_cols = [c for c in df.columns if c not in ['timestamp', 'sensor_id', 'location']]
        
        if fit:
            scaled_data = self.scaler.fit_transform(df[feature_cols])
            # Save scaler
            os.makedirs(Config.MODEL_DIR, exist_ok=True)
            joblib.dump(self.scaler, os.path.join(Config.MODEL_DIR, "scaler.pkl"))
        else:
            scaled_data = self.scaler.transform(df[feature_cols])
            
        df_scaled = pd.DataFrame(scaled_data, columns=feature_cols, index=df.index)
        return df_scaled

    def create_sequences(self, data, seq_len):
        """
        Creates sequences for LSTM: (Samples, TimeSteps, Features)
        """
        xs, ys = [], []
        data_values = data.values
        for i in range(len(data_values) - seq_len):
            x = data_values[i:(i + seq_len)]
            y = data_values[i + seq_len][0] # Predicting PM2.5 (1st column usually)
            xs.append(x)
            ys.append(y)
        return np.array(xs), np.array(ys)
