import os
import json

# Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")

# Charger le JSON anglais uniquement
with open(json_en_path, encoding="utf-8") as f_en:
    en_data = json.load(f_en)

# Normalisation
def normalize(name):
    return name.lower().strip().replace("_", " ").replace("-", " ").replace("  ", " ")

# Dossiers existants
existing_folders = set()
for subset in ["train", "val"]:
    subset_path = os.path.join(base_path, subset)
    if os.path.exists(subset_path):
        existing_folders.update([
            normalize(folder) for folder in os.listdir(subset_path)
            if os.path.isdir(os.path.join(subset_path, folder))
        ])

# Clés JSON normalisées
json_keys = {normalize(k): k for k in en_data.keys()}

# Création dans train/ et val/
created = []

for norm_key, original_key in json_keys.items():
    if norm_key not in existing_folders:
        for subset in ["train", "val"]:
            new_path = os.path.join(base_path, subset, original_key)
            os.makedirs(new_path, exist_ok=True)

            # Créer fiche maladie
            fiche = {
                "dossier": original_key,
                "en": en_data.get(original_key, {}),
                "images": []  # vide pour l'instant
            }

            # Sauvegarder dans le dossier
            fiche_path = os.path.join(new_path, "fiche_maladie.json")
            with open(fiche_path, "w", encoding="utf-8") as f_out:
                json.dump(fiche, f_out, indent=4, ensure_ascii=False)

        created.append(original_key)
        print(f"📁 Dossiers 'train' et 'val' créés pour : {original_key}")

# Résumé
print(f"\n✅ {len(created)} nouvelles maladies ajoutées à 'train' et 'val'")
