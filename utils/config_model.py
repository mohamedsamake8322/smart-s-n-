import os
import urllib.request
from tensorflow import keras
import streamlit as st

MODEL_URL = "https://huggingface.co/mohamedsamake8322/smartagro-efficientnet-resnet/resolve/main/efficientnet_resnet.keras"
MODEL_PATH = "model/efficientnet_resnet.keras"

def download_model():
    """Télécharge le modèle .keras depuis Hugging Face si absent localement."""
    if not os.path.exists(MODEL_PATH):
        os.makedirs("model", exist_ok=True)
        with st.spinner("📥 Téléchargement du modèle depuis Hugging Face..."):
            try:
                urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
                st.success("✅ Modèle téléchargé avec succès.")
            except Exception as e:
                st.error(f"❌ Échec du téléchargement du modèle : {e}")
                st.stop()

@st.cache_resource
def load_model():
    """Charge le modèle avec cache une fois téléchargé."""
    download_model()
    return keras.models.load_model(MODEL_PATH, compile=False)
