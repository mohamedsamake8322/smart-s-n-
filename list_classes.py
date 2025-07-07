import os

base_dir = r"C:\Users\moham\Music\plantdataset"
train_dir = os.path.join(base_dir, "train")
val_dir = os.path.join(base_dir, "val")

def list_classes(path, name):
    classes = sorted([d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))])
    print(f"\n📁 Classes dans {name} ({len(classes)} au total):\n")
    for cls in classes:
        print(f" - {cls}")
    return classes

# Afficher les classes dans train/ et val/
train_classes = list_classes(train_dir, "train")
val_classes = list_classes(val_dir, "val")
