﻿import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import plotly.express as px
import json
import time
import requests
import sqlite3

# âœ… Configuration de la page Streamlit
st.set_page_config(
    page_title="IoT Monitoring - Smart Agriculture",
    page_icon="ðŸ“¡",
    layout="wide"
)

st.title("ðŸ“¡ IoT Monitoring System - Smart Agriculture")
st.markdown("### Suivi en temps rÃ©el des paramÃ¨tres agricoles")

# âœ… ParamÃ¨tres MQTT et API
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "smart-agriculture/sensors"
API_URL = "http://iot-server/api/data"

# âœ… Stockage temporaire des donnÃ©es IoT
sensor_data = []

# âœ… Connexion MQTT et rÃ©cupÃ©ration des donnÃ©es IoT
def on_connect(client, userdata, flags, rc):
    """ExÃ©cutÃ©e lors de la connexion au broker MQTT."""
    st.write("ðŸ”— Connexion au broker MQTT rÃ©ussie !")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    """ExÃ©cutÃ©e lorsqu'un message MQTT est reÃ§u."""
    try:
        data = json.loads(msg.payload)
        sensor_data.append(data)
    except json.JSONDecodeError:
        st.error("ðŸš¨ Erreur de dÃ©codage des donnÃ©es MQTT reÃ§ues !")

# âœ… Initialisation du client MQTT
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# âœ… Fonction de rÃ©cupÃ©ration des donnÃ©es via API
def fetch_api_data():
    try:
        response = requests.get(API_URL)
        return response.json()
    except requests.RequestException:
        st.error("ðŸš¨ Impossible de rÃ©cupÃ©rer les donnÃ©es IoT via lâ€™API !")
        return {}

# âœ… Stockage et prÃ©traitement des donnÃ©es
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

# âœ… Visualisation interactive avec Plotly
def plot_data():
    df = pd.DataFrame(sensor_data)
    if not df.empty:
        fig = px.line(df, x="timestamp", y=["temperature", "humidity", "ph", "soil_moisture"], title="ðŸ“Š Evolution des paramÃ¨tres IoT")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Aucune donnÃ©e disponible pour l'affichage.")

# âœ… Automatisation et alertes
def check_alerts():
    if sensor_data:
        latest = sensor_data[-1]
        if latest["humidity"] < 30:
            st.error("ðŸš¨ Alerte : HumiditÃ© trop basse !")
        if latest["ph"] < 5 or latest["ph"] > 8:
            st.warning("âš ï¸ Alerte : pH du sol hors norme.")

# âœ… Interface Streamlit
st.sidebar.title("ðŸ” ParamÃ¨tres IoT")
if st.sidebar.button("ðŸ”„ RafraÃ®chir les donnÃ©es"):
    fetch_api_data()
    plot_data()
    check_alerts()

st.sidebar.info("DonnÃ©es mises Ã  jour en temps rÃ©el grÃ¢ce aux capteurs IoT.")

# âœ… DÃ©marrer l'Ã©coute MQTT en continu
client.loop_start()

st.write("ðŸš€ SystÃ¨me IoT actif - DonnÃ©es mises Ã  jour en temps rÃ©el !")


