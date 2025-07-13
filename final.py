import pandas as pd
import os
from glob import glob
from datetime import datetime, timedelta
from collections import defaultdict

input_folder = "weather_data_africa"
output_file = "weather_africa.csv"

# 🔄 Grouper les fichiers par point
grouped_files = defaultdict(list)
for f in glob(os.path.join(input_folder, "*.csv")):
    base = os.path.basename(f).replace("_copy1", "")  # ignore les doublons
    key = "_".join(base.split("_")[:3])  # Country_Lat_Lon
    grouped_files[key].append(f)

combined_dfs = []

for key, files in grouped_files.items():
    merged = None

    for f in files:
        try:
            # 🔍 Localiser l'index du vrai header
            with open(f, "r", encoding="utf-8") as file:
                lines = file.readlines()
            header_idx = next(i for i, line in enumerate(lines) if line.startswith("YEAR"))

            df = pd.read_csv(f, skiprows=header_idx)
            df["DATE"] = df.apply(lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1), axis=1)
            df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")
            df.drop(["YEAR", "DOY"], axis=1, errors="ignore", inplace=True)

            # ➕ Ajouter suffix basé sur nom du fichier pour éviter les doublons
            suffix = os.path.splitext(os.path.basename(f))[0].split("_")[-1]
            df = df.add_suffix(f"_{suffix}")
            df.rename(columns={f"DATE_{suffix}": "DATE"}, inplace=True)

            # 🔗 Fusion avec les précédents
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

# 📦 Fusion continentale
if combined_dfs:
    final_df = pd.concat(combined_dfs, ignore_index=True)
    final_df.to_csv(output_file, index=False)
    print(f"✅ Fichier météo fusionné enregistré : {output_file} ({len(final_df)} lignes)")
else:
    print("⚠️ Aucun fichier valide n’a été fusionné.")
