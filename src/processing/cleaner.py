import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
import os
import sys

# Config path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

class DataCleaner:
    def __init__(self):
        self.imputer = KNNImputer(n_neighbors=5)

    def handle_missing_values(self, df):
        """
        Imputes missing values using KNN.
        Numeric columns only.
        """
        print("Cleaning: Handling missing values...")
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # Keep non-numeric to concat back later if needed, but for time series we mostly deal with numeric
        # Assuming 'timestamp' is index or separate
        
        df_numeric = df[numeric_cols]
        df_imputed = pd.DataFrame(self.imputer.fit_transform(df_numeric), columns=numeric_cols, index=df.index)
        
        # Restore non-numeric
        for col in df.columns:
            if col not in numeric_cols:
                df_imputed[col] = df[col]
                
        return df_imputed

    def remove_outliers(self, df, columns, factor=3.0):
        """
        Removes outliers using IQR method.
        Factor 3.0 is for extreme outliers.
        """
        print(f"Cleaning: Removing outliers from {columns}...")
        df_clean = df.copy()
        for col in columns:
            Q1 = df_clean[col].quantile(0.25)
            Q3 = df_clean[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - factor * IQR
            upper_bound = Q3 + factor * IQR
            
            # Cap/Floor or Remove? For Time Series, Removing creates gaps. Capping is safer.
            df_clean[col] = np.where(df_clean[col] < lower_bound, lower_bound, df_clean[col])
            df_clean[col] = np.where(df_clean[col] > upper_bound, upper_bound, df_clean[col])
            
        return df_clean

    def save_processed(self, df, filename="clean_data.parquet"):
        path = os.path.join(Config.DATA_WAREHOUSE_DIR, filename)
        os.makedirs(Config.DATA_WAREHOUSE_DIR, exist_ok=True)
        df.to_parquet(path)
        print(f"Saved processed data to Data Warehouse: {path}")
        return path
