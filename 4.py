import os
import json

# Charger le mapping
with open("class_mapping_suggestions.json", "r", encoding="utf-8") as f:
    mapping = json.load(f)

base_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subsets = ["train", "val"]

for subset in subsets:
    folder = os.path.join(base_path, subset)
    for dirname in os.listdir(folder):
        src = os.path.join(folder, dirname)
        if os.path.isdir(src):
            key = dirname.lower().strip()
            new_name = mapping.get(key)
            if new_name and new_name != dirname:
                dst = os.path.join(folder, new_name)
                os.rename(src, dst)
                print(f"✅ Renommé : {dirname} → {new_name}")
