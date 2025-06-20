import os
import gdown

MODEL_PATH = os.path.join("model", "efficientnet_resnet.keras")
DRIVE_ID = "1mBKbOYqB6db3KDneEtSpcH9ywC55qfW_"

def download_model_if_missing():
    if not os.path.exists(MODEL_PATH):
        print("⬇️ Téléchargement du modèle depuis Google Drive avec gdown...")
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        gdown.download(id=DRIVE_ID, output=MODEL_PATH, quiet=False)
        print("✅ Modèle téléchargé.")

__all__ = ["MODEL_PATH", "download_model_if_missing"]
