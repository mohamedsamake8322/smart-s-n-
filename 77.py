import os
import rasterio
import pandas as pd
from tqdm import tqdm

# 📁 Chemin du dossier GAEZ Thème 6
base_path = r"C:\Users\moham\Music\2\Écarts de rendement et de production"

# 📋 Initialisation liste pour collecter les données
records = []

# 🔁 Parcours des sous-dossiers
for category in ["I", "R", "T", "V"]:
    for year in ["2000", "2010"]:
        folder_path = os.path.join(base_path, category, year)
        if not os.path.exists(folder_path):
            continue

        # 🔁 Parcours des fichiers .tif
        for filename in tqdm(os.listdir(folder_path), desc=f"{category}/{year}"):
            if filename.endswith(".tif"):
                file_path = os.path.join(folder_path, filename)
                with rasterio.open(file_path) as src:
                    band = src.read(1)
                    transform = src.transform

                    for row in range(band.shape[0]):
                        for col in range(band.shape[1]):
                            value = band[row, col]
                            if value != src.nodata and value is not None:
                                x, y = transform * (col, row)
                                records.append({
                                    "x": x,
                                    "y": y,
                                    "value": value,
                                    "year": int(year),
                                    "category": category,
                                    "layer": filename
                                })

# 📄 Conversion en DataFrame et export
df = pd.DataFrame(records)
df.to_csv("gaez_yield_gap_data.csv", index=False, encoding="utf-8")
print("✅ Données exportées dans gaez_yield_gap_data.csv")
