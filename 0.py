from rapidfuzz import process, fuzz
import os
import json

ROOT = r"C:\plateforme-agricole-complete-v2\plantdataset"
JSON_PATH = r"C:\plateforme-agricole-complete-v2\plantdataset\EN_mapping_fiches_maladies.json"

def normalize(name):
    return " ".join(name.lower().replace("_", " ").replace("-", " ").replace(",", "").split())

# Charger les maladies
with open(JSON_PATH, "r", encoding="utf-8") as f_json:
    data = json.load(f_json)
json_keys = [normalize(k) for k in data.keys()]

report = []

# Parcours des dossiers
for split in ["train", "val"]:
    split_path = os.path.join(ROOT, split)
    for folder in os.listdir(split_path):
        folder_path = os.path.join(split_path, folder)
        if not os.path.isdir(folder_path):
            continue

        norm_folder = normalize(folder)
        result = process.extractOne(norm_folder, json_keys, scorer=fuzz.ratio)
        if result:
            match, score, matched_key = result
            report.append({
                "folder": folder,
                "matched_key": matched_key,
                "score": score
            })

# Export du rapport
with open("correspondance_dossiers.json", "w", encoding="utf-8") as f_out:
    json.dump(report, f_out, indent=2, ensure_ascii=False)

print("✅ Rapport généré dans 'correspondance_dossiers.json'")
