import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_camel_telemetry_data(days=60):
    """Generates 60 days of telemetry data for camel activity and ambient heat load."""
    dates = [datetime.now() - timedelta(days=i) for i in range(days)][::-1]
    
    np.random.seed(42)
    base_activity = np.random.normal(loc=5200, scale=350, size=days)
    base_temp = np.random.normal(loc=36, scale=2.5, size=days)
    humidity = np.random.normal(loc=38, scale=4, size=days)
    
    # Simulate heatwave around day 42
    base_temp[40:46] += 9.5
    humidity[40:46] += 12.0
    base_activity[40:46] *= 0.40 
    
    df = pd.DataFrame({
        'date': [d.strftime('%Y-%m-%d') for d in dates],
        'activity_units': np.round(base_activity, 0),
        'temp_c': np.round(base_temp, 1),
        'humidity_pct': np.round(humidity, 1)
    })
    
    return df
