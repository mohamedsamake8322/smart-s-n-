import pandas as pd
import os
from glob import glob

# 📁 Dossier contenant tous les fichiers CSV
input_folder = "weather_data_africa"
output_file = "weather_africa.csv"

# 📦 Collecte tous les fichiers .csv
csv_files = glob(os.path.join(input_folder, "*.csv"))

# 🔄 Dictionnaire : {clé_point: [fichiers]}
from collections import defaultdict
grouped_files = defaultdict(list)

for file in csv_files:
    # Extrait une clé unique : ex "Mali_10.1_-12.17"
    basename = os.path.basename(file)
    key = "_".join(basename.split("_")[:3])  # pays_lat_lon
    grouped_files[key].append(file)

# 🧬 Fusion des fichiers par point
combined_dfs = []

for key, files in grouped_files.items():
    merged = None

    for f in files:
        try:
            df = pd.read_csv(f, skiprows=9)  # 🚨 skip header
            df = df.loc[:, ~df.columns.str.contains("Unnamed")]  # nettoie
            if merged is None:
                merged = df
            else:
                merged = pd.merge(merged, df, on="DATE", how="outer")
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")
            continue

    if merged is not None and not merged.empty:
        # 🏷️ Ajoute info géographique
        lat = key.split("_")[1]
        lon = key.split("_")[2]
        country = key.split("_")[0]

        merged.insert(0, "Country", country)
        merged.insert(1, "Latitude", lat)
        merged.insert(2, "Longitude", lon)

        combined_dfs.append(merged)

# 📊 Fusion continentale
final_df = pd.concat(combined_dfs, ignore_index=True)

# 💾 Sauvegarde finale
final_df.to_csv(output_file, index=False)
print(f"✅ Fichier fusionné enregistré : {output_file}")
