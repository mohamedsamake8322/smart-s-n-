import os
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, as_completed

extensions_images = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}

def verifier_image(chemin_fichier):
    try:
        with Image.open(chemin_fichier) as img:
            img.verify()
        return (chemin_fichier, True)
    except:
        return (chemin_fichier, False)

def nettoyer_images_corrompues_parallel(dossier_racine, max_workers=16, verbose=False):
    chemins_images = []
    for root, dirs, files in os.walk(dossier_racine):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in extensions_images:
                chemins_images.append(os.path.join(root, file))

    print(f"Nombre total d'images à vérifier : {len(chemins_images)}")

    supprimees = 0
    # Pour éviter les doublons, on utilise un set
    supprimees_paths = set()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(verifier_image, img): img for img in chemins_images}

        for future in as_completed(futures):
            chemin, valide = future.result()
            if not valide and chemin not in supprimees_paths:
                try:
                    os.remove(chemin)
                    supprimees_paths.add(chemin)
                    supprimees += 1
                    if verbose:
                        print(f"Supprimée image corrompue : {chemin}")
                except Exception as e:
                    if verbose:
                        print(f"Erreur suppression {chemin}: {e}")

    print(f"Total images corrompues supprimées : {supprimees}")

# Exemple d'utilisation :
dossier_train = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
nettoyer_images_corrompues_parallel(dossier_train, max_workers=16, verbose=True)
