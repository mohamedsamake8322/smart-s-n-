import os

# Chemin relatif depuis la racine du projet
MODEL_PATH = os.path.join("model", "efficientnet_resnet.keras")

def check_model_presence():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"🚨 Modèle introuvable à l'emplacement {MODEL_PATH}. "
            "Vérifie que le fichier existe bien localement."
        )
