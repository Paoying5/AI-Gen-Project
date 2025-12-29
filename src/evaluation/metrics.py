import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy import stats

class ModelEvaluator:
    @staticmethod
    def calculate_metrics(y_true, y_pred, model_name="Model"):
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        mae = mean_absolute_error(y_true, y_pred)
        mape = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        print(f"--- {model_name} Performance ---")
        print(f"RMSE: {rmse:.4f}")
        print(f"MAE:  {mae:.4f}")
        print(f"MAPE: {mape:.2f}%")
        
        return {"RMSE": rmse, "MAE": mae, "MAPE": mape}

    @staticmethod
    def diebold_mariano_test(y_true, y_pred_1, y_pred_2, h=1):
        """
        Diebold-Mariano Test for comparison of predictive accuracy.
        H0: Both models have same accuracy.
        
        d_t = e_1^2 - e_2^2  (Using Squared Error loss)
        """
        e1 = (y_true - y_pred_1)**2
        e2 = (y_true - y_pred_2)**2
        d = e1 - e2
        
        d_mean = np.mean(d)
        d_var = np.var(d, ddof=1)
        
        # DM Statistic
        dm_stat = d_mean / np.sqrt(d_var / len(d))
        
        # p-value (two-tailed)
        p_value = 2 * (1 - stats.norm.cdf(np.abs(dm_stat)))
        
        print(f"\n--- Diebold-Mariano Test ---")
        print(f"DM Statistic: {dm_stat:.4f}")
        print(f"p-value: {p_value:.6f}")
        
        if p_value < 0.05:
            print("=> Reject H0: Significant difference between models.")
            if dm_stat < 0:
                print("=> Model 1 has lower errors (Better).")
            else:
                print("=> Model 2 has lower errors (Better).")
        else:
            print("=> Fail to Reject H0: No significant difference.")
            
        return dm_stat, p_value
