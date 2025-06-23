# 🐍 Script : fusionner_dossiers_conflits.py
import os
import shutil
import json

# 📁 À adapter
dataset_root = r"C:\Downloads\plantdataset\plantvillage dataset"
mapping_path = "mapping_renommage_labels.json"

# 🔁 Charger le mapping de renommage
with open(mapping_path, encoding="utf-8") as f:
    label_map = json.load(f)

fusionnés = 0

# 🔍 Parcourir les labels avec conflits (labels où le dossier cible existe déjà)
for old_name, new_name in label_map.items():
    if old_name == new_name:
        continue

    source_path = os.path.join(dataset_root, old_name)
    target_path = os.path.join(dataset_root, new_name)

    if os.path.isdir(source_path) and os.path.isdir(target_path):
        # Fusionner les images
        for filename in os.listdir(source_path):
            src_file = os.path.join(source_path, filename)
            dest_file = os.path.join(target_path, filename)
            if not os.path.exists(dest_file):
                try:
                    shutil.move(src_file, dest_file)
                except Exception as e:
                    print(f"⚠️ Erreur sur {filename} : {e}")
        # Supprimer le dossier source s'il est vide
        if not os.listdir(source_path):
            os.rmdir(source_path)
        fusionnés += 1
        print(f"✅ Fusionné : {old_name} → {new_name}")

print(f"\n🎯 Fusion automatique terminée pour {fusionnés} dossiers conflictuels")
