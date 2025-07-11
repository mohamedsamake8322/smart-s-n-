import os
import json

# Chemins de base
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
custom_mapping_path = os.path.join(base_path, "custom_mapping.json")
sets = ["train", "val"]

# Charger le mapping validé
with open(custom_mapping_path, encoding="utf-8") as f:
    mapping = json.load(f)

# Préparer le rapport de renommage
rename_report = {}

for split in sets:
    split_path = os.path.join(base_path, split)

    if not os.path.exists(split_path):
        continue

    for folder in os.listdir(split_path):
        folder_path = os.path.join(split_path, folder)
        if not os.path.isdir(folder_path):
            continue

        # Vérifie si le dossier est dans le mapping
        new_name = mapping.get(folder)
        if new_name and new_name != folder:
            new_path = os.path.join(split_path, new_name)

            if not os.path.exists(new_path):
                os.rename(folder_path, new_path)
                rename_report.setdefault(folder, []).append({
                    "split": split,
                    "renamed_to": new_name,
                    "status": "renamed"
                })
                print(f"✅ {split}: {folder} → {new_name}")
            else:
                rename_report.setdefault(folder, []).append({
                    "split": split,
                    "renamed_to": new_name,
                    "status": "target already exists"
                })
                print(f"⚠️ {split}: le dossier {new_name} existe déjà.")
