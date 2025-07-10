import os
import json
from glob import glob
from multiprocessing import Pool, cpu_count, freeze_support
import tqdm
from rapidfuzz import process, fuzz

# 📁 Chemins principaux
ROOT = r"C:\plateforme-agricole-complete-v2\plantdataset"
SAVE_PATH = r"C:\plateforme-agricole-complete-v2\dataset_v2l_mapped.json"

json_paths = {
    "en": r"C:\plateforme-agricole-complete-v2\plantdataset\EN_mapping_fiches_maladies.json",
    "fr": r"C:\plateforme-agricole-complete-v2\plantdataset\mapping_fiches_maladies_fr.json"
}

REQUIRED_FIELDS = [
    "culture",
    "Agent causal",
    "description",
    "symptoms",
    "evolution",
    "Name of active product material",
    "treatment"
]

def normalize(name):
    return " ".join(name.lower().replace("_", " ").replace("-", " ").replace(",", "").split())

def is_valid_entry(entry):
    return all(field in entry for field in REQUIRED_FIELDS)

def load_jsons():
    with open(json_paths["en"], "r", encoding="utf-8") as f_en:
        raw_en = json.load(f_en)
    with open(json_paths["fr"], "r", encoding="utf-8") as f_fr:
        raw_fr = json.load(f_fr)

    en_data = {normalize(k): (k, raw_en[k]) for k in raw_en if isinstance(k, str) and is_valid_entry(raw_en[k])}
    fr_data = {normalize(k): (k, raw_fr[k]) for k in raw_fr if isinstance(k, str) and is_valid_entry(raw_fr[k])}
    return en_data, fr_data

maladies_en, maladies_fr = load_jsons()
valid_keys_en = list(maladies_en.keys())
ignored_classes = []

def process_class(category_path, split, threshold=65):
    output = []
    folder_name = os.path.basename(category_path)
    normalized_folder = normalize(folder_name)

    result = process.extractOne(normalized_folder, valid_keys_en, scorer=fuzz.ratio)
    if not result:
        ignored_classes.append(folder_name)
        return []

    _, score, matched_key = result
    if score < threshold or matched_key not in maladies_en:
        ignored_classes.append(folder_name)
        return []

    en_key, en_data = maladies_en[matched_key]
    fr_data = maladies_fr.get(matched_key, (None, None))[1]

    block = {
        "en": en_data,
        "fr": fr_data
    }

    # 🔎 Détection des images avec extensions classiques
    allowed_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".JPG", ".JPEG", ".PNG"}
    images = [
    os.path.join(category_path, f)
    for f in os.listdir(category_path)
    if os.path.isfile(os.path.join(category_path, f)) and os.path.splitext(f)[1] in allowed_exts
]


    for img_path in images:
        output.append({
            "split": split,
            "image_path": img_path,
            "label": en_key,
            "descriptions": block
        })
    return output

def process_class_wrapper(args):
    return process_class(*args)

if __name__ == "__main__":
    freeze_support()

    # 🧹 Réinitialisation du mapping précédent
    if os.path.exists(SAVE_PATH):
        os.remove(SAVE_PATH)
        print(f"🗑️ Fichier supprimé : {SAVE_PATH}")
    else:
        print(f"⚠️ Aucun fichier précédent trouvé : {SAVE_PATH}")

    # 📦 Construction des tâches
    tasks = []
    for split in ["train", "val"]:
        split_path = os.path.join(ROOT, split)
        for category in os.listdir(split_path):
            cat_path = os.path.join(split_path, category)
            if os.path.isdir(cat_path):
                tasks.append((cat_path, split))

    print(f"🚀 Traitement de {len(tasks)} classes avec {cpu_count()} processus...")

    # 🧠 Traitement parallèle
    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.imap(process_class_wrapper, tasks), total=len(tasks)))

    # 🔄 Fusion des résultats
    all_data = [item for sublist in results for item in sublist]

    # 💾 Sauvegarde finale
    with open(SAVE_PATH, "w", encoding="utf-8") as f_out:
        json.dump(all_data, f_out, indent=2, ensure_ascii=False)

    with open("ignored_classes.json", "w", encoding="utf-8") as f_ignored:
        json.dump(ignored_classes, f_ignored, indent=2, ensure_ascii=False)

    print(f"\n✅ Mapping terminé. Total d'images traitées : {len(all_data)}")
    print(f"📁 Dossiers ignorés enregistrés dans 'ignored_classes.json' ({len(ignored_classes)} dossiers)")
