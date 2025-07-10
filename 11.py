import os

# Chemin vers le dossier contenant les classes
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"

# Lister les dossiers (classes)
classes = [name for name in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, name))]

# Affichage
print(f"Nombre de classes trouvées : {len(classes)}")
print("Noms des classes :")
for cls in classes:
    print(f"- {cls}")
