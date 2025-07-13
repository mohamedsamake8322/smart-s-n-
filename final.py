import pandas as pd
import os
from glob import glob
from datetime import datetime, timedelta
from collections import defaultdict

# 📁 Dossier contenant les fichiers .csv météo
input_folder = "weather_data_africa"
output_file = "weather_africa.csv"

# 📦 Collecte tous les fichiers .csv
csv_files = glob(os.path.join(input_folder, "*.csv"))

# 🔄 Groupe les fichiers par point : pays_lat_lon
grouped_files = defaultdict(list)
for f in csv_files:
    key = "_".join(os.path.basename(f).split("_")[:3])  # Pays_Lat_Lon
    grouped_files[key].append(f)

combined_dfs = []

for key, files in grouped_files.items():
    merged = None

    for f in files:
        try:
            # 🧠 Détection de l'index du header 'YEAR,DOY,...'
            with open(f, "r", encoding="utf-8") as file:
                lines = file.readlines()
            header_idx = next(i for i, line in enumerate(lines) if line.startswith("YEAR"))

            # 📥 Lecture du fichier
            df = pd.read_csv(f, skiprows=header_idx)

            # 📅 Conversion YEAR + DOY → DATE
            df["DATE"] = df.apply(
                lambda row: datetime(int(row["YEAR"]), 1, 1) + timedelta(days=int(row["DOY"]) - 1),
                axis=1
            )
            df["DATE"] = df["DATE"].dt.strftime("%Y-%m-%d")

            # 🧹 Nettoyage
            df.drop(["YEAR", "DOY"], axis=1, errors="ignore", inplace=True)
            df = df.loc[:, ~df.columns.duplicated()]

            # 📌 Fusion horizontale
            if merged is None:
                merged = df
            else:
                merged = pd.merge(
                    merged, df, on="DATE", how="outer", suffixes=("", None)
                )

        except Exception as e:
            print(f"❌ Failed to read {f}: {e}")
            continue

    # 📦 Ajout des infos géographiques
    if merged is not None and not merged.empty:
        country, lat, lon = key.split("_")
        merged.insert(0, "Country", country)
        merged.insert(1, "Latitude", lat)
        merged.insert(2, "Longitude", lon)
        combined_dfs.append(merged)

# 🧬 Fusion finale continentale
if combined_dfs:
    final_df = pd.concat(combined_dfs, ignore_index=True)
    final_df.to_csv(output_file, index=False)
    print(f"✅ Fichier météo fusionné : {output_file} ({len(final_df)} lignes)")
else:
    print("⚠️ Aucun fichier valide n’a été fusionné.")
