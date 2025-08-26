import os

# Chemin du dossier
folder_path = r"C:\plateforme-agricole-complete-v2\vector_store"

# Vérifier si le dossier existe
if os.path.exists(folder_path):
    print(f"📂 Contenu du dossier : {folder_path}\n")
    for item in os.listdir(folder_path):
        print(item)
else:
    print(f"⚠️ Le dossier {folder_path} n'existe pas.")
