import os
import gzip
import csv
import rasterio # pyright: ignore[reportMissingImports]
import numpy as np

input_dir = "C:/plateforme-agricole-complete-v2/WCres"
output_dir = input_dir

tif_files = [
    "WCres_0-5cm_M_250m.tif",
    "WCres_5-15cm_M_250m.tif",
    "WCres_15-30cm_M_250m.tif",
    "WCres_30-60cm_M_250m.tif",
    "WCres_60-100cm_M_250m.tif",
    "WCres_100-200cm_M_250m.tif"
]

for tif_file in tif_files:
    input_path = os.path.join(input_dir, tif_file)
    output_path = os.path.join(output_dir, tif_file.replace(".tif", ".csv.gz"))

    print(f"\n🔄 Traitement de {tif_file}...")

    with rasterio.open(input_path) as src, gzip.open(output_path, 'wt', newline='') as gz_file:
        writer = csv.writer(gz_file)
        writer.writerow(["x", "y", "value"])  # En-tête CSV

        total_rows = src.height
        total_cols = src.width
        total_pixels = total_rows * total_cols

        block_size = 1000
        processed_pixels = 0

        for row_start in range(0, total_rows, block_size):
            row_end = min(row_start + block_size, total_rows)
            window = rasterio.windows.Window(0, row_start, total_cols, row_end - row_start)
            data = src.read(1, window=window)

            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    val = data[i, j]
                    x, y = src.xy(row_start + i, j)
                    writer.writerow([x, y, val])
                    processed_pixels += 1

            percent = (processed_pixels / total_pixels) * 100
            print(f"✅ Progression: {percent:.2f}%")

        print(f"📊 Pixels écrits: {processed_pixels} / {total_pixels}")
        if processed_pixels == total_pixels:
            print("✅ Intégrité confirmée : toutes les données ont été exportées.")
        else:
            print("⚠️ Attention : perte de données détectée !")

    print(f"✅ Fichier compressé écrit: {output_path}")
