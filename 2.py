import os
import shutil
import random

def stratified_split(train_dir, val_dir, split_ratio=0.2, seed=42):
    random.seed(seed)
    total_copied = 0

    for class_name in os.listdir(train_dir):
        class_train = os.path.join(train_dir, class_name)
        class_val = os.path.join(val_dir, class_name)

        if not os.path.isdir(class_train):
            continue  # Ignorer les fichiers non répertoires

        os.makedirs(class_val, exist_ok=True)

        images = [f for f in os.listdir(class_train) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        num_total = len(images)
        num_to_copy = int(num_total * split_ratio)

        if num_to_copy == 0:
            print(f"[!] Classe '{class_name}' a trop peu d'images pour le split.")
            continue

        selected = random.sample(images, num_to_copy)
        copied_count = 0

        for img_name in selected:
            src = os.path.join(class_train, img_name)
            dst = os.path.join(class_val, img_name)

            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied_count += 1

        total_copied += copied_count
        print(f"[✓] {class_name} → {copied_count} images copiées dans val/ ({num_total} total)")

    print(f"\n🚀 Split terminé : {total_copied} images déplacées vers 'val/'.")

# === Paramètres ===
train_path = r"C:\Users\moham\Pictures\plantdataset\train"
val_path = r"C:\Users\moham\Pictures\plantdataset\val"
proportion = 0.3  # 30% vers val

stratified_split(train_path, val_path, proportion)
