import os
import json

# Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
json_fr_path = os.path.join(base_path, "mapping_fiches_maladies_fr.json")
output_dir = os.path.join(base_path, "fiche_par_maladie")

# Charger les JSONs
with open(json_en_path, encoding="utf-8") as f_en:
    en_data = json.load(f_en)
with open(json_fr_path, encoding="utf-8") as f_fr:
    fr_data = json.load(f_fr)

# Normalisation
def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")

# Associer les clés normalisées à leurs versions originales
json_keys = {}
for key in set(en_data.keys()) | set(fr_data.keys()):
    json_keys[normalize(key)] = key

# Préparer le dossier de sortie
os.makedirs(output_dir, exist_ok=True)

# Parcourir chaque dossier maladie
for subset in ["train", "val"]:
    subset_path = os.path.join(base_path, subset)
    if not os.path.exists(subset_path):
        continue

    for folder in os.listdir(subset_path):
        folder_path = os.path.join(subset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        norm_folder = normalize(folder)
        json_key = json_keys.get(norm_folder)
        if not json_key:
            continue  # Maladie non reconnue

        # Récupérer les données EN/FR
        fiche = {
            "dossier": folder,
            "json_key": json_key,
            "en": en_data.get(json_key, {}),
            "fr": fr_data.get(json_key, {}),
            "images": []
        }

        # Ajouter les fichiers image
        for img in os.listdir(folder_path):
            if os.path.isfile(os.path.join(folder_path, img)):
                fiche["images"].append({
                    "filename": img,
                    "path": os.path.join(subset, folder, img)
                })

        # Enregistrer dans un fichier JSON par dossier
        out_path = os.path.join(output_dir, f"{folder}.json")
        with open(out_path, "w", encoding="utf-8") as f_out:
            json.dump(fiche, f_out, indent=4, ensure_ascii=False)

print(f"✅ Fiches générées dans : {output_dir}")
