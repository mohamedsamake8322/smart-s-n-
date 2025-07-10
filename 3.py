import os
import json
from rapidfuzz import process, fuzz

def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")

# Chemin vers le dossier contenant les sous-dossiers de classes
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subfolders = ["train", "val"]

# Étape 1 : Extraction des noms de classe
class_names = set()
for subset in subfolders:
    path = os.path.join(dataset_path, subset)
    if os.path.isdir(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                class_names.add(normalize(entry))

print(f"🎯 Noms de classes extraits : {len(class_names)}")

# Étape 2 : Charger les deux fichiers JSON
json_files = ["EN_mapping_fiches_maladies.json", "mapping_fiches_maladies_fr.json"]
json_keys = {}

for jf in json_files:
    with open(os.path.join(dataset_path, jf), "r", encoding="utf-8") as f:
        data = json.load(f)
        keys = [normalize(k) for k in data.keys()]
        json_keys[jf] = keys

# Étape 3 : Générer les suggestions de correspondance
mapping_suggestions = {}

for class_name in class_names:
    best_en, score_en, _ = process.extractOne(class_name, json_keys["EN_mapping_fiches_maladies.json"], scorer=fuzz.token_sort_ratio)
    best_fr, score_fr, _ = process.extractOne(class_name, json_keys["mapping_fiches_maladies_fr.json"], scorer=fuzz.token_sort_ratio)

    best_match = None
    if score_en >= score_fr and score_en >= 85:
        best_match = best_en
    elif score_fr > score_en and score_fr >= 85:
        best_match = best_fr

    if best_match:
        mapping_suggestions[class_name] = best_match
    else:
        mapping_suggestions[class_name] = None

# Étape 4 : Sauvegarde du mapping proposé
with open("class_mapping_suggestions.json", "w", encoding="utf-8") as f:
    json.dump(mapping_suggestions, f, indent=2, ensure_ascii=False)

print("\n✅ Mapping intelligent sauvegardé dans 'class_mapping_suggestions.json'")
