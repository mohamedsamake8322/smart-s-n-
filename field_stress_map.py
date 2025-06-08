import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3
import requests
import logging
from folium.plugins import HeatMap
import os
from dotenv import load_dotenv

load_dotenv()  # 🔄 Chargement des variables d’environnement
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 🚀 Logger Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🌍 Definition of Agricultural Fields
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0},
    {"name": "Field B", "lat": 12.66, "lon": -7.98},
    {"name": "Field C", "lat": 12.63, "lon": -8.02},
]

# 🌦️ Weather Data Retrieval with Error Handling
def get_weather_data(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Weather API Error: {e}")
        return {"main": {"temp": 25}, "wind": {"speed": 5}}  # Default values

# 📊 Generating Stress Trends
def generate_stress_trend():
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    stress_values = np.random.uniform(0, 1, size=30)
    return pd.DataFrame({"Date": dates, "Stress Level": stress_values})

# 🔥 Generating Monthly Heatmap Data
def generate_stress_heatmap(fields):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    field_names = [field["name"] for field in fields]
    data = np.random.rand(len(fields), len(months))
    return data, field_names, months

# 🌍 Stress Prediction Based on Weather with Logs
def predict_stress(temp, wind_speed):
    base_stress = np.random.uniform(0.2, 0.8)
    temp_factor = -0.1 if temp < 15 else 0.1 if temp > 30 else 0
    wind_factor = 0.05 if wind_speed > 10 else 0
    stress_level = min(1, max(0, base_stress + temp_factor + wind_factor))
    
    logging.info(f"🚀 Stress Prediction: Temp={temp}°C, Wind={wind_speed} m/s → Stress={stress_level:.2f}")
    return stress_level

# 🎨 Display Visualizations
def display_stress_trend(df):
    st.subheader("📉 Stress Trend Over Time")
    st.line_chart(df.set_index("Date"))

def display_stress_heatmap(data, field_names, months):
    st.subheader("🔥 Monthly Stress Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(data, annot=True, xticklabels=months, yticklabels=field_names, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

def display_weather_prediction(fields, weather_data):
    st.subheader("🌍 Weather-based Stress Prediction")
    temperature = weather_data['main']['temp']
    wind_speed = weather_data['wind']['speed']
    
    for field in fields:
        predicted_stress = predict_stress(temperature, wind_speed)
        st.write(f"{field['name']} - Predicted Stress Level: {predicted_stress:.2f}")

# 🎯 **Main Execution**
if __name__ == "__main__":
    stress_trend_df = generate_stress_trend()
    display_stress_trend(stress_trend_df)

    heatmap_data, field_names, months = generate_stress_heatmap(FIELDS)
    display_stress_heatmap(heatmap_data, field_names, months)

    weather_data = get_weather_data("YOUR_API_KEY", FIELDS[0]["lat"], FIELDS[0]["lon"])
    display_weather_prediction(FIELDS, weather_data)
    
    logging.info("✅ Script executed successfully!")
