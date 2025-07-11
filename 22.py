import os
import json

# Chargement du mapping
with open("C:/plateforme-agricole-complete-v2/plantdataset/custom_mapping.json", encoding="utf-8") as f:
    mapping = json.load(f)

base_path = "C:/plateforme-agricole-complete-v2/plantdataset"
sets = ["train", "val"]

for subset in sets:
    subset_path = os.path.join(base_path, subset)
    if not os.path.exists(subset_path):
        continue

    for folder in os.listdir(subset_path):
        folder_path = os.path.join(subset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        # Vérification si le dossier est dans le mapping
        if folder in mapping and folder != mapping[folder]:
            new_name = mapping[folder]
            new_path = os.path.join(subset_path, new_name)

            # Renommer s'il n'y a pas déjà un dossier cible
            if not os.path.exists(new_path):
                os.rename(folder_path, new_path)
                print(f"✅ {folder} → {new_name}")
            else:
                print(f"⚠️ Le dossier {new_name} existe déjà. Fusion manuelle nécessaire.")
