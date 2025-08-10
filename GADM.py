import os
import requests
import zipfile
from io import BytesIO

# Liste des codes ISO des pays africains
african_countries = [
    "DZA", "AGO", "BEN", "BFA", "BDI", "CMR", "CPV", "CAF", "TCD", "COM",
    "COG", "CIV", "COD", "DJI", "EGY", "GNQ", "ERI", "SWZ", "ETH", "GAB",
    "GMB", "GHA", "GIN", "GNB", "KEN", "LSO", "LBR", "LBY", "MDG", "MWI",
    "MLI", "MRT", "MUS", "MYT", "MAR", "MOZ", "NAM", "NER", "NGA", "REU",
    "RWA", "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "TZA",
    "TGO", "TUN", "UGA", "ZMB", "ZWE"
]

# Dossier de base
base_dir = r"C:\plateforme-agricole-complete-v2\gadm"
os.makedirs(base_dir, exist_ok=True)

for iso in african_countries:
    print(f"📦 Téléchargement de {iso}...")
    zip_url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/gadm41_{iso}_geo.zip"
    response = requests.get(zip_url)

    if response.status_code == 200:
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            country_dir = os.path.join(base_dir, iso)
            os.makedirs(country_dir, exist_ok=True)

            for file in z.namelist():
                if file.endswith(".geojson"):
                    level = file.split("_")[-1].replace(".geojson", "")
                    target_path = os.path.join(country_dir, f"{level}.geojson")
                    with z.open(file) as source, open(target_path, "wb") as target:
                        target.write(source.read())
                    print(f"✅ {iso} - {level} sauvegardé")
    else:
        print(f"❌ Échec pour {iso}")
