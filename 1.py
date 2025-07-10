import os
import json
from rapidfuzz import process, fuzz

# 📁 Chargement des fichiers JSON
with open("EN_mapping_fiches_maladies.json", encoding="utf-8") as f_en:
    data_en = json.load(f_en)

with open("mapping_fiches_maladies_fr.json", encoding="utf-8") as f_fr:
    data_fr = json.load(f_fr)

# 🧼 Fonction de normalisation des noms
def normalize(name):
    name = name.lower().replace("_", " ").replace("-", " ").replace(",", "").strip()
    return " ".join(name.split())

# 📂 Extraction des classes du dataset (train + val)
def extract_classes(folder_path):
    classes = set()
    for subdir in ["train", "val"]:
        full_path = os.path.join(folder_path, subdir)
        if os.path.exists(full_path):
            classes.update(os.listdir(full_path))
    return [normalize(cls) for cls in classes]

# 🔁 Matching et fusion EN/FR
def build_mapping(dataset_classes, data_en, data_fr, threshold=85):
    en_keys = [normalize(k) for k in data_en.keys()]
    fr_keys = [normalize(k) for k in data_fr.keys()]
    mapping = {}
    unmatched = []
    used_en_keys = set()

    for cls in dataset_classes:
        match, score, en_key = process.extractOne(cls, en_keys, scorer=fuzz.ratio)
        if score >= threshold:
            mapping[cls] = {
                "match_key_en": en_key,
                "data_en": data_en[en_key],
                "data_fr": None
            }
            used_en_keys.add(en_key)

            # 🔍 Tentative d’association avec une clé FR
            fr_match, fr_score, fr_key = process.extractOne(en_key, fr_keys, scorer=fuzz.ratio)
            if fr_score >= threshold:
                mapping[cls]["data_fr"] = data_fr[fr_key]
        else:
            unmatched.append(cls)

    extra_en = [k for k in en_keys if k not in used_en_keys]

    return mapping, unmatched, extra_en

# 📊 Exécution
folder = r"C:\plateforme-agricole-complete-v2\plantdataset"
dataset_classes = extract_classes(folder)
mapping, not_found, extra_keys = build_mapping(dataset_classes, data_en, data_fr)

# 💡 Résumé des résultats
print(f"✅ Classes associées : {len(mapping)}")
print(f"❌ Classes non trouvées dans le JSON : {len(not_found)}")
for cls in not_found:
    print(" -", cls)

print(f"📦 Clés EN non associées : {len(extra_keys)}")
for key in extra_keys:
    print(" -", key)

# 💾 Optionnel : sauvegarde dans un fichier
with open("dataset_mapping_bilingue.json", "w", encoding="utf-8") as f_out:
    json.dump(mapping, f_out, ensure_ascii=False, indent=2)
