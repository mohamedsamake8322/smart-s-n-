import os
from PIL import Image

# Dossier à nettoyer
DATASET_DIR = r"C:\Users\moham\Music\deficiencies"
removed = []

# Parcours des fichiers
for root, dirs, files in os.walk(DATASET_DIR):
    for file in files:
        if file.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff")):
            path = os.path.join(root, file)
            try:
                with Image.open(path) as img:
                    img.verify()  # Vérifie l'intégrité
            except Exception as e:
                print(f"❌ Image corrompue supprimée : {path}")
                os.remove(path)
                removed.append(path)

print(f"\n✅ Nettoyage terminé. {len(removed)} image(s) supprimée(s).")
