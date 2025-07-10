import os

def normalize(name):
    return name.lower().strip().replace("_", " ").replace("  ", " ")

dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset"
subfolders = ["train", "val"]

class_names = set()

for folder in subfolders:
    folder_path = os.path.join(dataset_path, folder)
    if os.path.isdir(folder_path):
        subdirs = os.listdir(folder_path)
        for d in subdirs:
            full_path = os.path.join(folder_path, d)
            if os.path.isdir(full_path):
                class_names.add(normalize(d))

print(f"Nombre total de classes (normalisées) : {len(class_names)}")
