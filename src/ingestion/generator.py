import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class DataGenerator:
    def __init__(self, n_samples=5000, start_date='2023-01-01', freq='H'):
        self.n_samples = n_samples
        self.start_date = start_date
        self.freq = freq

    def generate_series(self, base, trend, seasonality, noise_level):
        """
        Generates a synthetic time series with Trend + Seasonality + Noise
        Y_t = Base + Trend*t + Seasonality + Noise
        """
        time = np.arange(self.n_samples)
        trend_component = list(map(lambda t: t * trend, time))
        
        # Seasonality: Daily (24h) and Weekly (168h) cycles if hourly
        seasonal_component = list(map(lambda t: 10 * np.sin(2 * np.pi * t / 24) + \
                                                5 * np.cos(2 * np.pi * t / 168), time))
        
        noise = np.random.normal(0, noise_level, self.n_samples)
        
        series = base + np.array(trend_component) + np.array(seasonal_component) + noise
        return np.maximum(series, 0) # Ensure no negative values for pollution

    def create_dataset(self):
        print("Generating synthetic Air Quality data...")
        
        # PM2.5: Moderate trend, strong daily seasonality
        pm25 = self.generate_series(base=30, trend=0.005, seasonality=True, noise_level=5)
        
        # PM10: Higher base, similar trend
        pm10 = self.generate_series(base=50, trend=0.005, seasonality=True, noise_level=8)
        
        # NO2: Traffic related, sharp peaks
        no2 = self.generate_series(base=20, trend=0.002, seasonality=True, noise_level=4)
        
        # O3: Inverse correlation with NO2 often, but here just independent cyclicity
        o3 = self.generate_series(base=40, trend=-0.001, seasonality=True, noise_level=6)

        
        # Add realistic noise/anomalies
        # 1. Random NaNs (Sensor failure)
        nan_indices = random.sample(range(self.n_samples), int(self.n_samples * 0.05)) # 5% missing
        for i in nan_indices:
            pm25[i] = np.nan
        
        # 2. Random Spikes (Sensor malfunction or localized smoke)
        spike_indices = random.sample(range(self.n_samples), int(self.n_samples * 0.01)) # 1% outliers
        for i in spike_indices:
            pm25[i] = pm25[i] * random.uniform(3, 5) # 3x-5x spikes

        date_range = pd.date_range(start=self.start_date, periods=self.n_samples, freq=self.freq)
        
        data = []
        for i, date in enumerate(date_range):
            record = {
                "timestamp": date.isoformat(),
                "pm25": float(pm25[i]) if not np.isnan(pm25[i]) else None, # JSON standard for NaN is null
                "pm10": float(pm10[i]),
                "no2": float(no2[i]),
                "o3": float(o3[i]),
                "sensor_id": "VN_HANOI_001",
                "location": "Hanoi, Vietnam"
            }
            data.append(record)
            
        print(f"Generated {len(data)} samples (with 5% simulated missing values).")
        return data

if __name__ == "__main__":
    gen = DataGenerator()
    data = gen.create_dataset()
    print(data[:2])
