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
if not API_KEY:
    raise RuntimeError("🚨 ERREUR : La clé API OpenWeather est manquante ou invalide !")

# 📝 Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"🔄 Clé API chargée avec succès.")

# 🌍 Définition des champs agricoles
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0},
    {"name": "Field B", "lat": 12.66, "lon": -7.98},
    {"name": "Field C", "lat": 12.63, "lon": -8.02},
]

# 🌦️ Récupération des données météo
def get_weather_data(api_key, lat, lon):
    """Récupère les données météo via OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Erreur API météo : {e}")
        st.error("⚠️ Impossible de récupérer les données météo.")
        return None

# 🔥 Génération des tendances de stress
def generate_stress_trend():
    """Génère une tendance fictive de stress sur 30 jours."""
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    stress_values = np.random.uniform(0.2, 0.8, size=30)  # Normalisé pour éviter les extrêmes
    return pd.DataFrame({"Date": dates, "Stress Level": stress_values})

# 🔥 Génération des données de heatmap mensuelle
def generate_stress_heatmap(fields):
    """Génère une heatmap des niveaux de stress pour chaque champ."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    field_names = [field["name"] for field in fields]
    data = np.random.uniform(0.2, 0.8, size=(len(fields), len(months)))  # Valeurs normalisées
    return data, field_names, months

# 🌍 Calcul du stress basé sur la météo
def predict_stress(temp, wind_speed):
    """Calcule le niveau de stress basé sur la température et la vitesse du vent."""
    base_stress = np.random.uniform(0.2, 0.8)  # Valeur de base normalisée
    temp_factor = -0.1 if temp < 15 else 0.1 if temp > 30 else 0
    wind_factor = 0.05 if wind_speed > 10 else 0
    stress_level = min(1, max(0.2, base_stress + temp_factor + wind_factor))  # Normalisation du stress
    return round(stress_level, 2)

# 🎨 Affichage des données
def display_stress_trend(df):
    """Affiche la tendance du stress sous forme de graphique."""
    st.subheader("📉 Évolution du stress sur 30 jours")
    st.line_chart(df.set_index("Date"))

def display_stress_heatmap(data, field_names, months):
    """Affiche une heatmap mensuelle des niveaux de stress."""
    st.subheader("🔥 Heatmap des niveaux de stress")
    fig, ax = plt.subplots()
    sns.heatmap(data, annot=True, xticklabels=months, yticklabels=field_names, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

def display_map(fields, weather_data):
    """Affiche une carte interactive avec les prédictions de stress des champs agricoles."""
    st.subheader("🗺️ Carte des champs agricoles")

    m = folium.Map(location=[fields[0]["lat"], fields[0]["lon"]], zoom_start=12)

    for field in fields:
        weather_data = get_weather_data(API_KEY, field["lat"], field["lon"])
        if weather_data:
            temp = weather_data["main"]["temp"]
            wind_speed = weather_data["wind"]["speed"]
            stress = predict_stress(temp, wind_speed)
        else:
            stress = 0.5  # Valeur neutre en cas d'erreur API

        popup_text = f"{field['name']} - Stress Level: {stress:.2f}"
        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=popup_text,
            icon=folium.Icon(color="red" if stress > 0.5 else "green"),
        ).add_to(m)

    st_folium(m, width=700, height=500)

def display_weather_prediction(fields):
    """Affiche les prédictions météo et stress pour chaque champ."""
    st.subheader("🌍 Prédictions météo & stress")
    
    for field in fields:
        weather_data = get_weather_data(API_KEY, field["lat"], field["lon"])
        
        if not weather_data:
            st.warning(f"⚠️ Données météo indisponibles pour {field['name']}")
            continue  

        temp = weather_data['main']['temp']
        wind_speed = weather_data['wind']['speed']
        predicted_stress = predict_stress(temp, wind_speed)

        st.write(f"📍 {field['name']} - Temp : {temp}°C | Vent : {wind_speed} m/s | Stress : {predicted_stress:.2f}")

# 🎯 **Streamlit UI**
menu_option = st.sidebar.radio("📂 Sélectionnez une section", ["🏠 Accueil", "🗺️ Carte interactive", "📊 Tendances de stress", "🔥 Heatmap du stress"])

if menu_option == "🏠 Accueil":
    st.title("🚀 Bienvenue sur l'analyse du stress des champs agricoles !")
    st.write("Utilisez le menu pour explorer les différentes visualisations.")

elif menu_option == "📊 Tendances de stress":
    stress_trend_df = generate_stress_trend()
    display_stress_trend(stress_trend_df)

elif menu_option == "🔥 Heatmap du stress":
    heatmap_data, field_names, months = generate_stress_heatmap(FIELDS)
    display_stress_heatmap(heatmap_data, field_names, months)

elif menu_option == "🗺️ Carte interactive":
    display_map(FIELDS, None)
    display_weather_prediction(FIELDS)

st.success("✅ Application lancée avec succès ! 🚀")
