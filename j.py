import os
import pandas as pd
from datetime import datetime
import hashlib
import geopandas as gpd
from shapely.geometry import Point
from tqdm import tqdm
from colorama import Fore, Style, init


# 🎨 Initialiser colorama pour couleur terminal
init(autoreset=True)

# 📁 Dossier météo & shapefile
data_folder = r"C:\Users\moham\Music\weather_data_africa"
shapefile_path = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp"
world = gpd.read_file(shapefile_path)

unique_hashes = set()
records = []

def get_country_from_coords(lat, lon):
    point = Point(lon, lat)
    match = world[world.contains(point)]
    if not match.empty:
        return match.iloc[0]['name']
    return "Unknown"

def extract_location_header(lines):
    lat = lon = None
    for line in lines:
        if "latitude" in line and "longitude" in line:
            parts = line.split()
            try:
                lat = float(parts[parts.index("latitude") + 1])
                lon = float(parts[parts.index("longitude") + 1])
            except (ValueError, IndexError):
                pass
            break
    return lat, lon

def find_data_start(lines):
    for i, line in enumerate(lines):
        if line.strip().startswith("YEAR"):
            return i
    return None

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        hashcode = hashlib.md5(content.encode()).hexdigest()
        if hashcode in unique_hashes:
            print(Fore.YELLOW + f"[SKIPPED - Duplicate] {os.path.basename(filepath)}")
            return None
        unique_hashes.add(hashcode)

    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lat, lon = extract_location_header(lines)
    data_start = find_data_start(lines)

    if data_start is None:
        print(Fore.RED + f"[ERROR - No Header] {os.path.basename(filepath)}")
        return None

    try:
        df = pd.read_csv(filepath, skiprows=data_start)
    except Exception as e:
        print(Fore.RED + f"[ERROR - Read Fail] {os.path.basename(filepath)} → {e}")
        return None

    if 'YEAR' not in df.columns or 'DOY' not in df.columns:
        print(Fore.RED + f"[ERROR - Missing Columns] {os.path.basename(filepath)}")
        return None

    try:
        df["date"] = pd.to_datetime(df["YEAR"].astype(str) + df["DOY"].astype(str), format="%Y%j")
    except Exception as e:
        print(Fore.RED + f"[ERROR - Date Conversion] {os.path.basename(filepath)} → {e}")
        return None

    variables = ["WS10M_RANGE", "WD10M", "GWETTOP", "GWETROOT", "GWETPROF"]
    existing_vars = [var for var in variables if var in df.columns]
    melted = df.melt(id_vars=["date"], value_vars=existing_vars,
                     var_name="variable", value_name="value")

    melted["latitude"] = lat
    melted["longitude"] = lon
    melted["country"] = get_country_from_coords(lat, lon)

    print(Fore.GREEN + f"[OK] {os.path.basename(filepath)} → {len(melted)} rows")
    return melted

# 🏁 Démarrer le traitement
print(Style.BRIGHT + Fore.CYAN + "\n🚀 Lancement de la fusion météo africaine...\n")
files = [f for f in os.listdir(data_folder) if f.lower().endswith(".csv")]

for filename in tqdm(files, desc="📦 Traitement des fichiers"):
    filepath = os.path.join(data_folder, filename)
    result = process_file(filepath)
    if result is not None:
        records.append(result)

if records:
    final_df = pd.concat(records, ignore_index=True)
    output_path = "merged_weather_africa.csv"
    final_df.to_csv(output_path, index=False)
    print(Style.BRIGHT + Fore.GREEN + f"\n✅ Fusion terminée : {len(final_df)} lignes exportées vers {output_path}\n")
else:
    print(Style.BRIGHT + Fore.YELLOW + "\n⚠️ Aucun fichier valide traité.\n")
    print(world.columns)
