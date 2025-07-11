import os
from PIL import Image

def nettoyer_images_corrompues(dossier_racine):
    extensions_images = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
    count_total = 0
    count_supprimees = 0

    for root, dirs, files in os.walk(dossier_racine):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions_images:
                count_total += 1
                chemin_fichier = os.path.join(root, file)
                try:
                    # Essayer d'ouvrir l'image
                    with Image.open(chemin_fichier) as img:
                        img.verify()  # Vérifie que l’image n’est pas corrompue
                except Exception as e:
                    print(f"Image corrompue détectée et supprimée : {chemin_fichier}")
                    os.remove(chemin_fichier)
                    count_supprimees += 1

    print(f"Total images vérifiées : {count_total}")
    print(f"Images corrompues supprimées : {count_supprimees}")

# Exemple d’utilisation
dossier_train = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
dossier_val = r"C:\plateforme-agricole-complete-v2\plantdataset\val"

print("Nettoyage des images dans TRAIN...")
nettoyer_images_corrompues(dossier_train)

print("\nNettoyage des images dans VAL...")
nettoyer_images_corrompues(dossier_val)
