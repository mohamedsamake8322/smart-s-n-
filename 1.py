import geopandas as gpd
import requests
import os

# 🌍 Liste des pays africains selon leur code ISO3
african_countries = ['AGO', 'BEN', 'BFA', 'BDI', 'CMR', 'CAF', 'TCD', 'COM', 'COG', 'CIV', 'DJI', 'EGY',
                     'GNQ', 'ERI', 'ETH', 'GAB', 'GMB', 'GHA', 'GIN', 'GNB', 'KEN', 'LSO', 'LBR', 'LBY',
                     'MDG', 'MWI', 'MLI', 'MRT', 'MUS', 'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'RWA', 'STP',
                     'SEN', 'SYC', 'SLE', 'SOM', 'ZAF', 'SSD', 'SDN', 'SWZ', 'TZA', 'TGO', 'TUN', 'UGA',
                     'ZMB', 'ZWE']

# 📁 Dossier de destination
os.makedirs("gadm_africa_geojson", exist_ok=True)

for iso3 in african_countries:
    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso3}_2.json"
    response = requests.get(url)
    if response.status_code == 200:
        with open(f"gadm_africa_geojson/{iso3}_level2.geojson", "wb") as f:
            f.write(response.content)
        print(f"✅ Téléchargé : {iso3}")
    else:
        print(f"❌ Échec : {iso3}")
