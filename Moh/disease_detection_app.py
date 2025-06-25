import streamlit as st
import json, os
from PIL import Image, ImageEnhance
import numpy as np
import tensorflow as tf
from collections import defaultdict
from datetime import datetime

# 🕒 Heure de session
session_time = datetime.now().strftime("%Y-%m-%d %H:%M")

# 🌐 Configuration
st.set_page_config(page_title="🌱 Diagnostic Intelligent", layout="wide")
st.title("🧠 Analyse IA de la maladie")

# 📱 CSS responsive
st.markdown("""
<style>
@media (max-width: 768px) {
  .block-container { padding: 1rem; }
  .stButton>button { font-size: 1.1rem; }
  .stTextInput, .stFileUploader { font-size: 1.05rem; }
}
</style>
""", unsafe_allow_html=True)

# 🔧 Chemins des ressources
MODEL_PATH = "model/efficientnet_agro_final.keras"
FICHES_PATH = "mapping_fiches_maladies.json"
IMAGE_DIR = "illustrations"
REPARTITION_JSON = "repartition_maladies_afrique.json"

# 📥 Chargement du modèle
@st.cache_resource
def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

model = load_model()

# 📖 Chargement des fiches
@st.cache_data
def load_fiches():
    with open(FICHES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

fiches = load_fiches()

# 🌍 Chargement de la répartition par pays
@st.cache_data
def charger_repartition_par_pays(json_path=REPARTITION_JSON):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    pays_maladies = defaultdict(list)
    for maladie, liste_pays in data.items():
        for pays in liste_pays:
            pays_maladies[pays.strip()].append(maladie)
    return dict(pays_maladies)

repartition = charger_repartition_par_pays()

# 🧠 Prédiction
def predict_image(img):
    img_resized = img.resize((224, 224))
    img_array = np.expand_dims(np.array(img_resized) / 255.0, axis=0)
    predictions = model.predict(img_array)[0]
    class_index = np.argmax(predictions)
    confidence = float(predictions[class_index])
    return class_index, confidence

# 🎯 Noms de classes
CLASS_NAMES = list(fiches.keys())

# 📷 Upload image
uploaded_file = st.file_uploader("📸 Importer une image de plante", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file).convert("RGB")
    st.image(image, caption="🌿 Image importée", width=300)

    if st.button("🔬 Diagnostiquer"):
        with st.spinner("Analyse de l’image en cours..."):
            idx, score = predict_image(image)
            maladie = CLASS_NAMES[idx]
            confiance = round(score * 100, 1)
            fiche = fiches.get(maladie, {})

        st.success(f"✅ Maladie détectée : **{maladie}** ({confiance}%)")
        st.subheader("📋 Détails de la fiche")
        st.markdown(f"**Culture :** {fiche.get('culture', 'N/A')}")
        st.markdown(f"**Symptômes :** {fiche.get('symptômes', 'N/A')}")
        st.markdown(f"**Traitement :** {fiche.get('traitement', 'N/A')}")

        # 🖼️ Images illustratives
        st.markdown("---")
        st.subheader("📸 Références visuelles similaires")
        disease_folder = os.path.join(IMAGE_DIR, maladie.replace(" ", "_"))

        if os.path.isdir(disease_folder):
            images = [f for f in os.listdir(disease_folder) if f.endswith((".jpg", ".png", ".jpeg"))]
            for img_name in images[:4]:
                img_path = os.path.join(disease_folder, img_name)
                st.image(img_path, use_column_width=True)
        else:
            st.info("Pas d’illustrations disponibles pour cette maladie.")

# 🌍 Répartition des maladies par pays
st.title("🌍 Répartition géographique des maladies")
pays_disponibles = sorted(repartition.keys())
pays_selectionne = st.selectbox("Sélectionnez un pays :", pays_disponibles)

if pays_selectionne:
    maladies = sorted(repartition[pays_selectionne])
    st.success(f"{len(maladies)} maladies détectées en **{pays_selectionne}** :")
    for m in maladies:
        st.markdown(f"• {m}")

# Footer
st.caption(f"📅 {session_time} – Mohamed'SAMAKE Diagnostic Interface")
