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

# 📥 Ouvre les rasters en mode lecture
datasets = [rasterio.open(path) for path in tif_paths]

# ✅ Vérification que toutes les tailles correspondent
width, height = datasets[0].width, datasets[0].height
if not all(ds.width == width and ds.height == height for ds in datasets):
    raise ValueError("Tous les rasters doivent avoir les mêmes dimensions.")

print(f"📏 Dimensions : {width} x {height} pixels")
print(f"📦 Nombre de fichiers : {len(datasets)}")

# ✍️ Écriture en flux compressé
with gzip.open(output_file, "wt", newline='') as gzfile:
    writer = csv.writer(gzfile)

    # Écrire l'entête
    header = ["x", "y"] + [os.path.splitext(f)[0] for f in tif_files]
    writer.writerow(header)

    # Lecture ligne par ligne avec progression
    for row in range(height):
        # Lire la bande 1 de chaque fichier pour cette ligne
        bands_row = [ds.read(1, window=((row, row+1), (0, width)))[0] for ds in datasets]

        # Coordonnées géographiques pour chaque pixel de la ligne
        for col in range(width):
            x, y = datasets[0].transform * (col, row)
            values = [bands_row[i][col] for i in range(len(datasets))]
            writer.writerow([x, y] + values)

        # 🔄 Affichage de la progression
        if (row + 1) % 100 == 0 or row == height - 1:
            percent = ((row + 1) / height) * 100
            print(f"Progression : {percent:.2f} % ({row+1}/{height} lignes)")

print(f"✅ Données exportées dans {output_file}")
