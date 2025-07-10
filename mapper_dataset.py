import os
import json
from glob import glob
from multiprocessing import Pool, cpu_count, freeze_support
import tqdm

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

def is_valid_entry(entry):
    return all(field in entry for field in REQUIRED_FIELDS)

def load_jsons():
    with open(json_paths["en"], "r", encoding="utf-8") as f_en:
        maladies_en = json.load(f_en)
    with open(json_paths["fr"], "r", encoding="utf-8") as f_fr:
        maladies_fr = json.load(f_fr)

    merged = {}
    for disease_name in maladies_en:
        if disease_name in maladies_fr:
            en_entry = maladies_en[disease_name]
            fr_entry = maladies_fr[disease_name]
            if is_valid_entry(en_entry) and is_valid_entry(fr_entry):
                merged[disease_name] = {
                    "translations": {
                        "en": en_entry,
                        "fr": fr_entry
                    }
                }
    return merged

merged_data = load_jsons()
valid_classes = set(merged_data.keys())

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
    category_name = os.path.basename(category_path)
    if category_name not in valid_classes:
        return []
    description_block = merged_data[category_name]["translations"]
    images = glob(f"{category_path}/*.*")
    for img in images:
        if img not in mapped_images:
            output.append({
                "split": split,
                "image_path": img,
                "label": category_name,
                "descriptions": description_block
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
            if os.path.isdir(cat_path) and category in valid_classes:
                tasks.append((cat_path, split))

    print(f"🚀 Traitement de {len(tasks)} classes avec {cpu_count()} processus...")

    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.imap(process_class_wrapper, tasks), total=len(tasks)))

    all_data = already_mapped + [item for sublist in results for item in sublist]
    with open(SAVE_PATH, "w", encoding="utf-8") as f_out:
        json.dump(all_data, f_out, indent=2, ensure_ascii=False)

    print(f"\n✅ Mapping terminé. Total d'images traitées : {len(all_data)}")
