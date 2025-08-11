import os
import time
import dask.dataframe as dd
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import pyarrow as pa
import pyarrow.parquet as pq

# Paramètres
gadm_root = r"C:\plateforme-agricole-complete-v2\gadm"
input_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data.parquet"
output_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data_africa.parquet"
crs = "EPSG:4326"

# Charger frontières africaines
print("🔍 Chargement frontières pays africains...")
geojson_files = []
for country_dir in os.listdir(gadm_root):
    dir_path = os.path.join(gadm_root, country_dir)
    if os.path.isdir(dir_path):
        file_path = os.path.join(dir_path, "level0.geojson")
        if os.path.exists(file_path):
            geojson_files.append(file_path)

gadm_list = []
for f in geojson_files:
    gdf = gpd.read_file(f)
    gadm_list.append(gdf[["COUNTRY", "GID_0", "geometry"]])
gadm_africa = gpd.GeoDataFrame(pd.concat(gadm_list, ignore_index=True), crs=crs)
gadm_africa.sindex  # construction index spatial
print(f"🌍 {len(gadm_africa)} frontières chargées.")

# Calcul bbox étendue
minx, miny, maxx, maxy = gadm_africa.total_bounds
buffer = 1.0
bbox = (minx - buffer, miny - buffer, maxx + buffer, maxy + buffer)

# Supprimer fichier sortie s'il existe
if os.path.exists(output_parquet):
    os.remove(output_parquet)

# Lire parquet Dask
ddf = dd.read_parquet(input_parquet)
total_partitions = ddf.npartitions
print(f"⏳ {total_partitions} partitions à traiter...")

total_lines = 0
chunks_processed = 0
start_time = time.time()

writer = None

for i, partition in enumerate(ddf.to_delayed()):
    try:
        df = partition.compute()
        df = df.dropna(subset=["x", "y"])

        # Filtre simple Afrique (longitude -20 à 60, latitude -40 à 40)
        df = df[(df.x >= -20) & (df.x <= 60) & (df.y >= -40) & (df.y <= 40)]
        if df.empty:
            print(f"Partition {i+1}/{total_partitions} : Aucun point dans la zone Afrique approximative, sautée.")
            continue

        # Conversion en GeoDataFrame
        gdf_chunk = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.x, df.y),
            crs=crs
        )

        # Jointure spatiale avec polygones Afrique
        joined = gpd.sjoin(gdf_chunk, gadm_africa, how="inner", predicate="within")
        if joined.empty:
            print(f"Partition {i+1}/{total_partitions} : Aucun point après jointure spatiale, sautée.")
            continue

        # Colonnes à garder
        cols_to_keep = list(df.columns) + ["COUNTRY", "GID_0"]
        joined = joined[cols_to_keep]

        # Écriture dans fichier parquet en append
        table = pa.Table.from_pandas(joined, preserve_index=False)
        if writer is None:
            writer = pq.ParquetWriter(output_parquet, compression="snappy", use_dictionary=True, write_statistics=True)
        writer.write_table(table)

        total_lines += len(joined)
        chunks_processed += 1
        elapsed = time.time() - start_time
        pct = (i + 1) / total_partitions * 100
        speed = total_lines / elapsed if elapsed > 0 else 0

        print(f"Partition {i+1}/{total_partitions} traité - "
              f"Lignes écrites : {len(joined)} - Total lignes : {total_lines} - "
              f"Progression : {pct:.2f}% - Temps écoulé : {elapsed:.1f}s - "
              f"Vitesse : {speed:.2f} lignes/s")

    except Exception as e:
        print(f"⚠️ Erreur sur partition {i+1} : {e}")
        continue

if writer is not None:
    writer.close()

print(f"✅ Traitement terminé. Fichier sauvegardé : {output_parquet}")
print(f"Nombre total de points africains : {total_lines}")
