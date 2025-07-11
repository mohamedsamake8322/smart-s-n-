#📦 Résultat :
#Tu auras un dossier pour chaque maladie définie mais absente.
#Chaque dossier contiendra un fichier fiche_maladie.json prêt à être enrichi avec des images.
#Tu peux ensuite annoter, collecter ou générer des images pour ces maladies.
import os
import json

# Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
json_fr_path = os.path.join(base_path, "mapping_fiches_maladies_fr.json")
output_dir = os.path.join(base_path, "train")  # ou "val" selon ton choix

# Charger les JSONs
with open(json_en_path, encoding="utf-8") as f_en:
    en_data = json.load(f_en)
with open(json_fr_path, encoding="utf-8") as f_fr:
    fr_data = json.load(f_fr)

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
json_keys = {}
for key in set(en_data.keys()) | set(fr_data.keys()):
    json_keys[normalize(key)] = key

# Création des dossiers manquants
created = []

for norm_key, original_key in json_keys.items():
    if norm_key not in existing_folders:
        folder_path = os.path.join(output_dir, original_key)
        os.makedirs(folder_path, exist_ok=True)

        fiche = {
            "dossier": original_key,
            "en": en_data.get(original_key, {}),
            "fr": fr_data.get(original_key, {}),
            "images": []  # vide pour l’instant
        }

        # Sauvegarde de la fiche dans le dossier
        fiche_path = os.path.join(folder_path, "fiche_maladie.json")
        with open(fiche_path, "w", encoding="utf-8") as f_out:
            json.dump(fiche, f_out, indent=4, ensure_ascii=False)

        created.append(original_key)
        print(f"📁 Dossier créé : {original_key}")

# Résumé
print(f"\n✅ {len(created)} dossiers manquants ont été créés dans : {output_dir}")
