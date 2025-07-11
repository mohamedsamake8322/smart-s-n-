import os
import json

# Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
json_en_path = os.path.join(base_path, "EN_mapping_fiches_maladies.json")
json_fr_path = os.path.join(base_path, "mapping_fiches_maladies_fr.json")

# Charger les JSONs
with open(json_en_path, encoding="utf-8") as f_en:
    en_data = json.load(f_en)
with open(json_fr_path, encoding="utf-8") as f_fr:
    fr_data = json.load(f_fr)

# Fonction pour récupérer les noms des dossiers
def get_disease_folders(path):
    folders = []
    for subset in ['train', 'val']:
        subset_path = os.path.join(path, subset)
        if os.path.exists(subset_path):
            folders += [folder for folder in os.listdir(subset_path)
                        if os.path.isdir(os.path.join(subset_path, folder))]
    return list(set(folders))

# Vérification des correspondances exactes
disease_folders = get_disease_folders(base_path)
defined = []
undefined = []

for folder in disease_folders:
    if folder in en_data and folder in fr_data:
        defined.append(folder)
    else:
        undefined.append(folder)

# Affichage
print("\n✅ Maladies définies dans les deux fichiers JSON :")
for name in sorted(defined):
    print(f" - {name}")

print("\n⚠️ Maladies NON reconnues dans les deux fichiers JSON :")
for name in sorted(undefined):
    print(f" - {name}")
