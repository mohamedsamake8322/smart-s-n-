import os
import shutil
import random

# 📂 Répertoires
train_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\val"
illustrations_dir = r"C:\plateforme-agricole-complete-v2\illustrations"
max_images = 8
extensions = [".jpg", ".jpeg", ".png", ".webp"]

# 🌀 Création du dossier illustrations s'il n'existe pas
os.makedirs(illustrations_dir, exist_ok=True)

print("🚀 Lancement de la copie des images illustratives...\n")

# 💼 Boucle sur chaque classe de maladie
for disease_name in os.listdir(train_dir):
    src_subdir = os.path.join(train_dir, disease_name)
    dst_subdir = os.path.join(illustrations_dir, disease_name)

    if not os.path.isdir(src_subdir):
        continue  # Ignore les fichiers non dossiers

    print(f"📁 Traitement de la classe : {disease_name}")

    os.makedirs(dst_subdir, exist_ok=True)

    images = [f for f in os.listdir(src_subdir) if os.path.splitext(f)[1].lower() in extensions]
    selected_images = random.sample(images, min(len(images), max_images))

    if not selected_images:
        print("⚠️ Aucune image trouvée dans ce dossier.")
        continue

    for i, image in enumerate(selected_images, 1):
        src_path = os.path.join(src_subdir, image)
        dst_path = os.path.join(dst_subdir, image)
        shutil.copy2(src_path, dst_path)
        print(f"  ✅ Copié [{i}/{len(selected_images)}] : {image}")

    print("✅ Terminé pour cette classe.\n")

print("🎉 Copie des images terminée pour toutes les classes !")
