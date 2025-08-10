import rasterio
import numpy as np
import os
import pandas as pd
from multiprocessing import Pool, cpu_count

# 📂 Chemin du dossier contenant les fichiers
input_dir = r"C:\plateforme-agricole-complete-v2\WCres"
output_file = os.path.join(input_dir, "wcres_data.parquet")

# 📄 Liste des fichiers TIF
tif_files = [
    "WCres_0-5cm_M_250m.tif",
    "WCres_5-15cm_M_250m.tif",
    "WCres_15-30cm_M_250m.tif",
    "WCres_30-60cm_M_250m.tif",
    "WCres_60-100cm_M_250m.tif",
    "WCres_100-200cm_M_250m.tif"
]
tif_paths = [os.path.join(input_dir, f) for f in tif_files]

# 📥 Ouvre les rasters
datasets = [rasterio.open(path) for path in tif_paths]

# ✅ Vérification dimensions identiques
width, height = datasets[0].width, datasets[0].height
if not all(ds.width == width and ds.height == height for ds in datasets):
    raise ValueError("Tous les rasters doivent avoir les mêmes dimensions.")

print(f"📏 Dimensions : {width} x {height} pixels")
print(f"📦 Nombre de fichiers : {len(datasets)}")
print(f"💻 CPU utilisés : {cpu_count()}")

# ⚡ Paramètre : taille du bloc (lignes à la fois)
block_size = 256

# Fonction pour traiter un bloc de lignes
def process_block(start_row):
    end_row = min(start_row + block_size, height)
    bands_block = [ds.read(1, window=((start_row, end_row), (0, width))) for ds in datasets]

    rows_data = []
    for row_offset in range(end_row - start_row):
        row_index = start_row + row_offset
        for col in range(width):
            x, y = datasets[0].transform * (col, row_index)
            values = [bands_block[i][row_offset, col] for i in range(len(datasets))]
            rows_data.append((x, y, *values))

    return pd.DataFrame(rows_data, columns=["x", "y"] + [os.path.splitext(f)[0] for f in tif_files])

# 📊 Lecture + écriture Parquet par blocs
blocks = list(range(0, height, block_size))
total_blocks = len(blocks)

first_chunk = True
for idx, df in enumerate(Pool(cpu_count()).imap(process_block, blocks), start=1):
    df.to_parquet(
        output_file,
        engine="pyarrow",
        compression="snappy",
        index=False,
        append=not first_chunk
    )
    first_chunk = False
    print(f"Progression : {idx}/{total_blocks} blocs ({(idx/total_blocks)*100:.2f}%)")

print(f"✅ Données exportées dans {output_file}")
