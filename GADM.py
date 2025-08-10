import os
import requests

# Liste des codes ISO des pays africains (extrait partiel, tu peux compléter)
african_countries = [
    "DZA", "AGO", "BEN", "BWA", "BFA", "BDI", "CPV", "CMR", "CAF", "TCD",
    "COM", "COG", "COD", "DJI", "EGY", "GNQ", "ERI", "SWZ", "ETH", "GAB",
    "GMB", "GHA", "GIN", "GNB", "CIV", "KEN", "LSO", "LBR", "LBY", "MDG",
    "MWI", "MLI", "MRT", "MUS", "MAR", "MOZ", "NAM", "NER", "NGA", "RWA",
    "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "TZA", "TGO",
    "TUN", "UGA", "ZMB", "ZWE"
]

# Niveaux disponibles
levels = [0, 1, 2, 3, 4]

# Dossier de base
base_dir = r"C:\plateforme-agricole-complete-v2\gadm"

# URL template
url_template = "https://geodata.ucdavis.edu/gadm/gadm4.1/gadm41_{iso}_{level}.geojson"

# Créer le dossier de base
os.makedirs(base_dir, exist_ok=True)

for iso in african_countries:
    country_dir = os.path.join(base_dir, iso)
    os.makedirs(country_dir, exist_ok=True)

    for level in levels:
        url = url_template.format(iso=iso, level=level)
        filename = f"level{level}.geojson"
        filepath = os.path.join(country_dir, filename)

        print(f"Téléchargement de {iso} niveau {level}...")
        response = requests.get(url)

        if response.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Sauvegardé : {filepath}")
        else:
            print(f"❌ Niveau {level} non disponible pour {iso}")
