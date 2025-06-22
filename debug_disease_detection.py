from PIL import Image
import json
from utils.disease_detector import DiseaseDetector
from utils.config_model import load_labels

# 🔍 Charger le modèle
detector = DiseaseDetector(model_path="model/efficientnet_agro_final.keras")

# 🧠 Charger la base JSON
with open("data/all_diseases_translated.json", encoding="utf-8") as f:
    disease_descriptions = json.load(f)

# 🔁 Mapper les noms (si nécessaire)
disease_name_map = {
    "Late Blight": "Bright",
    "Early Blight": "Early Blightt",
    "Phomopsis Blight": "Phomopsis Blightt",
    "Cercospora Leaf Spot (Frogeye)": "Cercle Leaf Spot (Frogeye)",
    "Tomato Russet Mite": "Russet Tomato Mite",
    "Root-Knot Nematodes": "Root-knot nematodes",
    "Corn Earworm / Tomato Fruitworm": "Corn Earworm / Tomato FruitWorm",
    "Potato Leafhopper": "Potato leafhopper",
    "Beet Leafhopper": "Beet leafhopper",
    "Healthy": "Healthy plant"
    # … continue si besoin
}

# 🖼️ Charger une image de test (remplace par une image de ton jeu de validation)
image = Image.open(r"C:\plateforme-agricole-complete-v2\plant_disease_dataset\train\BACTERIAL CANKER\bacterial-canker6x2400-rjnalg.jpg").convert("RGB")

# 🧠 Prédictions
results = detector.predict(image, confidence_threshold=0.1)

print("\n📌 Résultats du modèle :")
for r in results:
    model_name = r["disease"]
    json_name = disease_name_map.get(model_name, model_name)

    matched = any(d.get("name", "").strip().lower() == json_name.strip().lower() for d in disease_descriptions)
    print(f" - 📷 {model_name} → JSON : {'✔️ OUI' if matched else '❌ NON'} — confiance {r['confidence']:.1f}%")
