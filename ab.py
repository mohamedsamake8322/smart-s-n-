import os
import gzip
import csv
import rasterio
import numpy as np
from tqdm import tqdm  # pour la barre de progression

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

block_size = 512  # taille du bloc pour lecture par fenêtre

for tif_file in tif_files:
    input_path = os.path.join(input_dir, tif_file)
    output_path = os.path.join(output_dir, tif_file.replace(".tif", ".csv.gz"))

    print(f"\n🚀 Traitement de {tif_file}...")

    with rasterio.Env(num_threads=4):
        with rasterio.open(input_path) as src, gzip.open(output_path, 'wt', newline='') as gz_file:
            writer = csv.writer(gz_file)
            writer.writerow(["x", "y", "value"])

            total_rows, total_cols = src.height, src.width
            total_blocks = ((total_rows + block_size - 1) // block_size)

            # Barre de progression
            with tqdm(total=total_blocks, desc="📥 Lecture", unit="bloc") as pbar:
                for row_start in range(0, total_rows, block_size):
                    row_end = min(row_start + block_size, total_rows)
                    window = rasterio.windows.Window(0, row_start, total_cols, row_end - row_start)
                    data = src.read(1, window=window)

                    rows_to_write = []
                    for i in range(data.shape[0]):
                        for j in range(data.shape[1]):
                            val = data[i, j]
                            if np.isnan(val):  # ignorer les NaN
                                continue
                            x, y = src.xy(row_start + i, j)
                            rows_to_write.append([x, y, val])

                    writer.writerows(rows_to_write)
                    pbar.update(1)

    print(f"✅ Fichier terminé : {output_path}")
