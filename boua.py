import rasterio
import numpy as np
import gzip
import csv
import os

# 📂 Chemin du dossier contenant les fichiers
input_dir = r"C:\plateforme-agricole-complete-v2\WCres"
output_file = os.path.join(input_dir, "wcres_data.csv.gz")

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

# ⚡ Paramètre : taille du bloc (nombre de lignes par lecture)
block_size = 256

# ✍️ Écriture en flux compressé
with gzip.open(output_file, "wt", newline='') as gzfile:
    writer = csv.writer(gzfile)

    # Écrire l'entête
    header = ["x", "y"] + [os.path.splitext(f)[0] for f in tif_files]
    writer.writerow(header)

    # Lecture par blocs
    for start_row in range(0, height, block_size):
        end_row = min(start_row + block_size, height)

        # Lire le bloc dans chaque raster
        bands_block = [ds.read(1, window=((start_row, end_row), (0, width))) for ds in datasets]

        # Pour chaque ligne dans le bloc
        for row_offset in range(end_row - start_row):
            row_index = start_row + row_offset

            # Coordonnées et valeurs
            for col in range(width):
                x, y = datasets[0].transform * (col, row_index)
                values = [bands_block[i][row_offset, col] for i in range(len(datasets))]
                writer.writerow([x, y] + values)

        # 🔄 Affichage de la progression
        percent = ((end_row) / height) * 100
        print(f"Progression : {percent:.2f} % ({end_row}/{height} lignes)")

print(f"✅ Données exportées dans {output_file}")
