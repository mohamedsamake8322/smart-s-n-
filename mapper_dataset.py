import os
import json
from glob import glob
from multiprocessing import Pool, cpu_count, freeze_support
import tqdm

# Chemins
ROOT = r"C:\plateforme-agricole-complete-v2\plantdataset"
SAVE_PATH = r"C:\plateforme-agricole-complete-v2\dataset_v2l_mapped.json"

# JSONs fusionnés
json_paths = {
    "maladies": r"C:\plateforme-agricole-complete-v2\plantdataset\mapping_fiches_maladies_fr.json",
    # ← choisi parmi les deux disponibles
    "maladies": r"C:\plateforme-agricole-complete-v2\plantdataset\EN_mapping_fiches_maladies.json",
    "carences": r"C:\plateforme-agricole-complete-v2\plantdataset\deficiencies_multilingual.json",
    "stress": r"C:\plateforme-agricole-complete-v2\plantdataset\stress_multilingual.json"
}

def load_jsons():
    with open(json_paths["maladies"], "r", encoding="utf-8") as f1:
        maladies = json.load(f1)
    with open(json_paths["carences"], "r", encoding="utf-8") as f2:
        carences = json.load(f2)["deficiencies"]
    with open(json_paths["stress"], "r", encoding="utf-8") as f3:
        stress = json.load(f3)["abiotic_stress"]
    return {**maladies, **carences, **stress}

merged_data = load_jsons()
valid_classes = set(merged_data.keys())

# Fichier déjà mappé ?
if os.path.exists(SAVE_PATH):
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        already_mapped = json.load(f)
        mapped_images = set(x["image_path"] for x in already_mapped)
        print(f"🔄 Reprise à partir de {len(mapped_images)} images déjà traitées.")
else:
    already_mapped = []
    mapped_images = set()

# Traitement d’une classe
def process_class(category_path, split):
    output = []
    category_name = os.path.basename(category_path)
    if category_name not in valid_classes:
        return []
    description_block = merged_data[category_name]
    if not description_block.get("translations"):
        return []
    images = glob(f"{category_path}/*.*")
    for img in images:
        if img not in mapped_images:
            output.append({
                "split": split,
                "image_path": img,
                "label": category_name,
                "descriptions": description_block["translations"]
            })
    return output

def process_class_wrapper(args):
    return process_class(*args)

if __name__ == "__main__":
    freeze_support()
    # Créer la liste des tâches
    tasks = []
    for split in ["train", "val"]:
        split_path = os.path.join(ROOT, split)
        for category in os.listdir(split_path):
            cat_path = os.path.join(split_path, category)
            if os.path.isdir(cat_path) and category in valid_classes:
                tasks.append((cat_path, split))

    print(f"🚀 Traitement de {len(tasks)} classes avec {cpu_count()} processus...")

    # Lancer le pool de traitement
    with Pool(processes=cpu_count()) as pool:
        results = list(tqdm.tqdm(pool.imap(process_class_wrapper, tasks), total=len(tasks)))

    # Fusion et sauvegarde
    all_data = already_mapped + [item for sublist in results for item in sublist]
    with open(SAVE_PATH, "w", encoding="utf-8") as f_out:
        json.dump(all_data, f_out, indent=2, ensure_ascii=False)

    print(f"\n✅ Mapping terminé. Total d'images traitées : {len(all_data)}")
