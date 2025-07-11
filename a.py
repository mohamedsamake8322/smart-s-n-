import os
import json

# Chemins vers les fichiers JSON
base_path = r'C:\plateforme-agricole-complete-v2\plantdataset'
json_en_path = os.path.join(base_path, 'EN_mapping_fiches_maladies.json')
json_fr_path = os.path.join(base_path, 'mapping_fiches_maladies_fr.json')

# Chargement des bibliothèques JSON
with open(json_en_path, encoding='utf-8') as f_en:
    en_mapping = json.load(f_en)

with open(json_fr_path, encoding='utf-8') as f_fr:
    fr_mapping = json.load(f_fr)

# Fonction utilitaire pour nettoyer les noms pour comparaison
def normalize(name):
    return name.strip().lower()

# Récupération des noms de dossiers de maladies dans train et val
def get_disease_folders(path):
    folders = []
    for subset in ['train', 'val']:
        subset_path = os.path.join(path, subset)
        if os.path.exists(subset_path):
            folders += [folder for folder in os.listdir(subset_path)
                        if os.path.isdir(os.path.join(subset_path, folder))]
    return folders

# Récupération et normalisation des clés des deux JSON
en_keys = {normalize(k) for k in en_mapping.keys()}
fr_keys = {normalize(k) for k in fr_mapping.keys()}

# Vérification des correspondances
disease_folders = get_disease_folders(base_path)
defined_in_both = []
undefined = []

for folder in disease_folders:
    norm_name = normalize(folder)
    if norm_name in en_keys and norm_name in fr_keys:
        defined_in_both.append(folder)
    else:
        undefined.append(folder)

# Affichage des résultats
print("✅ Maladies définies dans les deux fichiers JSON :")
for name in defined_in_both:
    print(f" - {name}")

print("\n⚠️ Maladies NON définies dans les deux fichiers JSON :")
for name in undefined:
    print(f" - {name}")
