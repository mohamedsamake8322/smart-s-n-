import os
import json

# Chemins
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subsets = ["train", "val"]

# Charger le fichier de mapping
with open("class_mapping_suggestions.json", "r", encoding="utf-8") as f:
    raw_mapping = json.load(f)

# Nettoyage des clés pour ignorer la casse
mapping = {k.lower().strip(): v.strip() for k, v in raw_mapping.items() if v}

log = []

for subset in subsets:
    subset_path = os.path.join(dataset_path, subset)
    for dirname in os.listdir(subset_path):
        dir_path = os.path.join(subset_path, dirname)
        if os.path.isdir(dir_path):
            name_key = dirname.lower().strip()
            new_name = mapping.get(name_key)

            if new_name and new_name != dirname:
                new_path = os.path.join(subset_path, new_name)
                if not os.path.exists(new_path):
                    os.rename(dir_path, new_path)
                    log.append(f"✅ {subset}: {dirname} → {new_name}")
                else:
                    log.append(f"⚠️ {subset}: {new_name} existe déjà, renommage ignoré")
            elif not new_name:
                log.append(f"❌ {subset}: {dirname} non trouvé dans le mapping")

# Sauvegarde du log
with open("renaming_log.txt", "w", encoding="utf-8") as f:
    for entry in log:
        f.write(entry + "\n")

print("📦 Renommage terminé. Voir renaming_log.txt pour le rapport.")
