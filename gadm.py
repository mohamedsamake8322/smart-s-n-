import os
import time
import dask.dataframe as dd
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import pyarrow as pa
import pyarrow.parquet as pq

# --- Paramètres ---
gadm_root = r"C:\plateforme-agricole-complete-v2\gadm"
input_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data.parquet"
output_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data_africa.parquet"

crs = "EPSG:4326"

# --- 1. Charger les frontières pays africains ---
print("🔍 Chargement des frontières pays africains...")
geojson_files = []
for country_dir in os.listdir(gadm_root):
    dir_path = os.path.join(gadm_root, country_dir)
    if os.path.isdir(dir_path):
        file_path = os.path.join(dir_path, "level0.geojson")
        if os.path.exists(file_path):
            geojson_files.append(file_path)

if not geojson_files:
    raise RuntimeError("Aucun fichier 'level0.geojson' trouvé dans gadm_root.")

gadm_list = []
for f in geojson_files:
    gdf = gpd.read_file(f)
    gadm_list.append(gdf[["COUNTRY", "GID_0", "geometry"]])
gadm_africa = gpd.GeoDataFrame(pd.concat(gadm_list, ignore_index=True), crs=crs)
print(f"🌍 {len(gadm_africa)} frontières chargées.")

# --- 2. Lire parquet en Dask ---
print("⏳ Lecture du parquet avec Dask...")
ddf = dd.read_parquet(input_parquet)

if os.path.exists(output_parquet):
    print(f"⚠️ Suppression du fichier de sortie existant : {output_parquet}")
    os.remove(output_parquet)

total_lines = 0
chunks_processed = 0
start_time = time.time()

# --- 3. Traitement par partition ---
for partition in ddf.to_delayed():
    df = partition.compute()
    df = df.dropna(subset=["x", "y"])

    # Conversion en GeoDataFrame
    gdf_chunk = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.x, df.y),
        crs=crs
    )

    # Jointure spatiale
    joined = gpd.sjoin(gdf_chunk, gadm_africa, how="inner", predicate="within")

    cols_to_keep = list(df.columns) + ["COUNTRY", "GID_0"]
    joined = joined[cols_to_keep]

    # Écriture parquet
    table = pa.Table.from_pandas(joined, preserve_index=False)

    if chunks_processed == 0:
        pq.write_table(table, output_parquet, compression="snappy")
    else:
        with pq.ParquetWriter(output_parquet, compression="snappy", use_dictionary=True, write_statistics=True, append=True) as writer:
            writer.write_table(table)

    total_lines += len(joined)
    chunks_processed += 1
    elapsed = time.time() - start_time
    print(f"Chunk {chunks_processed} traité - lignes écrites : {len(joined)} - total lignes : {total_lines} - temps écoulé : {elapsed:.1f}s")

print(f"✅ Traitement terminé. Fichier sauvegardé : {output_parquet}")
print(f"Nombre total de points en Afrique : {total_lines}")
