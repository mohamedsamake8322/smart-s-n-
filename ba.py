#🛠 Script Python : Téléchargement d’images via SerpAPI
import os
import json
import requests
import random
from serpapi import GoogleSearch

# Clé API SerpAPI
SERPAPI_KEY = "639c911a059fa04eb8f43179c0cafbfcf775b342"

# Chemin du dataset
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"

# Paramètres de téléchargement
train_range = (20, 30)
val_range = (10, 15)
image_extensions = [".jpg", ".jpeg", ".png"]

# Fonction pour chercher des images via SerpAPI
def fetch_image_urls(query, max_results=30):
    search = GoogleSearch({
        "q": query,
        "tbm": "isch",
        "api_key": SERPAPI_KEY
    })
    results = search.get_dict()
    images = results.get("images_results", [])
    return [img["original"] for img in images[:max_results] if "original" in img]

# Fonction pour télécharger une image
def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            ext = os.path.splitext(url)[1].lower()
            if ext not in image_extensions:
                ext = ".jpg"
            with open(save_path + ext, "wb") as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

# Parcours des dossiers
for subset, (min_img, max_img) in [("train", train_range), ("val", val_range)]:
    subset_path = os.path.join(base_path, subset)
    for folder in os.listdir(subset_path):
        folder_path = os.path.join(subset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        # Vérifie si le dossier contient déjà des images
        existing = [f for f in os.listdir(folder_path) if f.lower().endswith(tuple(image_extensions))]
        if len(existing) >= min_img:
            continue  # Skip si déjà rempli

        print(f"🔍 Recherche d’images pour : {folder} ({subset})")
        query = folder.replace("_", " ").replace("-", " ")
        urls = fetch_image_urls(query, max_results=max_img)

        count = 0
        for i, url in enumerate(urls):
            filename = f"img_{i+1}"
            save_path = os.path.join(folder_path, filename)
            if download_image(url, save_path):
                count += 1
            if count >= max_img:
                break

        print(f"✅ {count} images ajoutées à : {folder} ({subset})")

print("\n🎉 Téléchargement terminé pour tous les dossiers.")
