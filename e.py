# 🐍 Script : renommer_dossiers_dataset.py
import os
import json
import shutil

# 📁 À adapter à ton chemin réel
dataset_root = r"C:\Downloads\plantdataset\plantvillage dataset"
mapping_path = "mapping_renommage_labels.json"

# 🔁 Charger le mapping
with open(mapping_path, encoding="utf-8") as f:
    label_map = json.load(f)

# 🔍 Appliquer le renommage
renommés = 0
for dirpath, dirnames, _ in os.walk(dataset_root, topdown=False):
    for dirname in dirnames:
        old_path = os.path.join(dirpath, dirname)
        if dirname in label_map:
            new_name = label_map[dirname]
            if new_name != dirname:
                new_path = os.path.join(dirpath, new_name)
                if not os.path.exists(new_path):
                    try:
                        shutil.move(old_path, new_path)
                        renommés += 1
                        print(f"✅ {dirname} → {new_name}")
                    except Exception as e:
                        print(f"⚠️ Erreur sur {dirname} : {e}")
                else:
                    print(f"⚠️ Conflit : le dossier '{new_name}' existe déjà")

print(f"\n🎯 Renommage terminé : {renommés} dossiers renommés")
