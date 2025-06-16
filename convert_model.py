from tensorflow.keras.models import load_model
import os

# 🔹 Définition des chemins
MODEL_PATH_H5 = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.h5"
MODEL_PATH_KERAS = "C:/plateforme-agricole-complete-v2/model/efficientnet_resnet.keras"

# 🔍 Vérification du dossier de sauvegarde
os.makedirs(os.path.dirname(MODEL_PATH_KERAS), exist_ok=True)

# ✅ Charger le modèle existant `.h5`
model = load_model(MODEL_PATH_H5)

# 🔄 Sauvegarder en `.keras`
model.save(MODEL_PATH_KERAS)

print(f"✅ Modèle converti et enregistré sous {MODEL_PATH_KERAS}")
