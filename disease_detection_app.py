import streamlit as st
import json, os
from PIL import Image, ImageEnhance
import numpy as np
import tensorflow as tf

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
IMAGE_DIR = "illustrations"  # 📁 Dossier contenant images par maladie (optionnel)

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

# 🧠 Prédiction
def predict_image(img):
    img_resized = img.resize((224, 224))
    img_array = np.expand_dims(np.array(img_resized) / 255.0, axis=0)
    predictions = model.predict(img_array)[0]
    class_index = np.argmax(predictions)
    confidence = float(predictions[class_index])
    return class_index, confidence

# 🎯 Mapping des classes (à personnaliser selon ton modèle)
CLASS_NAMES = list(fiches.keys())  # supposer que classes == clés du JSON

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

        # 🖼️ Images illustratives (si dispo)
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

# Affichage
st.title("📊 Répartition des maladies par pays")
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Pays:N", sort="-y"),
    y="Nombre de maladies:Q"
).properties(width=800)
st.altair_chart(chart, use_container_width=True)
# Footer
st.caption(f"📅 {session_time} – Mohamed'SAMAKE Diagnostic Interface")
