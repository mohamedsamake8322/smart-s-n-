import os
import requests
import geopandas as gpd

GADM_ROOT = "C:/plateforme-agricole-complete-v2/gadm"
GADM_GITHUB = "https://raw.githubusercontent.com/ozgrozer/gadm-country-json/master"

AFRICAN_COUNTRIES = [
    "AGO", "BEN", "BFA", "BDI", "CMR", "CAF", "TCD", "COM", "COG", "CIV", "DJI", "EGY", "GNQ", "ERI", "ETH",
    "GAB", "GMB", "GHA", "GIN", "GNB", "KEN", "LSO", "LBR", "LBY", "MDG", "MWI", "MLI", "MRT", "MUS", "MAR",
    "MOZ", "NAM", "NER", "NGA", "RWA", "STP", "SEN", "SYC", "SLE", "SOM", "ZAF", "SSD", "SDN", "SWZ", "TZA",
    "TGO", "TUN", "UGA", "ZMB", "ZWE"
]

LEVELS = ["0", "1", "2"]

def download_gadm(country_code, level):
    url = f"{GADM_GITHUB}/{country_code}/{country_code}_adm{level}.geojson"
    dest_dir = os.path.join(GADM_ROOT, country_code)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, f"level{level}.geojson")

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"✅ Downloaded {country_code} level {level}")
    except Exception as e:
        print(f"❌ Failed to download {country_code} level {level}: {e}")

def validate_geojson(path):
    try:
        gdf = gpd.read_file(path)
        return not gdf.empty and gdf.is_valid.all()
    except:
        return False

def ensure_gadm(country_code):
    for level in LEVELS:
        path = os.path.join(GADM_ROOT, country_code, f"level{level}.geojson")
        if not os.path.exists(path) or not validate_geojson(path):
            download_gadm(country_code, level)

def run_gadm_check():
    for country_code in AFRICAN_COUNTRIES:
        ensure_gadm(country_code)

if __name__ == "__main__":
    run_gadm_check()
