import os
import pandas as pd
from datetime import datetime
import hashlib

data_folder = r"C:\Users\moham\Music\weather_data_africa"
unique_hashes = set()
records = []

def get_country_from_coords(lat, lon):
    # 👇 Optional: You can use reverse geocoding if needed (geopy or a custom mapping)
    return "Unknown"

for filename in os.listdir(data_folder):
    filepath = os.path.join(data_folder, filename)
    if not filepath.endswith('.csv'):
        continue

    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        hashcode = hashlib.md5(content.encode()).hexdigest()
        if hashcode in unique_hashes:
            continue
        unique_hashes.add(hashcode)

    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Extract location from header
    lat = lon = None
    for line in lines:
        if "latitude" in line and "longitude" in line:
            parts = line.split()
            lat = float(parts[parts.index("latitude") + 1])
            lon = float(parts[parts.index("longitude") + 1])
            break

    # Read the data portion
    df = pd.read_csv(filepath, skiprows=len(lines) - len([l for l in lines if "YEAR" in l]))

    # Melt the dataframe
    df["date"] = df.apply(lambda row: datetime.strptime(f"{int(row.YEAR)}-{int(row.DOY)}", "%Y-%j").date(), axis=1)
    melted = df.melt(id_vars=["date"], value_vars=["WS10M_RANGE", "WD10M", "GWETTOP", "GWETROOT", "GWETPROF"],
                     var_name="variable", value_name="value")

    # Fill in metadata
    melted["latitude"] = lat
    melted["longitude"] = lon
    melted["country"] = get_country_from_coords(lat, lon)

    records.append(melted)

# Concatenate and export
final_df = pd.concat(records, ignore_index=True)
final_df.to_csv("merged_weather_africa.csv", index=False)
