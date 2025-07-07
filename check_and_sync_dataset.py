import os
import shutil

base_dir = r"C:\Users\moham\Music\plantdataset"
train_path = os.path.join(base_dir, "train")
val_path = os.path.join(base_dir, "val")

# Lire les noms des classes
train_classes = sorted([d for d in os.listdir(train_path) if os.path.isdir(os.path.join(train_path, d))])
val_classes = sorted([d for d in os.listdir(val_path) if os.path.isdir(os.path.join(val_path, d))])

# Trouver les classes manquantes dans val/
missing_in_val = sorted(set(train_classes) - set(val_classes))

print(f"🔎 Total classes in train: {len(train_classes)}")
print(f"📁 Total classes in val  : {len(val_classes)}\n")

if missing_in_val:
    print(f"❌ Classes présentes dans train mais manquantes dans val :")
    for cls in missing_in_val:
        print(f"   - {cls}")

    # Copier quelques images pour compléter
    for cls in missing_in_val:
        src = os.path.join(train_path, cls)
        dst = os.path.join(val_path, cls)
        os.makedirs(dst, exist_ok=True)

        # Prendre jusqu’à 5 images pour compléter val/
        for i, file in enumerate(os.listdir(src)):
            if file.lower().endswith(".jpg") or file.lower().endswith(".png"):
                if i >= 30: break
                shutil.copy(os.path.join(src, file), os.path.join(dst, file))
        print(f"✅ Classe {cls} copiée dans val/ avec quelques échantillons.")
else:
    print("✅ Toutes les classes de train sont présentes dans val.")
