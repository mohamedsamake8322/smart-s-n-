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
query_file = os.path.join(base_path, "search_queries.json")
image_extensions = [".jpg", ".jpeg", ".png"]

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

# Lecture du fichier de requêtes
with open(query_file, encoding="utf-8") as f:
    queries = json.load(f)

# Traitement de chaque requête
for item in queries:
    subset = item["subset"]
    folder = item["folder"]
    query = item["query"]
    min_img = item["min_images"]
    max_img = item["max_images"]
    target_path = os.path.join(base_path, subset, folder)

    if not os.path.exists(target_path):
        continue

    # Vérifie les images déjà présentes
    existing = [f for f in os.listdir(target_path) if f.lower().endswith(tuple(image_extensions))]
    if len(existing) >= min_img:
        continue

    print(f"🔍 {subset}/{folder} → {query}")
    search = GoogleSearch({
        "q": query,
        "tbm": "isch",
        "api_key": SERPAPI_KEY
    })
    results = search.get_dict()
    images = results.get("images_results", [])
    urls = [img["original"] for img in images if "original" in img]

    count = 0
    for i, url in enumerate(urls):
        filename = f"img_{len(existing) + i + 1}"
        save_path = os.path.join(target_path, filename)
        if download_image(url, save_path):
            count += 1
        if count >= max_img:
            break

    print(f"✅ {count} images ajoutées à : {folder} ({subset})")

print("\n🎉 Téléchargement terminé pour toutes les requêtes.")
