import os

train_path = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
val_path = r"C:\plateforme-agricole-complete-v2\plantdataset\val"

# Liste des dossiers dans train
train_dirs = [d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d))]

# Liste des dossiers dans val
val_dirs = [d for d in os.listdir(val_path) if os.path.isdir(os.path.join(val_path, d))]

# Dossiers présents dans train mais absents dans val
missing_in_val = [d for d in train_dirs if d not in val_dirs]

print("Dossiers présents dans 'train' mais absents dans 'val' :")
for d in missing_in_val:
    print("-", d)
