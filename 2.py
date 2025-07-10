import os
import json

def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")

# Dossier dataset
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subfolders = ["train", "val"]

# Extraction et nettoyage des noms de classes
class_names = set()
for subset in subfolders:
    path = os.path.join(dataset_path, subset)
    if os.path.isdir(path):
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                class_names.add(normalize(entry))

print(f"🎯 Total de classes extraites (nettoyées) : {len(class_names)}")

# Chargement des deux fichiers JSON
json_files = ["EN_mapping_fiches_maladies.json", "mapping_fiches_maladies_fr.json"]
json_keys = {}

for jf in json_files:
    with open(os.path.join(dataset_path, jf), "r", encoding="utf-8") as f:
        data = json.load(f)
        cleaned_keys = set(normalize(k) for k in data.keys())
        json_keys[jf] = cleaned_keys

# Comparaison pour chaque JSON
for jf, keys in json_keys.items():
    print(f"\n📂 Analyse pour {jf}")
    matches = class_names & keys
    missing_in_json = class_names - keys
    extra_in_json = keys - class_names

    print(f"✅ Correspondances : {len(matches)}")
    print(f"❌ Classes non trouvées dans le JSON : {len(missing_in_json)}")
    for item in sorted(missing_in_json):
        print(f" - {item}")

    print(f"📦 Clés en trop dans le JSON : {len(extra_in_json)}")
    for item in sorted(extra_in_json):
        print(f" - {item}")
