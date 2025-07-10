import os
import json
from glob import glob
from multiprocessing import Pool, cpu_count, freeze_support
import tqdm
from rapidfuzz import process, fuzz

# Chemins
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
        maladies_en_raw = json.load(f_en)
    with open(json_paths["fr"], "r", encoding="utf-8") as f_fr:
        maladies_fr_raw = json.load(f_fr)

    # Construction de mapping avec clés normalisées
    maladies_en = {normalize(k): (k, maladies_en_raw[k]) for k in maladies_en_raw if is_valid_entry(maladies_en_raw[k])}
    maladies_fr = {normalize(k): (k, maladies_fr_raw[k]) for k in maladies_fr_raw if is_valid_entry(maladies_fr_raw[k])}
    return maladies_en, maladies_fr

maladies_en, maladies_fr = load_jsons()
valid_keys_en = list(maladies_en.keys())

# Reprise si mapping existant
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        already_mapped = json.load(f)
        mapped_images = set(x["image_path"] for x in already_mapped)
        print(f"🔄 Reprise à partir de {len(mapped_images)} images déjà traitées.")
else:
    already_mapped = []
    mapped_images = set()

def process_class(category_path, split):
    output = []
    folder_name = os.path.basename(category_path)
    normalized_folder = normalize(folder_name)

    # Matching flou avec les clés EN
    match, score, matched_key = process.extractOne(normalized_folder, valid_keys_en, scorer=fuzz.ratio)
    if score < 85:
        return []  # Classe ignorée si pas de correspondance suffisante

    en_key, en_data = maladies_en[matched_key]
    fr_data = maladies_fr.get(matched_key, (None, None))[1]

    block = {
        "en": en_data,
        "fr": fr_data
    }

    # Attribution aux images du dossier
    images = glob(os.path.join(category_path, "*.*"))
    for img_path in images:
        if img_path not in mapped_images:
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
    tasks = []
    for split in ["train", "val"]:
        split_path = os.path.join(ROOT, split)
        for category in os.listdir(split_path):
            cat_path = os.path.join(split_path, category)
            if os.path.isdir(cat_path):
                tasks.append((cat_path, split))

    print(f"🚀 Traitement de {len(tasks)} classes avec {cpu_count()} processus...")

    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.imap(process_class_wrapper, tasks), total=len(tasks)))

    all_data = already_mapped + [item for sublist in results for item in sublist]

    with open(SAVE_PATH, "w", encoding="utf-8") as f_out:
        json.dump(all_data, f_out, indent=2, ensure_ascii=False)

    print(f"\n✅ Mapping terminé. Total d'images traitées : {len(all_data)}")
