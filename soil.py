import os
import requests
from pathlib import Path

# 📁 Dossier de sortie
output_dir = Path("soilgrids_v2")
output_dir.mkdir(exist_ok=True)
# 🌍 Liste des 33 pays (codes ISO ou noms pour filtrage ultérieur si tu veux découper par shapefile)
countries = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Central African Republic",
    "Chad", "Congo", "DR Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia",
    "Gabon", "Gambia", "Ghana", "Guinea", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Madagascar", "Malawi",
    "Mali", "Mauritania", "Morocco", "Mozambique", "Namibia", "Niger"
]

# 🧪 Variables et profondeurs
# 🔬 Variables ISRIC + Profondeurs
variables = ["clay", "sand", "silt", "bdod", "soc", "cec", "phh2o"]
depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

# 🌐 Base URL pour GeoTIFF
base_url = "https://files.isric.org/soilgrids/latest/data"

# 📥 Boucle de téléchargement
for var in variables:
    for depth in depths:
        filename = f"{var}_mean_{depth}.tif"
        url = f"{base_url}/{var}/{filename}"
        out_path = output_dir / filename

        if out_path.exists():
            print(f"✅ Déjà présent : {filename}")
            continue

        print(f"⬇️ Téléchargement : {filename}")
        response = requests.get(url)

        if response.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(response.content)
        else:
            print(f"❌ Erreur {response.status_code} pour {filename}")
