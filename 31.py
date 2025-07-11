import os
import shutil

train_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
val_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\val"

# Liste dossiers dans train
train_folders = [f for f in os.listdir(train_dir) if os.path.isdir(os.path.join(train_dir, f))]

# Liste dossiers dans val (pour savoir lesquels existent déjà)
val_folders = set(f for f in os.listdir(val_dir) if os.path.isdir(os.path.join(val_dir, f)))

for folder in train_folders:
    if folder not in val_folders:
        src = os.path.join(train_dir, folder)
        dst = os.path.join(val_dir, folder)
        print(f"Copying folder '{folder}' with all contents...")
        shutil.copytree(src, dst)

print("Copy complete.")
