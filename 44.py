import os
import shutil
import hashlib
import json

def file_hash(path, block_size=65536):
    """Calcule le hash MD5 du fichier"""
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            hash_md5.update(block)
    return hash_md5.hexdigest()

# Chemins
base_path = "C:/plateforme-agricole-complete-v2/plantdataset"
mapping_path = os.path.join(base_path, "custom_mapping.json")
sets = ["train", "val"]

# Charger le mapping
with open(mapping_path, encoding="utf-8") as f:
    mapping = json.load(f)

report = {}

for subset in sets:
    subset_path = os.path.join(base_path, subset)

    for old_name, new_name in mapping.items():
        if old_name == new_name:
            continue

        old_path = os.path.join(subset_path, old_name)
        new_path = os.path.join(subset_path, new_name)

        if not os.path.exists(old_path) or not os.path.exists(new_path):
            continue

        for fname in os.listdir(old_path):
            source_file = os.path.join(old_path, fname)
            target_file = os.path.join(new_path, fname)

            if not os.path.isfile(source_file):
                continue

            if os.path.exists(target_file):
                if file_hash(source_file) == file_hash(target_file):
                    # Exact duplicate
                    action = "skipped (duplicate)"
                else:
                    # Fichier différent → renommer
                    base, ext = os.path.splitext(fname)
                    new_fname = f"{base}_alt{ext}"
                    target_file = os.path.join(new_path, new_fname)
                    shutil.move(source_file, target_file)
                    action = f"renamed to {new_fname}"
            else:
                shutil.move(source_file, target_file)
                action = "moved"

            report.setdefault(old_name, []).append({
                "file": fname,
                "action": action,
                "destination": new_name
            })

        # Supprimer le dossier source s’il est vide
        if not os.listdir(old_path):
            os.rmdir(old_path)
            report.setdefault(old_name, []).append({
                "action": "source folder removed"
            })

# Sauvegarde du rapport
report_path = os.path.join(base_path, "fusion_report.json")
with open(report_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=4, ensure_ascii=False)

print(f"✅ Rapport de fusion enregistré : {report_path}")
