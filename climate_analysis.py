import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import joblib
import os
import xgboost as xgb
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')  # ✅ Backend adapted to avoid display conflicts

# 🌍 API to fetch real-time climate data
WEATHER_API = "https://api.open-meteo.com/v1/forecast?latitude=35.6895&longitude=139.6917&hourly=temperature_2m"

# 📊 Loading the climate prediction model
MODEL_PATH = "model/climate_prediction.pkl"

# ✅ Fetching weather data via API
def fetch_weather_data():
    """Fetches real-time climate data."""
    try:
        response = requests.get(WEATHER_API)
        response.raise_for_status()
        data = response.json()
        temperature = np.array(data["hourly"]["temperature_2m"])
        return temperature
    except requests.exceptions.RequestException as e:
        print(f"🚨 Failed to fetch climate data: {e}")
        return None

# 📊 Generating climate trends over multiple periods
def generate_climate_trends():
    """Analyzes climate trends based on past historical data."""
    try:
        df = pd.read_csv("data/climate_history.csv")

        if "date" not in df.columns or "temperature" not in df.columns:
            raise ValueError("🚨 The 'date' and 'temperature' columns are missing from the dataset.")

        df["date"] = pd.to_datetime(df["date"])
        df.set_index("date", inplace=True)

        plt.figure(figsize=(12, 6))
        sns.lineplot(x=df.index, y=df["temperature"], label="Temperature")
        sns.lineplot(x=df.index, y=df["humidity"], label="Humidity", linestyle="dashed")
        plt.title("📊 Historical Climate Trends")
        plt.xlabel("Date")
        plt.ylabel("Normalized Values")
        plt.legend()
        plt.grid()
        plt.show()

        return df
    except Exception as e:
        print(f"🚨 Error in `generate_climate_trends`: {e}")
        return None

# ✅ Advanced analysis: Climate/soil correlation
def generate_climate_soil_correlation():
    """Analyzes the correlation between climate and soil quality using advanced models."""
    try:
        df_soil = pd.read_csv("data/soil_conditions.csv")

        numeric_df = df_soil.select_dtypes(include='number')

        if numeric_df.empty:
            raise ValueError("🚨 No numeric fields found in soil data!")

        # 🔍 Advanced normalization for better precision
        scaler = MinMaxScaler()
        numeric_df_scaled = pd.DataFrame(scaler.fit_transform(numeric_df), columns=numeric_df.columns)

        correlation = numeric_df_scaled.corr()

        plt.figure(figsize=(10, 8))
        sns.heatmap(correlation, annot=True, cmap="coolwarm", fmt=".2f")
        plt.title("📊 Advanced Soil-Climate Correlation Matrix")
        plt.show()
        plt.close()

        return correlation
    except Exception as e:
        print(f"🚨 Error in `generate_climate_soil_correlation`: {e}")
        return None

# ✅ Predicting future climate with ML model
def predict_future_climate(features):
    """Predicts future climate based on past trends and soil characteristics."""
    try:
        if not isinstance(features, dict):
            raise ValueError("🚨 Parameters must be provided as a dictionary.")

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"🚨 Model not found: {MODEL_PATH}")

        model = joblib.load(MODEL_PATH)
        input_data = pd.DataFrame([features])
        prediction = model.predict(input_data)

        return prediction[0]

    except Exception as e:
        print(f"🚨 Error in `predict_future_climate`: {e}")
        return None

# ✅ Detecting climatic and agricultural risks
def analyze_climate_risk(temperature, humidity, soil_type):
    """
    Analyzes agricultural and climatic risks:
    - Extreme drought or excessive rainfall risks
    - Impact of soil quality on crop growth
    """
    risk_factors = {
        "Loamy": {"humidity": 60, "temperature": 25, "risk": "⚠️ Moderate risk of soil acidification"},
        "Clay": {"humidity": 80, "temperature": 30, "risk": "⚠️ High risk of excessive water retention"},
        "Sandy": {"humidity": 50, "temperature": 35, "risk": "⚠️ Strong risk of drying out"}
    }

    risk_messages = []

    if soil_type in risk_factors:
        if humidity >= risk_factors[soil_type]["humidity"]:
            risk_messages.append(f"💧 High humidity -> {risk_factors[soil_type]['risk']}")
        if temperature >= risk_factors[soil_type]["temperature"]:
            risk_messages.append(f"🌡️ Critical temperature -> {risk_factors[soil_type]['risk']}")

    return "✅ No immediate risks detected." if not risk_messages else " | ".join(risk_messages)

# 🧪 **Module Testing**
if __name__ == "__main__":
    try:
        print("🔍 Fetching weather data...")
        temps_data = fetch_weather_data()
        if temps_data is not None:
            print(f"✅ Predicted average temperature: {np.mean(temps_data):.2f}°C")

        print("\n📊 Climate-Soil Correlation Analysis...")
        correlation_matrix = generate_climate_soil_correlation()
        if correlation_matrix is not None:
            print("✅ Correlation calculated successfully!")

        print("\n🔮 Climate Prediction...")
        future_climate = predict_future_climate({"temperature": 25, "humidity": 60, "pH": 6.5, "rainfall": 100})
        print(f"🌡️ Predicted Climate: {future_climate:.2f}")

        print("\n⚠️ Climate Risk Analysis...")
        climate_risk = analyze_climate_risk(temperature=30, humidity=85, soil_type="Clay")
        print(f"🌍 Detected Risk: {climate_risk}")

    except Exception as e:
        print(f"🚨 Error: {e}")
