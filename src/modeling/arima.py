import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import matplotlib.pyplot as plt
import os
import joblib
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class ArimaModel:
    def __init__(self, order=(5,1,0)):
        self.order = order
        self.model = None
        self.fit_model = None

    def analyze_acf_pacf(self, series):
        """
        Generates ACF and PACF plots for order selection
        """
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        plot_acf(series, ax=axes[0])
        plot_pacf(series, ax=axes[1])
        
        output_path = os.path.join(Config.LOG_DIR, "acf_pacf_plots.png")
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        plt.savefig(output_path)
        print(f"ACF/PACF plots saved to {output_path}")

    def train(self, train_data):
        print(f"Training ARIMA with order {self.order}...")
        self.model = ARIMA(train_data, order=self.order)
        self.fit_model = self.model.fit()
        print(self.fit_model.summary())
        
        model_path = os.path.join(Config.MODEL_DIR, "arima_model.pkl")
        joblib.dump(self.fit_model, model_path)
        print("ARIMA model saved.")

    def predict(self, steps):
        if not self.fit_model:
            raise ValueError("Model not trained yet.")
        return self.fit_model.forecast(steps=steps)
