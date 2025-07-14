import os
import rasterio
import numpy as np
import csv

# 📁 Répertoire principal contenant les données GAEZ
base_path = r"C:\Users\moham\Music\2\Écarts de rendement et de production"
output_csv = "gaez_gap_extracted_stream.csv"

# ✍️ Créer le fichier CSV dès le départ
with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["x", "y", "value", "year", "category", "layer"])  # En-tête

    # 🔁 Parcours des sous-dossiers
    for category in os.listdir(base_path):
        cat_path = os.path.join(base_path, category)
        if not os.path.isdir(cat_path):
            continue

        for year in os.listdir(cat_path):
            year_path = os.path.join(cat_path, year)
            if not os.path.isdir(year_path):
                continue

            print(f"🔍 Traitement : {category}/{year}")

            for filename in os.listdir(year_path):
                if not filename.endswith(".tif"):
                    continue

                file_path = os.path.join(year_path, filename)
                try:
                    with rasterio.open(file_path) as src:
                        band = src.read(1)
                        transform = src.transform
                        nodata = src.nodata

                        # Masquer les valeurs invalides
                        mask = (band != nodata) & (~np.isnan(band))
                        rows, cols = np.where(mask)
                        xs, ys = rasterio.transform.xy(transform, rows, cols)

                        # Écrire ligne par ligne
                        for x, y, val in zip(xs, ys, band[rows, cols]):
                            writer.writerow([x, y, val, int(year), category, filename])

                except Exception as e:
                    print(f"❌ Erreur sur {file_path} : {e}")

print(f"✅ Terminé : les résultats sont dans {output_csv}")
