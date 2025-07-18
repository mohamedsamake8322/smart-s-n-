import os
import pandas as pd
from datetime import datetime
import hashlib

# Dossier contenant les fichiers
data_folder = r"C:\Users\moham\Music\weather_data_africa"
unique_hashes = set()
records = []

def get_country_from_coords(lat, lon):
    # TODO: Remplacer par un vrai lookup si tu veux, ici on laisse "Unknown"
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
    # Vérifie doublons avec hash
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        hashcode = hashlib.md5(content.encode()).hexdigest()
        if hashcode in unique_hashes:
            return None
        unique_hashes.add(hashcode)

    # Lire le fichier ligne par ligne
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    lat, lon = extract_location_header(lines)
    data_start = find_data_start(lines)

    if data_start is None:
        print(f"⛔ Données non trouvées dans {filepath}")
        return None

    # Charger les données
    df = pd.read_csv(filepath, skiprows=data_start)

    if 'YEAR' not in df.columns or 'DOY' not in df.columns:
        print(f"❌ Colonnes manquantes dans {filepath}")
        return None

    # Transformer YEAR+DOY en date
    df["date"] = pd.to_datetime(df["YEAR"].astype(str) + df["DOY"].astype(str), format="%Y%j")

    # Convertir en format long (melt)
    variables = ["WS10M_RANGE", "WD10M", "GWETTOP", "GWETROOT", "GWETPROF"]
    existing_vars = [var for var in variables if var in df.columns]
    melted = df.melt(id_vars=["date"], value_vars=existing_vars,
                     var_name="variable", value_name="value")

    # Ajouter les métadonnées
    melted["latitude"] = lat
    melted["longitude"] = lon
    melted["country"] = get_country_from_coords(lat, lon)

    return melted

# Traitement principal
print("🚀 Fusion des fichiers météo en cours...")
for filename in os.listdir(data_folder):
    if not filename.lower().endswith(".csv"):
        continue
    filepath = os.path.join(data_folder, filename)
    result = process_file(filepath)
    if result is not None:
        records.append(result)

# Compilation finale
if records:
    final_df = pd.concat(records, ignore_index=True)
    final_df.to_csv("merged_weather_africa.csv", index=False)
    print(f"✅ Fusion terminée : {len(final_df)} lignes exportées vers merged_weather_africa.csv")
else:
    print("⚠️ Aucun fichier valide trouvé.")
