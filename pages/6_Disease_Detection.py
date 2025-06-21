# 📦 Imports
# 🧠 1. Chargement & Configuration
import streamlit as st
import numpy as np
import os
import sys
import json
from PIL import Image, ImageEnhance
from datetime import datetime
from utils.disease_detector import DiseaseDetector
from utils.config_model import load_labels

# 🧠 Initialisation
st.set_page_config(page_title="Diagnostic Agricole Pro", page_icon="🩺", layout="wide")
sys.path.append(os.path.abspath("."))

# 📚 Chargement descriptions
@st.cache_data
def load_disease_descriptions():
    with open("data/all_diseases_translated.json", encoding="utf-8") as f:
        return json.load(f)

disease_descriptions = load_disease_descriptions()
class_mapping = load_labels()
detector = DiseaseDetector()
# 🔍 2. Prédiction + carte résumé
DISEASE_ICONS = {
    "Healthy": "✅",
    "Aphids on Vegetables": "🐛🥦",
    "Armyworms on Vegetables": "🐛🍃",
    "Blister Beetle": "🪲🔥",
    "Beet Leafhopper": "🪲🌿",
    "Colorado Potato Beetle": "🥔🪲",
    "Western Striped and Spotted Cucumber Beetle": "🥒🪲",
    "Spotted Cucumber Beetle": "🥒🐞",
    "Cutworms on Vegetables": "🐛✂️",
    "False Chinch Bug": "🐜❌",
    "Flea Beetles": "🪲🔬",
    "Tomato and Tobacco Hornworms": "🍅🐛",
    "Thrips on Vegetables": "🦟🥦",
    "Potato Leafhopper": "🥔🌿",
    "Two-Spotted Spider Mite": "🕷️🌱",
    "Corn Earworm / Tomato Fruitworm": "🌽🍅🐛",
    "Tomato Russet Mite": "🍅🕷️",
    "Whiteflies (Family: Aleyrodidae)": "🦟🌿",
    "Alfalfa Mosaic Virus": "🦠🌱",
    "Bacterial Canker": "🦠⚠️",
    "Bacterial Speck": "🦠🍅",
    "Beet Curly Top Virus": "🌀🦠",
    "Big Bud": "🌿💥",
    "Blossom End Rot": "🍅⚫",
    "Damping-Off": "🌱🚫",
    "Early Blight": "🍅🟠",
    "Fusarium Crown/Root Rot": "🌿🦠",
    "Fusarium Wilt": "🌾⚠️",
    "Late Blight": "🍅🔥",
    "Root-Knot Nematodes": "🌱🐛",
    "Phytophthora Root, Stem, and Crown Rots": "🌿🦠",
    "Powdery Mildew on Vegetables": "🍃🌫️",
    "Tobacco Mosaic Virus & Tomato Mosaic Virus": "🍅🌿🦠",
    "Tomato Spotted Wilt Virus": "🍅🔴",
    "Verticillium Wilt": "🌾🔴",
    "Cercospora Leaf Spot (Frogeye)": "🌿⚪",
    "Choanephora Blight (Wet Rot)": "🌿💧",
    "Gray Leaf Spot": "🌿🔘",
    "Phomopsis Blight": "🌿🔥",
}

def estimate_progression(conf):
    if conf > 90: return "🔴 Critique"
    elif conf > 75: return "🟠 Avancé"
    elif conf > 50: return "🟡 Début"
    else: return "🟢 Faible impact"

def predict_disease(image_pil, confidence_threshold=0.6):
    results = detector.predict(image_pil, confidence_threshold=confidence_threshold)
    preds = []
    for r in results:
        desc = next((d for d in disease_descriptions if d.get("name") == r["disease"]), {})
        preds.append({
            "name": f"{DISEASE_ICONS.get(r['disease'], '🦠')} {r['disease']}",
            "confidence": r["confidence"],
            "progression_stage": estimate_progression(r["confidence"]),
            "symptoms": desc.get("symptoms", "❌ Non disponibles"),
            "recommendations": desc.get("management", "❌ Aucune recommandation"),
        })
    return preds
# 💡 3. Fiche Diagnostique
def render_diagnostic_card(result):
    color = {
        "🔴 Critique": "red",
        "🟠 Avancé": "orange",
        "🟡 Début": "gold",
        "🟢 Faible impact": "green"
    }.get(result["progression_stage"], "gray")

    with st.container():
        st.markdown("---")
        st.markdown(f"### {result['name']}")
        st.markdown(f"<span style='color:{color}; font-weight:bold;'>Gravité : {result['progression_stage']}</span>", unsafe_allow_html=True)
        st.markdown(f"📊 **Confiance IA :** {result['confidence']:.1f}%")
        st.markdown(f"🧬 **Symptômes :** {result['symptoms']}")
        st.markdown(f"💊 **Recommandations :** {result['recommendations']}")
# 🖼️ 4. Interface Pro
st.title("🌿 Disease Detector Pro")
uploaded = st.file_uploader("Téléverser une image de la plante 🌱", type=["png", "jpg", "jpeg"])

if uploaded:
    try:
        image = Image.open(uploaded).convert("RGB")
        col1, col2 = st.columns(2)
        with col1:
            st.image(image, caption="🌱 Image originale", use_container_width=True)


        enhance = st.checkbox("🔬 Améliorer le contraste ?", value=True)
        if enhance:
            image = ImageEnhance.Contrast(image).enhance(1.2)

        with st.spinner("🧠 Diagnostic en cours..."):
            predictions = predict_disease(image)

        if predictions:
            st.success("✅ Analyse terminée")
            for result in predictions[:3]:
                render_diagnostic_card(result)
        else:
            st.info("ℹ️ Aucun symptôme détecté avec une confiance suffisante.")

    except Exception as e:
        st.error(f"❌ Erreur lors de l’analyse : {e}")
else:
    st.info("📷 Téléversez une image de la plante pour commencer.")
