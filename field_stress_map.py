import folium
import numpy as np
import pandas as pd
import requests
import logging
import os
import matplotlib

from dotenv import load_dotenv
from folium.plugins import HeatMap

# ✅ Désactivation de l'interface graphique interactive pour éviter les erreurs de thread
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 🔄 Chargement des variables d’environnement
load_dotenv()

# 🔹 Récupération de l’API_KEY OpenWeather
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

if not WEATHER_API_KEY:
    raise RuntimeError("🚨 ERREUR : La clé API OpenWeather est manquante ou invalide ! Vérifie ton fichier .env.")
else:
    print(f"✅ Clé API bien chargée : {WEATHER_API_KEY[:10]}******")  # 🔎 Vérification
# 📝 Configuration des logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info("🔄 Clé API chargée avec succès.")

# 🌍 Définition des champs agricoles
FIELDS = [
    {"name": "Field A", "lat": 12.64, "lon": -8.0},
    {"name": "Field B", "lat": 12.66, "lon": -7.98},
    {"name": "Field C", "lat": 12.63, "lon": -8.02},
]

# 🌦️ Récupération des données météo
def get_weather_data(lat, lon):
    """Récupère les données météo via OpenWeather API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"

    try:
        response = requests.get(url, timeout=5)  # ✅ Ajout d'un timeout pour éviter les blocages
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"🚨 Erreur API météo pour {lat}, {lon} : {e}")
        return None

# 🔥 Génération des tendances de stress
def generate_stress_trend():
    """Génère une tendance fictive de stress sur 30 jours."""
    dates = pd.date_range(start="2025-01-01", periods=30, freq="D")
    stress_values = np.random.uniform(0.2, 0.8, size=30)
    return pd.DataFrame({"Date": dates, "Stress Level": stress_values})

def display_stress_trend():
    """Affiche la tendance du stress sous forme de graphique."""
    plt.close('all')  # ✅ Nettoyage des graphiques précédents
    df = generate_stress_trend()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["Date"], df["Stress Level"], marker="o", linestyle="-", color="blue")
    ax.set_xlabel("Date")
    ax.set_ylabel("Stress Level")
    ax.set_title("Évolution du stress sur 30 jours")
    ax.grid(True)
    plt.savefig("stress_trend.png")  # ✅ Sauvegarde pour éviter les erreurs GUI
    return fig

# 🔥 Génération des données de heatmap mensuelle
def generate_stress_heatmap(fields):
    """Génère une heatmap des niveaux de stress pour chaque champ."""
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    field_names = [field["name"] for field in fields]
    data = np.random.uniform(0.2, 0.8, size=(len(fields), len(months)))
    return data, field_names, months

# 🌍 Calcul du stress basé sur la météo
def predict_stress(temp, wind_speed):
    """Calcule le niveau de stress basé sur la température et la vitesse du vent."""
    base_stress = np.random.uniform(0.2, 0.8)
    temp_factor = -0.1 if temp < 15 else 0.1 if temp > 30 else 0
    wind_factor = 0.05 if wind_speed > 10 else 0
    stress_level = min(1, max(0.2, base_stress + temp_factor + wind_factor))
    return round(stress_level, 2)

def display_weather_prediction():
    """Affiche la prédiction météo pour chaque champ."""
    for field in FIELDS:
        weather_data = get_weather_data(field["lat"], field["lon"])
        if weather_data:
            temp = weather_data["main"]["temp"]
            humidity = weather_data["main"]["humidity"]
            logging.info(f"🌍 {field['name']}: Température: {temp}°C, Humidité: {humidity}%")
        else:
            logging.warning(f"🚨 Données météo indisponibles pour {field['name']}")

# 🗺️ Génération de la carte Folium
def generate_map(fields):
    """Génère une carte Folium interactive avec les niveaux de stress des champs."""
    m = folium.Map(location=[fields[0]["lat"], fields[0]["lon"]], zoom_start=12, control_scale=True)

    for field in fields:
        weather_data = get_weather_data(field["lat"], field["lon"])
        if weather_data:
            temp = weather_data["main"]["temp"]
            wind_speed = weather_data["wind"]["speed"]
            stress = predict_stress(temp, wind_speed)
        else:
            temp, wind_speed, stress = "N/A", "N/A", 0.5  # Valeur neutre en cas d'erreur API

        popup_text = f"""<b>{field['name']}</b><br>
                         🌡 Température: {temp}°C<br>
                         🌬 Vent: {wind_speed} m/s<br>
                         🔥 Stress Level: {stress:.2f}"""

        folium.Marker(
            location=[field["lat"], field["lon"]],
            popup=folium.Popup(popup_text, max_width=300),
            icon=folium.Icon(color="red" if stress > 0.5 else "green", icon="info-sign")
        ).add_to(m)

    return m  # ✅ Retourne la carte pour être utilisée dans app.py
print(f"✅ Vérification API_KEY utilisée : {WEATHER_API_KEY[:10]}******")
