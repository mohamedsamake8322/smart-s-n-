import rasterio
import csv
import gzip
import os

def convert_tif_to_csv_gz_stream_progress(tif_path, output_path, window_size=1024, print_every_percent=5):
    print(f"Démarrage conversion : {tif_path}")
    with rasterio.open(tif_path) as src, gzip.open(output_path, 'wt', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["longitude", "latitude", "value"])  # header

        transform = src.transform
        nodata = src.nodata
        width = src.width
        height = src.height

        total_pixels = width * height
        processed_pixels = 0
        next_print = print_every_percent  # prochaine étape à afficher en %

        for top in range(0, height, window_size):
            for left in range(0, width, window_size):
                win_width = min(window_size, width - left)
                win_height = min(window_size, height - top)
                window = rasterio.windows.Window(left, top, win_width, win_height)
                band = src.read(1, window=window)

                for row in range(band.shape[0]):
                    for col in range(band.shape[1]):
                        value = band[row, col]
                        processed_pixels += 1
                        if nodata is not None and value == nodata:
                            continue
                        global_col = left + col
                        global_row = top + row
                        lon, lat = transform * (global_col, global_row)
                        writer.writerow([lon, lat, value])

                progress = processed_pixels / total_pixels * 100
                if progress >= next_print:
                    print(f"Progression : {progress:.0f} %")
                    next_print += print_every_percent

        print(f"✅ Conversion terminée et sauvegardée : {output_path}")


# Partie principale
if __name__ == "__main__":
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
        tif_path = os.path.join(input_dir, tif_file)
        output_name = tif_file.replace(".tif", ".csv.gz")
        output_path = os.path.join(output_dir, output_name)
        convert_tif_to_csv_gz_stream_progress(tif_path, output_path)
