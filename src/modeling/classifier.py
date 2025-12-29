import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import shap
import joblib
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class AirQualityClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        
    def _get_label(self, pm25):
        if pm25 <= Config.RISK_THRESHOLDS["Safe"]:
            return "Safe"
        elif pm25 <= Config.RISK_THRESHOLDS["Normal"]:
            return "Normal"
        elif pm25 <= Config.RISK_THRESHOLDS["Moderate"]:
            return "Moderate"
        elif pm25 <= Config.RISK_THRESHOLDS["Light Pollution"]:
            return "Light Pollution"
        elif pm25 <= Config.RISK_THRESHOLDS["Heavy Pollution"]:
            return "Heavy Pollution"
        else:
            return "Red Alert"

    def prepare_labels(self, df):
        df['risk_label'] = df['pm25'].apply(self._get_label)
        return df

    def train(self, X, y):
        print("Training Random Forest Classifier...")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        self.model.fit(X_train, y_train)
        
        # Evaluation
        y_pred = self.model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Feature Importance (SHAP)
        print("Explaining model with SHAP...")
        # Reduce background data for speed if needed
        explainer = shap.TreeExplainer(self.model)
        # shap_values = explainer.shap_values(X_test)
        
        # Depending on scikit-learn/shap version, output format varies. 
        # For multiclass, shap_values is a list of arrays (one for each class).
        # We will visualize Summary Plot for Class 0 (Safe) or Aggregate.
        
        # Save feature importances as JSON for Dashboard
        importances = dict(zip(X.columns, self.model.feature_importances_))
        print("Feature Importances:", importances)
        
        # Plotting (requires matplotlib)
        try:
            import matplotlib.pyplot as plt
            shap_values = explainer.shap_values(X_test)
            
            # Summary Plot
            plt.figure()
            # If multiclass, shap_values is a list. Take the first class (e.g., Safe) or aggregate?
            # Usually summary_plot handles list for multiclass
            shap.summary_plot(shap_values, X_test, show=False)
            
            os.makedirs(Config.PLOT_DIR, exist_ok=True)
            plot_path = os.path.join(Config.PLOT_DIR, "shap_summary.png")
            plt.savefig(plot_path, bbox_inches='tight')
            plt.close()
            print(f"SHAP Summary Plot saved to {plot_path}")
            
        except Exception as e:
            print(f"Warning: Could not generate SHAP plot: {e}")

        # Save model
        joblib.dump(self.model, os.path.join(Config.MODEL_DIR, "rf_classifier.pkl"))
        print("Classifier saved.")

    def predict(self, X):
        return self.model.predict(X)
