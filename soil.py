from pystac_client import Client
import requests
import os

# 📁 Crée un dossier local pour stocker les téléchargements
output_folder = "./isdasoil_downloads"
os.makedirs(output_folder, exist_ok=True)

# 🌍 Charger le catalogue STAC
catalog_url = "https://isdasoil.s3.amazonaws.com/catalog.json"
catalog = Client.open(catalog_url)

# 📦 Accéder à la collection "soil_data"
soil_collection = catalog.get_child("soil_data")

# 🌾 Variables que tu veux télécharger
variables_cibles = ["ph", "carbon", "nitrogen", "clay", "sand", "silt"]

# 🔁 Boucle sur tous les items
for item in soil_collection.get_items():
    props = item.to_dict().get("properties", {})
    var_name = props.get("soil_property")

    if var_name and any(v in var_name.lower() for v in variables_cibles):
        asset = item.assets.get("image")
        if asset:
            url = asset.href
            filename = os.path.join(output_folder, url.split("/")[-1])

            print(f"⬇️ Téléchargement : {filename}")
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"✅ Terminé : {filename}")
