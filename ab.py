import os
import gzip
import csv
import rasterio
import numpy as np
from tqdm import tqdm  # barre de progression

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

block_size = 512  # taille du bloc pour lecture

for tif_file in tif_files:
    input_path = os.path.join(input_dir, tif_file)
    output_path = os.path.join(output_dir, tif_file.replace(".tif", ".csv.gz"))

    print(f"\n🚀 Traitement de {tif_file}...")

    with rasterio.Env(num_threads=4):
        with rasterio.open(input_path) as src, gzip.open(output_path, 'wt', newline='') as gz_file:
            writer = csv.writer(gz_file)
            writer.writerow(["x", "y", "value"])

            total_rows, total_cols = src.height, src.width
            total_blocks = (total_rows + block_size - 1) // block_size

            with tqdm(total=total_rows, desc="📥 Lecture (lignes)", unit="ligne") as pbar:
                for row_start in range(0, total_rows, block_size):
                    row_end = min(row_start + block_size, total_rows)
                    window_height = row_end - row_start

                    window = rasterio.windows.Window(0, row_start, total_cols, window_height)
                    data = src.read(1, window=window)

                    nodata = src.nodata
                    if nodata is None:
                        mask_valid = ~np.isnan(data)
                    else:
                        mask_valid = data != nodata

                    # Indices valides
                    valid_indices = np.where(mask_valid)
                    if valid_indices[0].size == 0:
                        pbar.update(window_height)
                        continue

                    rows_idx = valid_indices[0]
                    cols_idx = valid_indices[1]

                    # Calculer coordonnées x,y pour tous les pixels valides
                    xs, ys = src.xy(row_start + rows_idx, cols_idx)

                    # Préparer lignes à écrire
                    rows_to_write = zip(xs, ys, data[rows_idx, cols_idx])

                    # Écrire dans le csv
                    writer.writerows(rows_to_write)

                    pbar.update(window_height)

    print(f"✅ Fichier terminé : {output_path}")
