import os
import rasterio
import pandas as pd
import numpy as np

# 📁 Chemin vers le dossier contenant tous les .tif (à adapter)
base_path = r"C:\Users\moham\Music\2\Écarts de rendement et de production"

# 📂 Structure attendue : base_path\{Category}\{Year}\*.tif
output_csv = "gaez_gap_extracted.csv"

records = []

for category in os.listdir(base_path):
    cat_path = os.path.join(base_path, category)
    if not os.path.isdir(cat_path):
        continue

    for year in os.listdir(cat_path):
        year_path = os.path.join(cat_path, year)
        if not os.path.isdir(year_path):
            continue

        print(f"🔍 Traitement : {category}/{year}")

        for filename in os.listdir(year_path):
            if not filename.endswith(".tif"):
                continue

            file_path = os.path.join(year_path, filename)

            try:
                with rasterio.open(file_path) as src:
                    band = src.read(1)
                    transform = src.transform
                    nodata = src.nodata

                    # Masque des pixels valides
                    mask = (band != nodata) & (~np.isnan(band))
                    rows, cols = np.where(mask)
                    xs, ys = rasterio.transform.xy(transform, rows, cols)

                    # Stocker les données valides
                    for x, y, val in zip(xs, ys, band[rows, cols]):
                        records.append({
                            "x": x,
                            "y": y,
                            "value": val,
                            "year": int(year),
                            "category": category,
                            "layer": filename
                        })

            except Exception as e:
                print(f"❌ Erreur fichier {file_path} : {e}")

# 💾 Sauvegarde en CSV
df = pd.DataFrame(records)
df.to_csv(output_csv, index=False)
print(f"✅ Export terminé : {output_csv} ({len(df)} lignes)")
