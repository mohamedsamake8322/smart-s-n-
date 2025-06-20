import os
import requests

MODEL_URL = "https://drive.google.com/uc?export=download&id=1mBKbOYqB6db3KDneEtSpcH9ywC55qfW_"
MODEL_PATH = os.path.join("model", "efficientnet_resnet.keras")

def download_model_if_missing():
    if not os.path.exists(MODEL_PATH):
        print("⬇️ Téléchargement du modèle depuis Google Drive...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            f.write(requests.get(MODEL_URL).content)
        print("✅ Modèle téléchargé avec succès.")
