# 🧠 Script : generer_mapping_renommage.py
import os
import json

# 📁 À adapter selon ton chemin réel
dataset_dir = r"C:\Downloads\plantdataset\plantvillage dataset"

# 🔍 Exploration récursive
def collect_raw_labels(root_dir):
    labels = set()
    for dirpath, _, files in os.walk(root_dir):
        if any(f.lower().endswith(('.jpg', '.jpeg', '.png')) for f in files):
            labels.add(os.path.basename(dirpath))
    return sorted(labels)

# 🛠️ Suppression des suffixes numériques, underscores en espaces, nettoyage
def nettoyer_nom(label):
    clean = label.lower()
    for prefix in ["train_set", "test_set"]:
        if clean.startswith(prefix):
            clean = clean.replace(prefix, "")
    clean = ''.join([c for c in clean if not c.isdigit()])
    clean = clean.replace("_", " ").replace("  ", " ").strip()
    return clean

# 🚧 Génération d’un mapping brut
labels = collect_raw_labels(dataset_dir)
mapping = {}
for raw_label in labels:
    clean_label = nettoyer_nom(raw_label)
    mapping[raw_label] = clean_label

# 💾 Export
with open("mapping_renommage_labels.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"✅ Mapping de renommage généré pour {len(mapping)} labels dans 'mapping_renommage_labels.json'")
