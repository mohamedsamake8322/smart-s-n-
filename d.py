import os
import json

# Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
json_fr_path = os.path.join(base_path, "mapping_fiches_maladies_fr.json")

# Chargement des JSON
with open(json_en_path, encoding="utf-8") as f_en:
    en_data = json.load(f_en)
with open(json_fr_path, encoding="utf-8") as f_fr:
    fr_data = json.load(f_fr)

# Normalisation stricte
def normalize(name):
    return name.lower().strip().replace('_', ' ').replace('-', ' ').replace('  ', ' ')

# Création d’un dictionnaire des clés JSON normalisées
normalized_keys = {}
for key in set(list(en_data.keys()) + list(fr_data.keys())):
    norm = normalize(key)
    normalized_keys[norm] = key

# Récupération des dossiers
def get_disease_folders(path):
    folders = []
    for subset in ["train", "val"]:
        subset_path = os.path.join(path, subset)
        if os.path.exists(subset_path):
            folders += [folder for folder in os.listdir(subset_path)
                        if os.path.isdir(os.path.join(subset_path, folder))]
    return list(set(folders))

# Vérification réelle
found = {}
not_found = []

for folder in get_disease_folders(base_path):
    norm_name = normalize(folder)
    match = normalized_keys.get(norm_name)

    if match:
        found[folder] = match
    else:
        not_found.append(folder)

# Affichage
print("\n✅ Correspondances trouvées avec les JSONs :")
for folder, json_key in sorted(found.items()):
    print(f" - {folder} → {json_key}")

print("\n❌ Dossiers sans correspondance exacte :")
for folder in sorted(not_found):
    print(f" - {folder}")
