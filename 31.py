import os
import shutil

train_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
val_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\val"

# Parcours rapide seulement des dossiers déjà existants dans val
val_folders = [f for f in os.listdir(val_dir) if os.path.isdir(os.path.join(val_dir, f))]

for folder in val_folders:
    train_folder_path = os.path.join(train_dir, folder)
    val_folder_path = os.path.join(val_dir, folder)
    if not os.path.exists(train_folder_path):
        # Si dossier absent dans train (peu probable), skip
        continue

    train_files = set(os.listdir(train_folder_path))
    val_files = set(os.listdir(val_folder_path))

    missing_files = train_files - val_files
    for file in missing_files:
        src = os.path.join(train_folder_path, file)
        dst = os.path.join(val_folder_path, file)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
            print(f"Copied missing folder '{file}' in '{folder}'")
        else:
            shutil.copy2(src, dst)
            print(f"Copied missing file '{file}' in folder '{folder}'")

print("Copying missing files done.")
