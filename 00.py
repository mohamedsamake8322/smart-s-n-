import os
import json
from rapidfuzz import process, fuzz

# Paths
base_path = r'C:\plateforme-agricole-complete-v2\plantdataset'
json_en_path = os.path.join(base_path, 'EN_mapping_fiches_maladies.json')
json_fr_path = os.path.join(base_path, 'mapping_fiches_maladies_fr.json')

# Load JSON files
with open(json_en_path, encoding='utf-8') as f_en:
    en_mapping = json.load(f_en)

with open(json_fr_path, encoding='utf-8') as f_fr:
    fr_mapping = json.load(f_fr)

# Normalize utility
def normalize(name):
    return name.strip().lower().replace('_', ' ').replace('  ', ' ')

# Collect folder names
def get_disease_folders(base_path):
    folders = []
    for subset in ['train', 'val']:
        subset_path = os.path.join(base_path, subset)
        if os.path.exists(subset_path):
            folders += [folder for folder in os.listdir(subset_path)
                        if os.path.isdir(os.path.join(subset_path, folder))]
    return list(set(folders))  # deduplicate

disease_folders = get_disease_folders(base_path)
en_keys = list(en_mapping.keys())
fr_keys = list(fr_mapping.keys())
combined_keys = list(set(en_keys) & set(fr_keys))

# Prepare report
report = {}

for folder in disease_folders:
    orig_name = folder
    norm_name = normalize(folder)

    matched = False
    for key in combined_keys:
        if normalize(key) == norm_name:
            report[orig_name] = {"status": "defined", "matched_name": key}
            matched = True
            break

    if not matched:
        # Try fuzzy match on English keys
        best_match_en = process.extractOne(norm_name, en_keys, scorer=fuzz.token_sort_ratio)
        best_match_fr = process.extractOne(norm_name, fr_keys, scorer=fuzz.token_sort_ratio)

        report[orig_name] = {
            "status": "undefined",
            "suggestion_from_EN": {
                "match": best_match_en[0],
                "score": best_match_en[1]
            },
            "suggestion_from_FR": {
                "match": best_match_fr[0],
                "score": best_match_fr[1]
            }
        }

# Save report
report_path = os.path.join(base_path, 'maladie_matching_report.json')
with open(report_path, 'w', encoding='utf-8') as f_out:
    json.dump(report, f_out, indent=4, ensure_ascii=False)

print(f"✅ Rapport généré avec succès : {report_path}")
