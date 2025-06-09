# === visualizations.py ===
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.dates as mdates
import streamlit as st
import folium
import sqlite3
import requests
import numpy as np
from streamlit_folium import st_folium
from folium.plugins import HeatMap

print("🚀 Script visualizations.py started...")

# 🌍 Definition of agricultural fields
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0},
    {"name": "Field B", "lat": 12.66, "lon": -7.98},
    {"name": "Field C", "lat": 12.63, "lon": -8.02},
]
def generate_map():
    m = folium.Map(location=[12.64, -8.0], zoom_start=12)
    return m  # Retourne l'objet carte
# 📊 Store data in SQLite
def create_database():
    conn = sqlite3.connect("fields_data.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fields (
        id INTEGER PRIMARY KEY,
        name TEXT,
        latitude REAL,
        longitude REAL,
        temperature REAL,
        humidity REAL,
        stress_level REAL
    )
    """)

    for field in FIELDS:
        cursor.execute("""
        INSERT INTO fields (name, latitude, longitude, temperature, humidity, stress_level)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (field["name"], field["lat"], field["lon"], 27, 60, 0.75))

    conn.commit()
    conn.close()
    print("✅ Data saved in SQLite!")

# 🌦️ Retrieve weather data
import requests

API_KEY = "2746334b2f4cc68fe6c1e8bd86b4922e"

FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0, "country": "Mali"},
    {"name": "Field B", "lat": 40.71, "lon": -74.01, "country": "USA"},
    {"name": "Field C", "lat": 48.85, "lon": 2.35, "country": "France"},
    {"name": "Field D", "lat": -23.55, "lon": -46.63, "country": "Brazil"},
    {"name": "Field E", "lat": 35.68, "lon": 139.76, "country": "Japan"},
]

def get_weather_data(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    return response.json()

# Récupération météo pour tous les champs
for field in FIELDS:
    weather_data = get_weather_data(field["lat"], field["lon"])
    if "main" in weather_data:
        temperature = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        print(f"🌍 {field['name']} ({field['country']}): {temperature}°C, Humidité: {humidity}%")
    else:
        print(f"⚠️ Erreur météo pour {field['name']} : {weather_data}")


# 🌦️ Update database with weather data
def update_weather():
    conn = sqlite3.connect("fields_data.db")
    cursor = conn.cursor()

    for field in FIELDS:
        weather = get_weather_data(field["lat"], field["lon"])
        
        if "main" in weather:
            temperature = weather["main"]["temp"]
            humidity = weather["main"]["humidity"]
        else:
            temperature, humidity = None, None  # ✅ Default values if API fails
            print(f"⚠️ Weather data error for {field['name']} : {weather}")

        stress_level = min(1, max(0, 0.5 + (temperature - 25) * 0.02))

        cursor.execute("UPDATE fields SET temperature=?, humidity=?, stress_level=? WHERE name=?",
                       (temperature, humidity, stress_level, field["name"]))

    conn.commit()
    conn.close()
    print("✅ Weather data updated!")

# 🌍 Generate Folium map
def generate_map():
    m = folium.Map(location=[12.64, -8.0], zoom_start=12)

    for field in FIELDS:
        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=f"{field['name']} - Stress Level: 0.75",
            icon=folium.Icon(color="green")
        ).add_to(m)

    return m  # 🔄 Returning the map object

# 📊 Yield Visualization Functions
def plot_yield_distribution(df):
    if "PredictedYield" not in df.columns:
        raise ValueError("❌ Column 'PredictedYield' is missing in DataFrame")

    fig, ax = plt.subplots()
    sns.histplot(df["PredictedYield"], bins=20, kde=True, color="green", ax=ax)
    ax.set_xlabel("Yield (tons/ha)")
    ax.set_ylabel("Frequency")
    fig.tight_layout()
    return fig

def plot_yield_pie(df):
    if "PredictedYield" not in df.columns:
        raise ValueError("❌ Column 'PredictedYield' is missing in DataFrame")

    bins = [0, 10, 20, 30, 50, 100]
    labels = ["<10", "10–20", "20–30", "30–50", ">50"]
    df["yield_bin"] = pd.cut(df["PredictedYield"], bins=bins, labels=labels, right=False)

    counts = df["yield_bin"].value_counts().sort_index()
    colors = sns.color_palette("pastel")

    fig, ax = plt.subplots()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90, colors=colors)
    ax.set_title("🎂 Predicted Yield Distribution (Pie Chart)")
    fig.tight_layout()
    return fig

def plot_yield_over_time(df):
    if "timestamp" not in df.columns or "PredictedYield" not in df.columns:
        raise ValueError("❌ Columns 'timestamp' and 'PredictedYield' are required in DataFrame")

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.sort_values("timestamp")

    fig, ax = plt.subplots()
    sns.lineplot(x="timestamp", y="PredictedYield", data=df, ax=ax, marker="o")
    ax.set_title("📈 Predicted Yield Trend Over Time")
    ax.set_xlabel("📅 Date")
    ax.set_ylabel("🌾 Yield (tons/ha)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    fig.tight_layout()
    return fig

# 🔥 Run all functionalities
if __name__ == "__main__":
    create_database()   # Initialize database
    update_weather()    # Update weather data

    # 🔍 Load fields data from SQLite
    conn = sqlite3.connect("fields_data.db")
    df = pd.read_sql("SELECT * FROM fields", conn)
    conn.close()

    # 📊 Streamlit Interface
    st.title("🌍 Agricultural Field Visualizations")

    # ✅ Display field data
    st.subheader("📊 Fields Data")
    st.dataframe(df)

    # ✅ Display Folium map
    st.subheader("🌍 Fields Map")
    map_object = generate_map()
    st_folium(map_object, width=700, height=500)

print("🚀 Visualizations and data updates completed successfully!")
