# streaming_to_parquet.py
import os
import time
import math
import numpy as np
import rasterio
import pyarrow as pa
import pyarrow.parquet as pq

# ---------- paramètres ----------
input_dir = r"C:\plateforme-agricole-complete-v2\WCsat"
tif_files = [
    "WCsat_0-5cm_M_250m.tif"
]
tif_paths = [os.path.join(input_dir, f) for f in tif_files]
output_file = os.path.join(input_dir, "wcsat_0-5com_data.parquet")

# objectif de taille de chunk en nombre de pixels (ajuste si besoin)
TARGET_PIXELS_PER_CHUNK = 2_000_000

# si True, on supprime les lignes où TOUTES les bandes sont nodata -> réduit fortement la taille
FILTER_ROWS_WITH_ALL_NODATA = True
# --------------------------------

# -> ouvrir rasters (dans le même process)
datasets = [rasterio.open(p) for p in tif_paths]

# vérif dims identiques
width, height = datasets[0].width, datasets[0].height
if not all(ds.width == width and ds.height == height for ds in datasets):
    raise ValueError("Tous les rasters doivent avoir les mêmes dimensions.")

print(f"📏 Dimensions : {width} x {height} pixels")
print(f"📦 Nombre de fichiers : {len(datasets)}")
print(f"🧭 Target pixels/chunk : {TARGET_PIXELS_PER_CHUNK}")

# calcule lignes par chunk de façon adaptative
rows_per_chunk = max(1, int(TARGET_PIXELS_PER_CHUNK // width))
print(f"⚙️ Rows per chunk : {rows_per_chunk}")

# helper pour obtenir les nodata pour chaque raster
nodata_values = [ds.nodatavals[0] if ds.nodatavals is not None else ds.nodata for ds in datasets]

# création du writer Parquet (on l'initialise au premier chunk)
writer = None
processed_rows = 0
start_time = time.time()

try:
    for start_row in range(0, height, rows_per_chunk):
        end_row = min(start_row + rows_per_chunk, height)
        num_rows = end_row - start_row
        n_points = num_rows * width

        # lire le chunk (shape: num_rows x width)
        bands = [ds.read(1, window=((start_row, end_row), (0, width))) for ds in datasets]

        # aplatir en vecteur (ordre C : ligne-major) => correspond au maillage row-major
        flat_bands = [b.ravel() for b in bands]

        # indices de ligne/col pour chaque pixel (1D)
        cols_idx = np.tile(np.arange(width, dtype=np.int64), num_rows)
        rows_idx = np.repeat(np.arange(start_row, end_row, dtype=np.int64), width)

        # obtenir coords X,Y (vectorisé)
        xs, ys = rasterio.transform.xy(datasets[0].transform, rows_idx, cols_idx, offset='center')
        xs = np.array(xs, dtype=np.float64)
        ys = np.array(ys, dtype=np.float64)

        # construire dict de colonnes
        data = {
            "x": xs,
            "y": ys
        }
        for i, name in enumerate([os.path.splitext(f)[0] for f in tif_files]):
            # convertir en float32 pour gagner de la place (adapter si besoin)
            data[name] = flat_bands[i].astype(bands[i].dtype)


        # filtrage nodata (optionnel) : garder lignes où AU MOINS une bande est valide
        if FILTER_ROWS_WITH_ALL_NODATA:
            valid_masks = []
            for i, arr in enumerate([data[n] for n in list(data.keys())[2:]]):  # skip x,y
                nod = nodata_values[i]
                if nod is None:
                    # on considère NaN comme nodata s'il y en a
                    valid = ~np.isnan(arr)
                else:
                    # nodata peut être int/float
                    valid = arr != nod
                valid_masks.append(valid)
            # mask = True si au moins une bande valide
            mask_any_valid = np.logical_or.reduce(valid_masks)
            keep_count = mask_any_valid.sum()
            if keep_count == 0:
                # rien à écrire pour ce chunk
                processed_rows += num_rows
                pct = (processed_rows / height) * 100
                print(f"Chunk {start_row}-{end_row} : 0 lignes valides (progress {pct:.2f}%)")
                continue

            # réduire chaque colonne
            for k in list(data.keys()):
                data[k] = data[k][mask_any_valid]

        # convertir en Table PyArrow
        table = pa.table(data)

        # initialiser writer si premier chunk
        if writer is None:
            writer = pq.ParquetWriter(output_file, table.schema, compression='snappy')

        writer.write_table(table)

        processed_rows += num_rows
        pct = (processed_rows / height) * 100
        elapsed = time.time() - start_time
        speed_rows_per_s = processed_rows / elapsed if elapsed > 0 else 0
        print(f"Chunk {start_row}-{end_row} ({table.num_rows} lignes écrites) — Progression : {pct:.2f}% — {speed_rows_per_s:.2f} rows/s")

finally:
    if writer is not None:
        writer.close()
    # fermer datasets
    for ds in datasets:
        ds.close()

total_time = time.time() - start_time
print(f"✅ Terminé en {total_time:.1f}s. Fichier : {output_file}")
