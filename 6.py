import os
import json

def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")

# Chemins
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subsets = ["train", "val"]

# Charger les deux fichiers JSON
with open(os.path.join(dataset_path, "EN_mapping_fiches_maladies.json"), "r", encoding="utf-8") as f:
    en_data = json.load(f)
with open(os.path.join(dataset_path, "mapping_fiches_maladies_fr.json"), "r", encoding="utf-8") as f:
    fr_data = json.load(f)

en_keys = set(normalize(k) for k in en_data.keys())
fr_keys = set(normalize(k) for k in fr_data.keys())

# Vérification des dossiers
missing = []

for subset in subsets:
    folder = os.path.join(dataset_path, subset)
    for dirname in os.listdir(folder):
        full_path = os.path.join(folder, dirname)
        if os.path.isdir(full_path):
            name = normalize(dirname)
            if name not in en_keys and name not in fr_keys:
                missing.append((subset, dirname))

# Résultat
if missing:
    print(f"❌ {len(missing)} dossiers sans correspondance dans les JSON :")
    for subset, name in missing:
        print(f" - {subset}/{name}")
else:
    print("✅ Tous les dossiers ont une correspondance dans au moins un fichier JSON.")
