import rasterio
import pandas as pd
import gzip
import os

def convert_tif_to_csv_gz(tif_path, output_path):
    with rasterio.open(tif_path) as src:
        band = src.read(1)
        transform = src.transform
        nodata = src.nodata

        rows, cols = band.shape
        data = []

        for row in range(rows):
            for col in range(cols):
                value = band[row, col]
                if nodata is not None and value == nodata:
                    continue
                lon, lat = transform * (col, row)
                data.append((lon, lat, value))

    df = pd.DataFrame(data, columns=["longitude", "latitude", "value"])
    with gzip.open(output_path, 'wt', encoding='utf-8') as f:
        df.to_csv(f, index=False)
    print(f"✅ Saved: {output_path}")

# 📁 Dossiers
input_dir = "C:/plateforme-agricole-complete-v2/WCres"
output_dir = "C:/plateforme-agricole-complete-v2/Bouadata"
os.makedirs(output_dir, exist_ok=True)  # crée le dossier si nécessaire

# 📄 Liste des fichiers à traiter
tif_files = [
    "WCres_0-5cm_M_250m.tif",
    "WCres_5-15cm_M_250m.tif",
    "WCres_15-30cm_M_250m.tif",
    "WCres_30-60cm_M_250m.tif",
    "WCres_60-100cm_M_250m.tif",
    "WCres_100-200cm_M_250m.tif"
]

# 🔁 Conversion en boucle
for tif_file in tif_files:
    tif_path = os.path.join(input_dir, tif_file)
    output_name = tif_file.replace(".tif", ".csv.gz")
    output_path = os.path.join(output_dir, output_name)
    convert_tif_to_csv_gz(tif_path, output_path)
