from tensorflow import keras
import json

MODEL_PATH = "model/efficientnet_resnet.keras"

try:
    model = keras.models.load_model(MODEL_PATH, compile=False)
    print("✅ Le modèle a été chargé avec succès.")
except Exception as e:
    print(f"❌ Erreur lors du chargement du modèle : {e}")
    exit()

# 🔍 Affichage du résumé des couches
print("\n📋 Structure du modèle :")
model.summary()

# 🔎 Vérifie s’il y a des couches de normalisation implicites
print("\n🧪 Recherche de couches potentiellement problématiques :")
found = False
for layer in model.layers:
    if "normalization" in layer.name.lower() or "batchnorm" in layer.name.lower():
        print(f"⚠️  Couche détectée : {layer.name} ({layer.__class__.__name__})")
        found = True

if not found:
    print("✅ Aucune couche de normalisation explicite détectée.")

# (Optionnel) Sauvegarde la structure du modèle pour inspection JSON
with open("model_structure.json", "w") as f:
    json.dump(model.to_json(), f)
    print("💾 Structure JSON du modèle enregistrée dans 'model_structure.json'")
