import os
import json
import shutil

# Chemin du dataset
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subsets = ["train", "val"]

# Chargement du mapping
mapping_path = os.path.join("C:\\plateforme-agricole-complete-v2", "class_mapping_suggestions.json")
with open(mapping_path, "r", encoding="utf-8") as f:

    mapping = json.load(f)

log = []

for subset in subsets:
    folder_path = os.path.join(dataset_path, subset)
    for dirname in os.listdir(folder_path):
        src = os.path.join(folder_path, dirname)
        if os.path.isdir(src):
            key = dirname.lower().strip()
            new_name = mapping.get(key)

            if new_name and new_name != dirname:
                dst = os.path.join(folder_path, new_name)

                if not os.path.exists(dst):
                    os.rename(src, dst)
                    log.append(f"✅ {subset}: {dirname} → {new_name}")
                else:
                    # Fusion : déplacer les fichiers de src vers dst
                    for filename in os.listdir(src):
                        src_file = os.path.join(src, filename)
                        dst_file = os.path.join(dst, filename)

                        # Évite d'écraser des fichiers identiques
                        if not os.path.exists(dst_file):
                            shutil.move(src_file, dst)
                        else:
                            log.append(f"⚠️ {subset}: fichier déjà présent {filename} ignoré")

                    # Supprime le dossier source une fois vidé
                    if not os.listdir(src):
                        os.rmdir(src)
                        log.append(f"🔀 {subset}: fusion et suppression du dossier {dirname}")
                    else:
                        log.append(f"⚠️ {subset}: dossier {dirname} non vide après fusion")

# Sauvegarde du log
with open("rename_merge_log.txt", "w", encoding="utf-8") as f:
    for entry in log:
        f.write(entry + "\n")

print("✅ Fusion terminée. Rapport enregistré dans 'rename_merge_log.txt'")
