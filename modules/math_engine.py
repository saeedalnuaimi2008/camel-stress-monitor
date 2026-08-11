import numpy as np
import pandas as pd

def calculate_thi(temp_c, humidity_pct):
    """
    Calculates Livestock Temperature-Humidity Index (THI).
    Formula: THI = (1.8 * T + 32) - (0.55 - 0.55 * (RH / 100)) * (1.8 * T - 26)
    """
    thi = (1.8 * temp_c + 32.0) - (0.55 - 0.55 * (humidity_pct / 100.0)) * (1.8 * temp_c - 26.0)
    
    if thi >= 89.0:
        status = "EXTREME_HAZARD"
    elif thi >= 79.0:
        status = "MODERATE_STRESS"
    elif thi >= 72.0:
        status = "MILD_ALERT"
    else:
        status = "COMFORT"
        
    return round(thi, 1), status

def calculate_camel_activity_ewma(df, activity_col='activity_units', acute_days=7, chronic_days=28):
    """
    Calculates EWMA Acute vs Chronic activity levels for camel health tracking.
    A drop in acute activity relative to chronic baseline indicates lethargy/illness.
    """
    data = df.copy()
    
    lambda_acute = 2 / (acute_days + 1)
    lambda_chronic = 2 / (chronic_days + 1)
    
    data['acute_activity'] = data[activity_col].ewm(alpha=lambda_acute, adjust=False).mean()
    data['chronic_activity'] = data[activity_col].ewm(alpha=lambda_chronic, adjust=False).mean()
    
    # Activity Ratio: Acute / Chronic (< 0.7 indicates acute lethargy drop)
    data['activity_ratio'] = data['acute_activity'] / data['chronic_activity']
    
    return data
