import os
import shutil

base_path = "C:/plateforme-agricole-complete-v2/plantdataset"
sets = ["train", "val"]
mapping_path = os.path.join(base_path, "custom_mapping.json")

# Charger le mapping
with open(mapping_path, encoding="utf-8") as f:
    mapping = json.load(f)

for subset in sets:
    subset_path = os.path.join(base_path, subset)
    for old_name, new_name in mapping.items():
        if old_name == new_name:
            continue

        old_path = os.path.join(subset_path, old_name)
        new_path = os.path.join(subset_path, new_name)

        if os.path.exists(old_path) and os.path.exists(new_path):
            # Fusion des fichiers
            for file_name in os.listdir(old_path):
                source_file = os.path.join(old_path, file_name)
                target_file = os.path.join(new_path, file_name)

                # Évite les doublons de noms
                if not os.path.exists(target_file):
                    shutil.move(source_file, new_path)
                else:
                    print(f"⚠️ Fichier déjà présent : {target_file}")

            # Supprime l'ancien dossier s'il est vide
            if not os.listdir(old_path):
                os.rmdir(old_path)
                print(f"✅ Fusion terminée et {old_name} supprimé.")
            else:
                print(f"⚠️ Dossier {old_name} non vide après fusion.")
