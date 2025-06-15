import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.express as px
import json
import time
import requests
import sqlite3

# ✅ Configuration de la page Streamlit
st.set_page_config(
    page_title="IoT Monitoring - Smart Agriculture",
    page_icon="📡",
    layout="wide"
)

st.title("📡 IoT Monitoring System - Smart Agriculture")
st.markdown("### Suivi en temps réel des paramètres agricoles")

# ✅ Paramètres MQTT et API
BROKER = "broker.hivemq.com"  # Exemple public, à modifier selon tes capteurs
TOPIC = "smart-agriculture/sensors"
API_URL = "http://iot-server/api/data"

# ✅ Connexion et récupération des données IoT
sensor_data = []  # Stockage temporaire

def on_connect(client, userdata, flags, rc):
    st.write("🔗 Connexion au broker MQTT réussie !")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    sensor_data.append(data)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER, 1883, 60)

# ✅ Récupération de données via API
def fetch_api_data():
    try:
        response = requests.get(API_URL)
        return response.json()
    except:
        st.error("🚨 Impossible de récupérer les données IoT !")

# ✅ Stockage et prétraitement des données
def store_data(data):
    conn = sqlite3.connect("iot_data.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sensors (
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            ph REAL,
            soil_moisture REAL
        )
    """)
    cursor.execute("INSERT INTO sensors VALUES (?, ?, ?, ?, ?)", data)
    conn.commit()
    conn.close()

# ✅ Visualisation interactive avec Plotly
def plot_data():
    df = pd.DataFrame(sensor_data)
    if not df.empty:
        fig = px.line(df, x="timestamp", y=["temperature", "humidity", "ph", "soil_moisture"], title="📊 Evolution des paramètres IoT")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnée disponible pour l'affichage.")

# ✅ Automatisation et alertes
def check_alerts():
    if sensor_data:
        latest = sensor_data[-1]
        if latest["humidity"] < 30:
            st.error("🚨 Alerte : Humidité trop basse !")
        if latest["ph"] < 5 or latest["ph"] > 8:
            st.warning("⚠️ Alerte : pH du sol hors norme.")

# ✅ Interface Streamlit
st.sidebar.title("🔍 Paramètres IoT")
if st.sidebar.button("🔄 Rafraîchir les données"):
    fetch_api_data()
    plot_data()
    check_alerts()

st.sidebar.info("Données mises à jour en temps réel grâce aux capteurs IoT.")

# ✅ Exécution continue du client MQTT
client.loop_start()
time.sleep(10)  # Simulation d'attente pour la réception des données
client.loop_stop()

st.write("🚀 Système IoT actif - Données mises à jour toutes les 10 secondes")
