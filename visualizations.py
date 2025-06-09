import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib.dates as mdates
import folium
import sqlite3
import requests
import numpy as np
from folium.plugins import HeatMap
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("API_KEY")

("🚀 Script visualizations.py started...")

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

# 🌦️ Retrieve weather data
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

        stress_level = min(1, max(0, 0.5 + (temperature - 25) * 0.02))

        cursor.execute("UPDATE fields SET temperature=?, humidity=?, stress_level=? WHERE name=?",
                       (temperature, humidity, stress_level, field["name"]))

    conn.commit()
    conn.close()

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
