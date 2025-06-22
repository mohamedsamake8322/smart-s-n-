import os
from collections import Counter

def explorer_dataset(dataset_path):
    compteur = Counter()

    for racine, dossiers, fichiers in os.walk(dataset_path):
        if fichiers:
            classe = os.path.basename(racine)
            compteur[classe] += len(fichiers)

    print("Résumé du dataset :\n")
    for classe, nb_images in compteur.items():
        print(f"🔸 {classe} : {nb_images} image(s)")
    print(f"\nNombre total de classes : {len(compteur)}")
    print(f"Nombre total d’images : {sum(compteur.values())}")

# Exemple d'utilisation :
explorer_dataset(r"C:\Downloads\archive\农作物病虫害数据集")

