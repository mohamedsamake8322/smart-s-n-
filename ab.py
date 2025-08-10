import rasterio
import pandas as pd
import gzip
import os

def convert_tif_to_csv_gz(tif_path, output_path, window_size=1024):
    with rasterio.open(tif_path) as src:
        transform = src.transform
        nodata = src.nodata
        width = src.width
        height = src.height

        data = []

        # Lire par fenêtres de taille window_size x window_size
        for top in range(0, height, window_size):
            for left in range(0, width, window_size):
                win_width = min(window_size, width - left)
                win_height = min(window_size, height - top)
                window = rasterio.windows.Window(left, top, win_width, win_height)
                band = src.read(1, window=window)

                for row in range(band.shape[0]):
                    for col in range(band.shape[1]):
                        value = band[row, col]
                        if nodata is not None and value == nodata:
                            continue
                        # coordonnée dans l'image globale
                        global_col = left + col
                        global_row = top + row
                        lon, lat = transform * (global_col, global_row)
                        data.append((lon, lat, value))

        # Convertir en DataFrame et sauver compressé
        df = pd.DataFrame(data, columns=["longitude", "latitude", "value"])
        with gzip.open(output_path, 'wt', encoding='utf-8') as f:
            df.to_csv(f, index=False)
        print(f"✅ Saved: {output_path}")

# Dossier d'entrée/sortie
input_dir = "C:/plateforme-agricole-complete-v2/WCres"
output_dir = input_dir  # tu peux changer si besoin

tif_files = [
    "WCres_0-5cm_M_250m.tif",
    "WCres_5-15cm_M_250m.tif",
    "WCres_15-30cm_M_250m.tif",
    "WCres_30-60cm_M_250m.tif",
    "WCres_60-100cm_M_250m.tif",
    "WCres_100-200cm_M_250m.tif"
]

for tif_file in tif_files:
    tif_path = os.path.join(input_dir, tif_file)
    output_name = tif_file.replace(".tif", ".csv.gz")
    output_path = os.path.join(output_dir, output_name)
    convert_tif_to_csv_gz(tif_path, output_path)
