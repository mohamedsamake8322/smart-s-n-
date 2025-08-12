import os

# 📂 Chemin du dossier à analyser
base_path = r"C:\plateforme-agricole-complete-v2\gadm"

# Parcours du dossier
for root, dirs, files in os.walk(base_path):
    # Affiche le chemin relatif depuis la racine
    relative_path = os.path.relpath(root, base_path)
    if relative_path == ".":
        relative_path = base_path  # Nom complet si racine

    print(f"\n📁 Dossier : {relative_path}")

    if dirs:
        print("   ├── Sous-dossiers :", ", ".join(dirs))
    else:
        print("   ├── Aucun sous-dossier")

    if files:
        print("   ├── Fichiers :", ", ".join(files))
    else:
        print("   ├── Aucun fichier")
