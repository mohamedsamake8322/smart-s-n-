import os
import json
from glob import glob

# Chemins
ROOT = r"C:\plateforme-agricole-complete-v2\plantdataset"
JSON_MALADIES = r"C:\plateforme-agricole-complete-v2\plantdataset\mapping_fiches_maladies_multilingual.json"
JSON_CARENCE = r"C:\plateforme-agricole-complete-v2\plantdataset\deficiencies_multilingual.json"
JSON_STRESS = r"C:\plateforme-agricole-complete-v2\plantdataset\stress_multilingual.json"

# Charger les JSON
with open(JSON_MALADIES, "r", encoding="utf-8") as f1:
    maladies_data = json.load(f1)
with open(JSON_CARENCE, "r", encoding="utf-8") as f2:
    carences_data = json.load(f2)["deficiencies"]
with open(JSON_STRESS, "r", encoding="utf-8") as f3:
    stress_data = json.load(f3)["abiotic_stress"]

# Fusion des références
merged = {**maladies_data, **carences_data, **stress_data}

# Générer le dataset
output = []
for split in ["train", "val"]:
    split_path = os.path.join(ROOT, split)
    for category in os.listdir(split_path):
        cat_path = os.path.join(split_path, category)
        if os.path.isdir(cat_path):
            description_block = merged.get(category)
            if description_block and "translations" in description_block:
                images = glob(f"{cat_path}/*.*")
                for img in images:
                    output.append({
                        "split": split,
                        "image_path": img,
                        "label": category,
                        "descriptions": description_block["translations"]
                    })

# Sauvegarde
with open(r"C:\plateforme-agricole-complete-v2\dataset_v2l.json", "w", encoding="utf-8") as f_out:
    json.dump(output, f_out, indent=2, ensure_ascii=False)
