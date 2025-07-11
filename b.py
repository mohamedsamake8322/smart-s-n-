import os
import json
from rapidfuzz import process, fuzz

# Paths
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
json_fr_path = os.path.join(base_path, "mapping_fiches_maladies_fr.json")
custom_map_path = os.path.join(base_path, "custom_mapping.json")

# Load data
with open(json_en_path, encoding='utf-8') as f_en:
    en_data = json.load(f_en)
with open(json_fr_path, encoding='utf-8') as f_fr:
    fr_data = json.load(f_fr)
with open(custom_map_path, encoding='utf-8') as f_map:
    custom_map = json.load(f_map)

# Normalize keys
def normalize(s):
    return s.lower().strip().replace('_', ' ').replace('  ', ' ')

json_keys = list(set(list(en_data.keys()) + list(fr_data.keys())))
json_keys_normalized = {normalize(k): k for k in json_keys}

# Get all folders from train/val
def get_disease_folders(path):
    folders = []
    for split in ['train', 'val']:
        split_path = os.path.join(path, split)
        if os.path.exists(split_path):
            folders += [folder for folder in os.listdir(split_path)
                        if os.path.isdir(os.path.join(split_path, folder))]
    return list(set(folders))

# Match logic
matched, unmatched = {}, {}
folders = get_disease_folders(base_path)
THRESHOLD = 85

for folder in folders:
    name_norm = normalize(folder)

    # Priorité au mapping manuel
    if folder in custom_map:
        matched[folder] = {"type": "manual", "match": custom_map[folder]}
        continue

    # Recherche floue dans les JSON
    best_match = process.extractOne(name_norm, json_keys, scorer=fuzz.token_sort_ratio)
    if best_match and best_match[1] >= THRESHOLD:
        matched[folder] = {"type": "fuzzy", "match": best_match[0], "score": best_match[1]}
    else:
        unmatched[folder] = {"normalized": name_norm, "suggestion": best_match[0] if best_match else None, "score": best_match[1] if best_match else None}

# Résultats
print("✅ Correspondances reconnues :")
for name, info in matched.items():
    print(f" - {name} → {info['match']} ({info['type']})")

print("\n⚠️ Non reconnues ou ambiguës :")
for name, info in unmatched.items():
    print(f" - {name} ❌ (suggestion : {info['suggestion']} score {info['score']})")
