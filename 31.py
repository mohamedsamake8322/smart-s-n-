import os
import shutil

train_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
val_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\val"

# Liste des dossiers dans train
train_folders = [f for f in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, f))]

for folder in train_folders:
    train_folder_path = os.path.join(train_dir, folder)
    val_folder_path = os.path.join(val_dir, folder)

    # Si dossier absent dans val, on le copie entièrement
    if not os.path.exists(val_folder_path):
        print(f"Copying missing folder '{folder}' from train to val...")
        shutil.copytree(train_folder_path, val_folder_path)
    else:
        # Si dossier existe déjà dans val, on copie seulement les fichiers manquants
        train_files = os.listdir(train_folder_path)
        val_files = os.listdir(val_folder_path)
        for file in train_files:
            train_file_path = os.path.join(train_folder_path, file)
            val_file_path = os.path.join(val_folder_path, file)
            if not os.path.exists(val_file_path):
                print(f"Copying missing file '{file}' in folder '{folder}'...")
                if os.path.isdir(train_file_path):
                    shutil.copytree(train_file_path, val_file_path)
                else:
                    shutil.copy2(train_file_path, val_file_path)

print("Copy complete.")
