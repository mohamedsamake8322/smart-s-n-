import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import BallTree
import numpy as np

# 📥 1. Charger les données
gdf_soil = gpd.read_file("isdasoil_points.geojson")  # Données sol en GeoDataFrame
df_meteo = pd.read_csv("merged_weather_africa.csv")  # Données météo enrichies
df_inputs = pd.read_csv("indicateurs_agronomiques_FAOSTAT.csv")  # Indicateurs par pays et année

# 📍 2. Appariement météo-sol par proximité géographique

# Préparer les coordonnées en radians
soil_coords = np.deg2rad(gdf_soil[['latitude', 'longitude']].values)
weather_coords = np.deg2rad(df_meteo[['latitude', 'longitude']].values)

# Construire l'index spatial BallTree
tree = BallTree(soil_coords, metric='haversine')
dist, idx = tree.query(weather_coords, k=1)

# Ajouter les infos d'appariement
df_meteo['soil_index'] = idx.flatten()
df_meteo['distance_km'] = dist.flatten() * 6371  # conversion en km

# ⚠️ Filtrer les appariements trop éloignés (> 50 km)
df_meteo_filtered = df_meteo[df_meteo['distance_km'] <= 50]

# 🔗 3. Fusion météo + sol
gdf_soil = gdf_soil.reset_index()
df_meteo_joined = df_meteo_filtered.merge(gdf_soil, left_on='soil_index', right_on='index')

# 🕒 4. Ajout de l'année à partir de la date
df_meteo_joined['year'] = pd.to_datetime(df_meteo_joined['date']).dt.year

# 📊 5. Fusion météo+sol avec FAOSTAT (par pays et année)
df_final = df_meteo_joined.merge(df_inputs, on=['country', 'year'], how='left')

# 💾 6. Export du jeu final
df_final.to_csv("dataset_agronomique_final.csv", index=False)
print("✅ Fusion complète terminée : dataset_agronomique_final.csv avec météo + sol + FAOSTAT")
