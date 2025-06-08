import streamlit as st
import folium
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import logging
import os
import requests
from dotenv import load_dotenv
from folium.plugins import HeatMap

# 🔄 Chargement des variables d’environnement
load_dotenv()  
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 🚀 Vérification de la clé API
if not API_KEY or API_KEY == "CLE_INVALIDE":
    raise RuntimeError("🚨 ERREUR : La clé API OpenWeather est manquante ou invalide !")

# 📝 Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"🔄 Clé API chargée : {API_KEY}")

# 🌍 Définition des champs agricoles
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0},
    {"name": "Field B", "lat": 12.66, "lon": -7.98},
    {"name": "Field C", "lat": 12.63, "lon": -8.02},
]

# 🌦️ Récupération des données météo
def get_weather_data(api_key, lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Erreur API météo : {e}")
        st.error("⚠️ Impossible de récupérer les données météo. Vérifie ta connexion ou ta clé API.")
        return None

# 🔥 Génération des tendances de stress
def generate_stress_trend():
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    stress_values = np.random.uniform(0, 1, size=30)
    return pd.DataFrame({"Date": dates, "Stress Level": stress_values})

# 🔥 Génération des données de heatmap mensuelle
def generate_stress_heatmap(fields):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    field_names = [field["name"] for field in fields]
    data = np.random.rand(len(fields), len(months))
    return data, field_names, months

# 🌍 Prédiction du stress basé sur la météo
def predict_stress(temp, wind_speed):
    base_stress = np.random.uniform(0.2, 0.8)
    temp_factor = -0.1 if temp < 15 else 0.1 if temp > 30 else 0
    wind_factor = 0.05 if wind_speed > 10 else 0
    stress_level = min(1, max(0, base_stress + temp_factor + wind_factor))

    logging.info(f"🚀 Stress Prediction: Temp={temp}°C, Wind={wind_speed} m/s → Stress={stress_level:.2f}")
    return stress_level

# 🎨 Affichage de la tendance du stress
def display_stress_trend(df):
    st.subheader("📉 Stress Trend Over Time")
    st.line_chart(df.set_index("Date"))

# 🎨 Affichage de la heatmap de stress
def display_stress_heatmap(data, field_names, months):
    st.subheader("🔥 Monthly Stress Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(data, annot=True, xticklabels=months, yticklabels=field_names, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

# 🗺️ Affichage de la carte interactive
def display_map(fields, weather_data):
    st.subheader("🗺️ Carte des champs agricoles")

    if weather_data:
        temperature = weather_data["main"]["temp"]
        wind_speed = weather_data["wind"]["speed"]
    else:
        temperature, wind_speed = 25, 5  # Valeurs par défaut

    m = folium.Map(location=[fields[0]["lat"], fields[0]["lon"]], zoom_start=12)

    for field in fields:
        stress = predict_stress(temperature, wind_speed)
        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=f"{field['name']} - Stress Level: {stress:.2f}",
            icon=folium.Icon(color="red" if stress > 0.5 else "green"),
        ).add_to(m)

    st_folium(m, width=700, height=500)

# 🌍 Affichage de la prédiction météo et du stress
def display_weather_prediction(fields, weather_data):
    st.subheader("🌍 Weather-based Stress Prediction")

    if not weather_data:
        st.warning("⚠️ Données météo non disponibles")
        return

    temperature = weather_data['main']['temp']
    wind_speed = weather_data['wind']['speed']

    for field in fields:
        predicted_stress = predict_stress(temperature, wind_speed)
        st.write(f"{field['name']} - Predicted Stress Level: {predicted_stress:.2f}")

# 🎯 **Streamlit UI**
menu_option = st.sidebar.selectbox("📂 Menu", ["🏠 Accueil", "🗺️ Carte des champs agricoles", "📊 Tendances de stress", "🔥 Heatmap du stress"])

if menu_option == "📊 Tendances de stress":
    stress_trend_df = generate_stress_trend()
    display_stress_trend(stress_trend_df)

elif menu_option == "🔥 Heatmap du stress":
    heatmap_data, field_names, months = generate_stress_heatmap(FIELDS)
    display_stress_heatmap(heatmap_data, field_names, months)

elif menu_option == "🗺️ Carte des champs agricoles":
    weather_data = get_weather_data(API_KEY, FIELDS[0]["lat"], FIELDS[0]["lon"])
    display_map(FIELDS, weather_data)
    display_weather_prediction(FIELDS, weather_data)

st.success("✅ Application lancée avec succès ! 🚀")
