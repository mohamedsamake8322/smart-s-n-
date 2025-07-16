import os
import requests
from pathlib import Path

# 📁 Dossier de sortie
output_dir = Path("soilgrids_africa")
output_dir.mkdir(exist_ok=True)

# 🌍 Liste des 33 pays (codes ISO ou noms pour filtrage ultérieur si tu veux découper par shapefile)
countries = [
    "Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cameroon", "Central African Republic",
    "Chad", "Congo", "DR Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia",
    "Gabon", "Gambia", "Ghana", "Guinea", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Madagascar", "Malawi",
    "Mali", "Mauritania", "Morocco", "Mozambique", "Namibia", "Niger"
]

# 🧪 Variables et profondeurs
variables = {
    "clay": ["0-5cm", "100-200cm"],
    "sand": ["0-5cm", "100-200cm"],
    "silt": ["0-5cm", "100-200cm"],
    "bdod": ["0-5cm", "100-200cm"],  # Masse volumique apparente
    "soc": ["0-5cm", "100-200cm"],   # Carbone organique
    "cec": ["0-5cm", "100-200cm"],   # Capacité d’échange cationique
    "phh2o": ["0-5cm", "100-200cm"]  # pH
}

# 📡 URL de base
base_url = "https://files.isric.org/soilgrids/latest/data"

# 📥 Téléchargement
for var, depths in variables.items():
    for depth in depths:
        filename = f"{var}_{depth}_mean.tif"
        url = f"{base_url}/{var}/{filename}"
        out_path = output_dir / filename
        if not out_path.exists():
            print(f"Téléchargement : {filename}")
            r = requests.get(url)
            if r.status_code == 200:
                with open(out_path, "wb") as f:
                    f.write(r.content)
            else:
                print(f"❌ Échec pour {filename} ({r.status_code})")
        else:
            print(f"✅ Déjà téléchargé : {filename}")
