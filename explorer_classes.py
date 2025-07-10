import os
import json
from glob import glob

ROOT = r"C:\plateforme-agricole-complete-v2\plantdataset"
OUTPUT_STATS = r"C:\plateforme-agricole-complete-v2\stats_classes.json"

# Charger le JSON fusionné
with open(r"C:\plateforme-agricole-complete-v2\dataset_v2l_mapped.json", "r", encoding="utf-8") as f:
    mapped = json.load(f)

mapped_classes = set(entry["label"] for entry in mapped)

# Charger les classes du JSON multilingue
with open(r"C:\plateforme-agricole-complete-v2\plantdataset\mapping_fiches_maladies_fr.json", "r", encoding="utf-8") as f_maladies:
    json_data = json.load(f_maladies)

with open(r"C:\plateforme-agricole-complete-v2\plantdataset\deficiencies_multilingual.json", "r", encoding="utf-8") as f_carences:
    json_carences = json.load(f_carences)["deficiencies"]

with open(r"C:\plateforme-agricole-complete-v2\plantdataset\stress_multilingual.json", "r", encoding="utf-8") as f_stress:
    json_stress = json.load(f_stress)["abiotic_stress"]

merged_keys = set(json_data.keys()) | set(json_carences.keys()) | set(json_stress.keys())

# Explorer les classes
stats = {}
for split in ["train", "val"]:
    split_path = os.path.join(ROOT, split)
    for class_name in os.listdir(split_path):
        class_path = os.path.join(split_path, class_name)
        if os.path.isdir(class_path):
            n_images = len(glob(f"{class_path}/*.*"))
            stats[class_name] = {
                "split": split,
                "num_images": n_images,
                "in_multilingual_json": class_name in merged_keys,
                "already_mapped": class_name in mapped_classes
            }

# Sauvegarde
with open(OUTPUT_STATS, "w", encoding="utf-8") as f_out:
    json.dump(stats, f_out, indent=2, ensure_ascii=False)

print(f"✅ Rapport généré : {len(stats)} classes analysées. Fichier : stats_classes.json")
