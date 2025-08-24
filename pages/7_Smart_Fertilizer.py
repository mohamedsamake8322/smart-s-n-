# -----------------------------
# Imports
# -----------------------------
import streamlit as st
import pandas as pd
import os
from io import BytesIO

# 🔌 Modules personnalisés
from utils.fertilizer_api import predict_fertilizer
from utils.pdf_generator import build_pdf, build_excel
from utils.logger import log_prediction

# -----------------------------
# Paths
# -----------------------------
BASE = os.path.dirname(__file__)
DATA_FOLDER = r"C:\plateforme-agricole-complete-v2\Crop-Fertilizer-Analysis"

# -----------------------------
# Extraire cultures depuis CSV
# -----------------------------
def get_available_cultures(folder_path: str) -> list:
    cultures = set()
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder_path, file))
            for col in df.columns:
                if col.lower().strip() in ["label", "crop type", "culture"]:
                    cultures.update(df[col].dropna().unique())
    return sorted(list(cultures))

available_cultures = get_available_cultures(DATA_FOLDER)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌾 SmartFactLaser – Recommandation de fertilisant")

cols = st.columns(2)
with cols[0]:
    culture = st.selectbox("🌿 Type de culture", available_cultures)
    surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)
with cols[1]:
    soil_type = st.selectbox("🧱 Type de sol", ["Sandy", "Loamy", "Clayey", "Black", "Red"])
    moisture = st.number_input("Humidité du sol (%)", min_value=0, max_value=100, value=40)

st.markdown("### 🌤 Paramètres environnementaux")
temperature = st.number_input("Température (°C)", min_value=-10, max_value=50, value=28)
humidity = st.number_input("Humidité de l'air (%)", min_value=0, max_value=100, value=60)
nitrogen = st.number_input("Azote (N)", min_value=0, value=20)
phosphorous = st.number_input("Phosphore (P)", min_value=0, value=30)
potassium = st.number_input("Potassium (K)", min_value=0, value=10)

if st.button("🔍 Prédire fertilisant & Générer plan"):
    user_inputs = {
        "Temperature": temperature,
        "Humidity": humidity,
        "Moisture": moisture,
        "Soil Type": soil_type,
        "Crop Type": culture,
        "Nitrogen": nitrogen,
        "Phosphorous": phosphorous,
        "Potassium": potassium
    }

    try:
        fertilizer_name = predict_fertilizer(user_inputs)
        log_prediction(user_inputs, fertilizer_name)
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        st.stop()

    st.success(f"🧪 Fertilizer recommandé : {fertilizer_name}")

    # PDF
    pdf_bytes = build_pdf(culture, surface, fertilizer_name)
    st.download_button("📄 Télécharger le plan PDF", pdf_bytes, file_name=f"{culture}_fertilisation_plan.pdf", mime="application/pdf")

    # Excel
    excel_bytes = build_excel(culture, surface, fertilizer_name)
    st.download_button("📥 Télécharger Excel", excel_bytes, file_name=f"{culture}_fertilisation_plan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Explication
    st.markdown("### ℹ️ Explication rapide")
    st.write("- Le fertilisant est recommandé selon les conditions agro-climatiques et les besoins nutritionnels.")
    st.write("- Le modèle est entraîné sur des données réelles de fertilisation.")
    st.success("✅ Plan généré — téléchargez le PDF ou Excel ci-dessous.")
