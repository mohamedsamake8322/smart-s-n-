import pandas as pd
import numpy as np
import random
import logging
import os

# 🚀 Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ✅ Definition of soil types and crops
soil_types = ['Sandy', 'Loamy', 'Clay', 'Silty']
crop_types = ['Maize', 'Rice', 'Wheat', 'Millet', 'Sorghum']

# ✅ Seed for reproducibility
np.random.seed(42)
random.seed(42)

# 🔹 Synthetic data generation
def generate_data(n=1000):
    logger.info(f"🚀 Generating {n} rows of synthetic data...")

    data = {
        'temperature': np.random.normal(loc=28, scale=5, size=n).round(2),
        'humidity': np.random.uniform(30, 90, n).round(2),
        'pH': np.random.uniform(4.5, 8.5, n).round(2),
        'rainfall': np.random.gamma(shape=2, scale=30, size=n).round(1),
        'soil_type': np.random.choice(soil_types, n),
        'crop_type': np.random.choice(crop_types, n),
    }

    df = pd.DataFrame(data)

    # 🔍 Yield calculation based on rules
    def estimate_yield(row):
        base_yield = {
            'Maize': 2000,
            'Rice': 2500,
            'Wheat': 2200,
            'Millet': 1800,
            'Sorghum': 1900
        }.get(row['crop_type'], 2000)  # Default value

        modifiers = 0
        if pd.isnull(row["temperature"]) or pd.isnull(row["rainfall"]) or pd.isnull(row["pH"]):
            return np.nan  # Ignore missing values

        if 6.0 <= row['pH'] <= 7.5:
            modifiers += 100
        if row['rainfall'] < 50:
            modifiers -= 300
        elif row['rainfall'] > 150:
            modifiers -= 200
        if row['temperature'] > 35:
            modifiers -= 150

        noise = np.random.normal(0, 100)
        return round(base_yield + modifiers + noise, 1)

    df['yield'] = df.apply(estimate_yield, axis=1)

    return df

# 🔥 Data generation and saving
df = generate_data()

if df.empty:
    logger.error("🚨 No data generated!")
    raise RuntimeError("🚨 Error: DataFrame is empty.")

# ✅ Save to `data.csv`
save_path = os.path.join(os.getcwd(), "data.csv")
df.to_csv(save_path, index=False)
logger.info(f"✅ Data generated and saved as {save_path} ({len(df)} rows).")
