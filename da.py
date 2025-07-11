import os
import json
import requests

# 🔑 Clés Google Custom Search
API_KEY = "AIzaSyCiI8dCsaLs8uHxdJzNXOiS_790_5CTTnU"
CX = "72138b4cb9b0d4073"  # Remplace par ton vrai CX ici si différent

# 📁 Chemins
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
query_file = os.path.join(base_path, "search_queries.json")
image_extensions = [".jpg", ".jpeg", ".png"]

# 📥 Fonction pour télécharger une image
def download_image(url, save_path):
    try:
        ext = os.path.splitext(url)[1].lower()
        if ext not in image_extensions:
            ext = ".jpg"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path + ext, "wb") as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False

# 📖 Lecture du fichier JSON
with open(query_file, encoding="utf-8") as f:
    queries = json.load(f)

# 🔄 Traitement des requêtes
for item in queries:
    subset = item["subset"]
    folder = item["folder"]
    query = item["query"]
    min_img = item["min_images"]
    max_img = item["max_images"]
    target_path = os.path.join(base_path, subset, folder)

    if not os.path.exists(target_path):
        continue

    existing = [f for f in os.listdir(target_path) if f.lower().endswith(tuple(image_extensions))]
    if len(existing) >= min_img:
        continue

    print(f"🔍 {subset}/{folder} → {query}")
    downloaded = 0
    start_index = 1

    while downloaded < max_img:
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&searchType=image&start={start_index}&num=10&key={API_KEY}&cx={CX}"
        try:
            response = requests.get(url).json()
            items = response.get("items", [])
            if not items:
                break

            for i, item in enumerate(items):
                img_url = item.get("link")
                if not img_url:
                    continue
                filename = f"img_{len(existing) + downloaded + 1}"
                save_path = os.path.join(target_path, filename)
                if download_image(img_url, save_path):
                    downloaded += 1
                if downloaded >= max_img:
                    break

            start_index += 10
        except Exception as e:
            print(f"⚠️ Erreur sur {folder}: {e}")
            break

    print(f"✅ {downloaded} images ajoutées à : {folder} ({subset})")

print("\n🎉 Téléchargement Google Images terminé pour tous les dossiers.")
