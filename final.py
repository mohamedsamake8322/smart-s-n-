import pandas as pd
import os
from glob import glob
from datetime import datetime, timedelta
from collections import defaultdict

input_folder = "weather_data_africa"
output_folder = "weather_by_country"
os.makedirs(output_folder, exist_ok=True)

# Regroupe les fichiers par pays
country_groups = defaultdict(list)
for f in glob(os.path.join(input_folder, "*.csv")):
    base = os.path.basename(f)
    if "_copy" in base:
        continue  # Ignorer les duplicatas
    country = base.split("_")[0]
    country_groups[country].append(f)

for country, files in country_groups.items():
    grouped_files = defaultdict(list)

    # Regroupe par point (lat + lon)
    for f in files:
        key = "_".join(os.path.basename(f).split("_")[:3])
        grouped_files[key].append(f)

    country_dfs = []

    for key, file_list in grouped_files.items():
        merged = None

        for f in file_list:
            try:
                with open(f, "r", encoding="utf-8") as file:
                    lines = file.readlines()
                header_idx = next(i for i, line in enumerate(lines) if line.startswith("YEAR"))
                df = pd.read_csv(f, skiprows=header_idx)

                df["DATE"] = df.apply(
                    lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1),
                    axis=1
                )
                df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")
                df.drop(["YEAR", "DOY"], axis=1, errors="ignore", inplace=True)

                # Ajoute suffixe unique pour éviter les collisions
                suffix = os.path.splitext(os.path.basename(f))[0].split("_")[-1]
                df = df.rename(columns={col: f"{col}_{suffix}" for col in df.columns if col != "DATE"})

                if merged is None:
                    merged = df
                else:
                    merged = pd.merge(merged, df, on="DATE", how="outer")

            except Exception as e:
                print(f"❌ Failed to read {f}: {e}")
                continue

        if merged is not None and not merged.empty:
            c, lat, lon = key.split("_")
            merged.insert(0, "Country", c)
            merged.insert(1, "Latitude", lat)
            merged.insert(2, "Longitude", lon)
            country_dfs.append(merged)

    # Fusionner tous les points du pays
    if country_dfs:
        final = pd.concat(country_dfs, ignore_index=True)
        out_path = os.path.join(output_folder, f"weather_{country}.csv")
        final.to_csv(out_path, index=False)
        print(f"✅ Fusion {country} : {out_path} ({len(final)} lignes)")
    else:
        print(f"⚠️ Aucun point valide pour {country}")
