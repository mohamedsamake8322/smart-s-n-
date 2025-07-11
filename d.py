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

# Fonction de normalisation stricte
def normalize(name):
    return name.lower().strip().replace('_', ' ').replace('-', ' ').replace('  ', ' ')

# Récupération des noms de dossiers
def get_disease_folders(path):
    folders = []
    for subset in ['train', 'val']:
        subset_path = os.path.join(path, subset)
        if os.path.exists(subset_path):
            folders += [folder for folder in os.listdir(subset_path)
                        if os.path.isdir(os.path.join(subset_path, folder))]
    return list(set(folders))

# Normalisation des clés JSON
en_keys = {normalize(k): k for k in en_data.keys()}
fr_keys = {normalize(k): k for k in fr_data.keys()}

# Vérification
defined = []
undefined = []

for folder in get_disease_folders(base_path):
    norm = normalize(folder)
    if norm in en_keys and norm in fr_keys:
        defined.append(folder)
    else:
        undefined.append(folder)

# Affichage
print("\n✅ Maladies reconnues dans les deux JSON (normalisées) :")
for name in sorted(defined):
    print(f" - {name}")

print("\n⚠️ Maladies NON reconnues dans les deux JSON :")
for name in sorted(undefined):
    print(f" - {name}")
