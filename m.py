#🧪 Script Python — Fusion Sol + Climat + Engrais
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from sklearn.neighbors import BallTree
import numpy as np

# 📥 Charger les données de sol (GeoDataFrame déjà créée)
gdf_soil = gpd.read_file("isdasoil_points.geojson")

# 📥 Charger les données météo restructurées
df_meteo = pd.read_csv("weather_afrique_restruc_total.csv")

# 📥 Charger les indicateurs FAOSTAT
df_inputs = pd.read_csv("indicateurs_agronomiques_FAOSTAT.csv")

# 🧭 Étape 1 — Associer météo par proximité géographique

# Convertir points sol en radians
soil_coords = np.deg2rad(gdf_soil[['latitude', 'longitude']].values)
tree = BallTree(soil_coords, metric='haversine')

# Associer chaque point météo au point de sol le plus proche
weather_coords = np.deg2rad(df_meteo[['latitude', 'longitude']].values)
dist, idx = tree.query(weather_coords, k=1)

# Créer fusion météo+sol
df_meteo['soil_index'] = idx.flatten()
df_meteo['distance_km'] = dist.flatten() * 6371  # rayon terrestre

# Filtrer les paires trop éloignées (> 50 km)
df_meteo_filtered = df_meteo[df_meteo['distance_km'] <= 50]

# 🧠 Étape 2 — Fusion sol + météo
gdf_soil = gdf_soil.reset_index()
df_meteo_joined = df_meteo_filtered.merge(gdf_soil, left_on='soil_index', right_on='index')

# 📊 Étape 3 — Ajouter FAOSTAT (par pays et année)
df_meteo_joined['year'] = pd.DatetimeIndex(df_meteo_joined['date']).year
df_final = df_meteo_joined.merge(df_inputs, on=['country', 'year'], how='left')

# 💾 Exporter le jeu d’apprentissage final
df_final.to_csv("dataset_agronomique_final.csv", index=False)
print("✅ Fusion complète terminée : dataset_agronomique_final.csv")
