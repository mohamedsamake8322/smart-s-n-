import shutil
import os

# Chemin source et destination
source = r"C:\plateforme-agricole-complete-v2\plantdataset"
destination = r"H:\My Drive\plantdataset"

# Vérifier si la source existe
if not os.path.exists(source):
    raise FileNotFoundError(f"Le dossier source n'existe pas : {source}")

# Créer le dossier de destination si nécessaire
os.makedirs(os.path.dirname(destination), exist_ok=True)

# Déplacer le dossier
shutil.move(source, destination)
print(f"Dossier déplacé de {source} vers {destination}")
