import os

# Dossier racine
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"

# Sous-dossiers à explorer (train, val, etc.)
subfolders = [f for f in os.listdir(dataset_path) if os.path.isdir(os.path.join(dataset_path, f))]

# Dictionnaire pour stocker les classes par sous-dossier
classes_dict = {}

for folder in subfolders:
    folder_path = os.path.join(dataset_path, folder)
    classes = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    classes_dict[folder] = classes

# Affichage
for folder, class_list in classes_dict.items():
    print(f"\n🔍 {folder.upper()} contient {len(class_list)} classes :")
    for cls in class_list:
        print(f" - {cls}")
