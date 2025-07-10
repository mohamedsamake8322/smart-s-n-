import os
import json
from rapidfuzz import process, fuzz

# 🔍 Chargement du JSON
with open("EN_mapping_fiches_maladies.json", encoding="utf-8") as f:
    data = json.load(f)

# 🔧 Nettoyage et normalisation
def normalize(name):
    name = name.lower().replace("_", " ").replace("-", " ").replace(",", "").strip()
    return " ".join(name.split())  # Remove extra spaces

# 📂 Extraction des noms de classe du dataset
def extract_classes(folder_path):
    classes = set()
    for subdir in ["train", "val"]:
        full_path = os.path.join(folder_path, subdir)
        if os.path.exists(full_path):
            classes.update(os.listdir(full_path))
    return [normalize(cls) for cls in classes]

# 🔁 Matching intelligent
def build_mapping(dataset_classes, json_keys, threshold=85):
    mapping = {}
    unmatched = []
    extra_json = []

    for cls in dataset_classes:
        match, score, key = process.extractOne(cls, json_keys, scorer=fuzz.ratio)
        if score >= threshold:
            mapping[cls] = key
        else:
            unmatched.append(cls)

    # Clés JSON non utilisées
    used_keys = set(mapping.values())
    extra_json = [key for key in json_keys if key not in used_keys]

    return mapping, unmatched, extra_json

# 🔬 Exécution
folder = r"C:\plateforme-agricole-complete-v2\plantdataset"
dataset_classes = extract_classes(folder)
json_keys = [normalize(k) for k in data.keys()]
mapping, not_found, extra_keys = build_mapping(dataset_classes, json_keys)

# 📊 Résultats
print(f"✅ Correspondances trouvées : {len(mapping)}")
print(f"❌ Classes non trouvées dans le JSON : {len(not_found)}")
for cls in not_found:
    print(" -", cls)

print(f"📦 Clés en trop dans le JSON : {len(extra_keys)}")
for key in extra_keys:
    print(" -", key)
