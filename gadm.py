import os
import glob
import time
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import pyarrow.parquet as pq

# --- Paramètres ---
gadm_root = r"C:\plateforme-agricole-complete-v2\gadm"
input_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data.parquet"
output_parquet = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data_africa.parquet"

chunk_size = 500_000  # adapte selon ta RAM (500k lignes par chunk)
crs = "EPSG:4326"  # coord système latitude/longitude WGS84

# --- 1. Charger et fusionner les frontières pays africains (niveau 0) ---
print("🔍 Recherche fichiers GADM africains niveau 0...")
geojson_files = []
for country_dir in os.listdir(gadm_root):
    dir_path = os.path.join(gadm_root, country_dir)
    if os.path.isdir(dir_path):
        files = glob.glob(os.path.join(dir_path, "*_0.geojson"))
        geojson_files.extend(files)

print(f"⚙️ {len(geojson_files)} fichiers trouvés.")

gadm_list = []
for f in geojson_files:
    gdf = gpd.read_file(f)
    gadm_list.append(gdf[["COUNTRY", "GID_0", "geometry"]])  # garder juste l'essentiel

gadm_africa = gpd.GeoDataFrame(pd.concat(gadm_list, ignore_index=True), crs=crs)
print(f"🌍 GeoDataFrame Afrique fusionné, {len(gadm_africa)} polygones.")

# --- 2. Préparer l'écriture du fichier final ---
if os.path.exists(output_parquet):
    print("⚠️ Le fichier de sortie existe déjà. Suppression...")
    os.remove(output_parquet)

# --- 3. Lecture et traitement par chunks ---
print("⏳ Traitement des données WCsat par chunks...")

reader = pd.read_parquet(input_parquet, engine="pyarrow", chunksize=chunk_size)

total_lines = 0
chunks_processed = 0
start_time = time.time()

for chunk in reader:
    # Conversion en GeoDataFrame
    chunk = chunk.dropna(subset=["x", "y"])  # enlever points sans coord
    gdf_chunk = gpd.GeoDataFrame(
        chunk,
        geometry=gpd.points_from_xy(chunk.x, chunk.y),
        crs=crs
    )

    # Spatial join pour trouver le pays
    joined = gpd.sjoin(gdf_chunk, gadm_africa, how="inner", predicate="within")

    # On garde uniquement les colonnes d'origine + COUNTRY et GID_0
    cols_to_keep = list(chunk.columns) + ["COUNTRY", "GID_0"]
    joined = joined[cols_to_keep]

    # Écrire en mode append dans le fichier parquet
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
