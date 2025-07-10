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

# 🔄 Création des maps normalisées → clés originales
en_key_map = {normalize(k): k for k in data_en}
fr_key_map = {normalize(k): k for k in data_fr}

# 📂 Extraction des classes du dataset (train + val)
def extract_classes(folder_path):
    classes = set()
    for subdir in ["train", "val"]:
        full_path = os.path.join(folder_path, subdir)
        if os.path.exists(full_path):
            classes.update(os.listdir(full_path))
    return [normalize(cls) for cls in classes]

# 🔁 Matching intelligent avec fusion EN/FR
def build_mapping(dataset_classes, en_key_map, fr_key_map, threshold=85):
    en_keys = list(en_key_map.keys())
    fr_keys = list(fr_key_map.keys())

    mapping = {}
    unmatched = []
    used_en_keys = set()

    for cls in dataset_classes:
        match, score, en_key_norm = process.extractOne(cls, en_keys, scorer=fuzz.ratio)
        if score >= threshold:
            en_key = en_key_map.get(en_key_norm)
            en_data = data_en.get(en_key)

            mapping[cls] = {
                "match_key_en": en_key,
                "data_en": en_data,
                "data_fr": None
            }
            used_en_keys.add(en_key_norm)

            # 🔍 Matching FR basé sur la clé EN trouvée
            fr_match, fr_score, fr_key_norm = process.extractOne(en_key_norm, fr_keys, scorer=fuzz.ratio)
            if fr_score >= threshold:
                fr_key = fr_key_map.get(fr_key_norm)
                mapping[cls]["data_fr"] = data_fr.get(fr_key)
        else:
            unmatched.append(cls)

    extra_en = [en_key_map[k] for k in en_keys if k not in used_en_keys]

    return mapping, unmatched, extra_en

# 📊 Exécution
folder = r"C:\plateforme-agricole-complete-v2\plantdataset"
dataset_classes = extract_classes(folder)
mapping, not_found, extra_keys = build_mapping(dataset_classes, en_key_map, fr_key_map)

# 🔍 Résumé des résultats
print(f"✅ Classes associées : {len(mapping)}")
print(f"❌ Classes non trouvées dans le JSON : {len(not_found)}")
for cls in not_found:
    print(" -", cls)

print(f"📦 Clés EN non associées : {len(extra_keys)}")
for key in extra_keys:
    print(" -", key)

# 💾 Sauvegarde dans un fichier JSON final
with open("dataset_mapping_bilingue.json", "w", encoding="utf-8") as f_out:
    json.dump(mapping, f_out, ensure_ascii=False, indent=2)
