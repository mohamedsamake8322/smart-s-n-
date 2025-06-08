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

# 🔄 Chargement des variables d’environnement
load_dotenv()  
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 🚀 Vérification de la clé API
if not API_KEY or API_KEY == "CLE_INVALIDE":
    st.warning("⚠️ La clé API OpenWeather est absente ou invalide. Certaines fonctionnalités seront limitées.")

# 📝 Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 🌍 Définition des champs agricoles
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0, "stress": 0.75},
    {"name": "Field B", "lat": 12.66, "lon": -7.98, "stress": 0.75},
    {"name": "Field C", "lat": 12.63, "lon": -8.02, "stress": 0.75},
]

# 🌦️ Récupération des données météo
@st.cache_data
def get_weather_data(api_key, lat, lon):
    if not api_key:
        return None
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Erreur API météo : {e}")
        st.error("⚠️ Impossible de récupérer les données météo.")
        return None

# 🌍 Prédiction du stress basée sur la météo
def predict_stress(temp, wind_speed):
    """ Estime le stress en fonction de la météo. """
    base_stress = np.random.uniform(0.2, 0.8)
    temp_factor = -0.1 if temp < 15 else 0.1 if temp > 30 else 0
    wind_factor = 0.05 if wind_speed > 10 else 0
    return min(1, max(0, base_stress + temp_factor + wind_factor))

# 🗺️ Affichage de la carte interactive combinée
def display_map(fields, weather_data):
    st.subheader("🗺️ Carte interactive des champs")

    m = folium.Map(location=[fields[0]["lat"], fields[0]["lon"]], zoom_start=12)

    # 🔹 Ajout des marqueurs statiques
    for field in fields:
        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=f"{field['name']} - Stress Level (statique): {field['stress']:.2f}",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    # 🔹 Ajout des marqueurs dynamiques basés sur la météo
    if weather_data:
        temperature = weather_data["main"]["temp"]
        wind_speed = weather_data["wind"]["speed"]
    else:
        temperature, wind_speed = 25, 5  # Valeurs par défaut

    for field in fields:
        stress = predict_stress(temperature, wind_speed)
        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=f"{field['name']} - Stress Level (météo): {stress:.2f}",
            icon=folium.Icon(color="red" if stress > 0.5 else "green"),
        ).add_to(m)

    st_folium(m, width=700, height=500)

# 🎯 **Streamlit UI**
menu_option = st.sidebar.selectbox("📂 Menu", ["🏠 Accueil", "🗺️ Carte des champs agricoles", "📊 Tendances de stress"])

if menu_option == "🗺️ Carte des champs agricoles":
    weather_data = get_weather_data(API_KEY, FIELDS[0]["lat"], FIELDS[0]["lon"])
    display_map(FIELDS, weather_data)

st.success("✅ Application améliorée avec les deux cartes ! 🚀")
