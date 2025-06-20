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
import json

LABELS_URL = "https://huggingface.co/mohamedsamake8322/smartagro-efficientnet-resnet/resolve/main/labels.json"
LABELS_PATH = "model/labels.json"

def load_labels():
    if not os.path.exists(LABELS_PATH):
        try:
            urllib.request.urlretrieve(LABELS_URL, LABELS_PATH)
        except Exception as e:
            st.error(f"❌ Impossible de télécharger labels.json : {e}")
            st.stop()
    with open(LABELS_PATH, "r") as f:
        return json.load(f)
