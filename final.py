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
    if "_copy" in f:
        continue  # ⛔ Ignorer les duplicatas
    base = os.path.basename(f)
    key = "_".join(base.split("_")[:3])  # Country_Lat_Lon
    grouped_files[key].append(f)

combined_dfs = []

for key, files in grouped_files.items():
    merged = None

    for idx, f in enumerate(files):
        try:
            with open(f, "r", encoding="utf-8") as file:
                lines = file.readlines()
            header_idx = next(i for i, line in enumerate(lines) if line.startswith("YEAR"))
            df = pd.read_csv(f, skiprows=header_idx)

            # 📅 Créer colonne DATE
            df["DATE"] = df.apply(
                lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1),
                axis=1
            )
            df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")
            df.drop(["YEAR", "DOY"], axis=1, errors="ignore", inplace=True)

            # 🏷️ Renommer les colonnes pour éviter les conflits
            unique_id = f.split("_")[-1].replace(".csv", "")  # ex: "0.53"
            df = df.rename(columns={col: f"{col}_{unique_id}" for col in df.columns if col != "DATE"})

            # 🔗 Fusion horizontale
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

# 📊 Fusion finale continentale
if combined_dfs:
    final_df = pd.concat(combined_dfs, ignore_index=True)
    final_df.to_csv(output_file, index=False)
    print(f"✅ Fichier météo fusionné : {output_file} ({len(final_df)} lignes)")
else:
    print("⚠️ Aucun fichier n’a pu être fusionné.")
