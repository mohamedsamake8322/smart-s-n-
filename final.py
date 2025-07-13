import pandas as pd
import os
from glob import glob
from datetime import datetime, timedelta

input_folder = "weather_data_africa"
output_file = "weather_africa.csv"

from collections import defaultdict
grouped_files = defaultdict(list)

# 🔍 Indexer tous les fichiers par point
for f in glob(os.path.join(input_folder, "*.csv")):
    key = "_".join(os.path.basename(f).split("_")[:3])
    grouped_files[key].append(f)

combined_dfs = []

for key, files in grouped_files.items():
    merged = None

    for f in files:
        try:
            # 🔎 Trouver l’index du header YEAR,DOY,...
            with open(f, "r", encoding="utf-8") as file:
                lines = file.readlines()
            header_idx = next(i for i, line in enumerate(lines) if line.startswith("YEAR"))
            df = pd.read_csv(f, skiprows=header_idx)

            # 🕒 Ajouter colonne DATE
            df["DATE"] = df.apply(
                lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1),
                axis=1
            )
            df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

            df.drop(["YEAR", "DOY"], axis=1, inplace=True)

            if merged is None:
                merged = df
            else:
                merged = pd.merge(merged, df, on="DATE", how="outer")

        except Exception as e:
            print(f"❌ Failed to read {f}: {e}")
            continue

    if merged is not None and not merged.empty:
        country, lat, lon = key.split("_")
        merged.insert(0, "Country", country)
        merged.insert(1, "Latitude", lat)
        merged.insert(2, "Longitude", lon)
        combined_dfs.append(merged)

# 📊 Fusion continentale
final_df = pd.concat(combined_dfs, ignore_index=True)
final_df.to_csv(output_file, index=False)
print(f"✅ Fusion terminée : {output_file}")
