import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "model", "efficientnet_resnet.keras")
MODEL_PATH = os.path.normpath(MODEL_PATH)
def check_model_presence():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"🚨 Modèle introuvable à l'emplacement : {MODEL_PATH}\n"
            "💡 Assure-toi qu’il est bien présent dans le dossier 'model/' au bon endroit."
        )
