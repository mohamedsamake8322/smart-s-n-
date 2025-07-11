import os
import json
import unicodedata

# Chemin du dataset
base_path = r"C:/plateforme-agricole-complete-v2/plantdataset"
output_path = os.path.join(base_path, "search_queries.json")

# Normalisation simple
def normalize(text):
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode()
    text = text.lower().replace("_", " ").replace("-", " ").strip()
    return " ".join(text.split())

# Reformulation heuristique
def reformulate(name):
    name = normalize(name)
    if "healthy" in name:
        return f"healthy {name.replace('healthy', '').strip()} plant"
    if "powdery mildew" in name:
        return f"{name} disease on leaves"
    if "leaf spot" in name or "blight" in name:
        return f"{name} symptoms on crop leaves"
    if "mite" in name or "worm" in name or "beetle" in name:
        return f"{name} pest damage on plants"
    if "virus" in name or "mosaic" in name:
        return f"{name} virus symptoms on crops"
    if "rot" in name or "burn" in name:
        return f"{name} fungal disease on stems or roots"
    return f"{name} plant disease"

# Collecte des dossiers
search_queries = []

for subset, (min_img, max_img) in [("train", (20, 30)), ("val", (10, 15))]:
    subset_path = os.path.join(base_path, subset)
    if not os.path.exists(subset_path):
        continue

    for folder in os.listdir(subset_path):
        folder_path = os.path.join(subset_path, folder)
        if not os.path.isdir(folder_path):
            continue

        query = reformulate(folder)
        search_queries.append({
            "subset": subset,
            "folder": folder,
            "query": query,
            "min_images": min_img,
            "max_images": max_img
        })

# Sauvegarde
with open(output_path, "w", encoding="utf-8") as f_out:
    json.dump(search_queries, f_out, indent=4, ensure_ascii=False)

print(f"✅ Requêtes reformulées sauvegardées dans : {output_path}")
