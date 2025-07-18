import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import BallTree
import numpy as np

# 📥 1. Charger les données
print("📥 Chargement des fichiers...")
gdf_soil = gpd.read_file("isdasoil_points.geojson")
df_meteo = pd.read_csv("merged_weather_africa.csv")
df_inputs = pd.read_csv("indicateurs_agronomiques_FAOSTAT.csv")

print(f"✅ Points iSDAsoil : {len(gdf_soil)}")
print(f"✅ Données météo : {len(df_meteo)} lignes")
print(f"✅ Indicateurs FAOSTAT : {len(df_inputs)} lignes\n")

# 🧭 2. Appariement météo → sol
print("🧭 Association géographique météo ↔ sol par BallTree...")
soil_coords = np.deg2rad(gdf_soil[['latitude', 'longitude']].values)
weather_coords = np.deg2rad(df_meteo[['latitude', 'longitude']].values)
tree = BallTree(soil_coords, metric='haversine')
dist, idx = tree.query(weather_coords, k=1)

df_meteo['soil_index'] = idx.flatten()
df_meteo['distance_km'] = dist.flatten() * 6371
print(f"📏 Appariement effectué. Points trop éloignés filtrés (>50km)...")

df_meteo_filtered = df_meteo[df_meteo['distance_km'] <= 50]
print(f"✅ Points conservés après filtrage : {len(df_meteo_filtered)} / {len(df_meteo)}\n")

# 🔗 3. Fusion météo + sol
print("🔗 Fusion météo + caractéristiques du sol...")
gdf_soil = gdf_soil.reset_index()
df_meteo_joined = df_meteo_filtered.merge(gdf_soil, left_on='soil_index', right_on='index')
print(f"✅ Fusion météo-sol : {len(df_meteo_joined)} lignes\n")

# 📊 4. Ajout des indicateurs FAOSTAT
print("📊 Ajout des indicateurs FAOSTAT (par pays + année)...")
df_meteo_joined['year'] = pd.to_datetime(df_meteo_joined['date']).dt.year
df_final = df_meteo_joined.merge(df_inputs, on=['country', 'year'], how='left')
print(f"✅ Fusion finale avec FAOSTAT : {len(df_final)} lignes\n")

# 💾 5. Export
output_file = "dataset_agronomique_final.csv"
df_final.to_csv(output_file, index=False)
print(f"💾 Export terminé vers : {output_file}")
