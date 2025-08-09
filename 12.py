import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 🔹 Étape 1 : Définir le chemin du fichier
file_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\X_land_water_cleanedRessources en terres et en eau.csv"

# 🔹 Étape 2 : Charger le fichier CSV
df_resources = pd.read_csv(file_path)

# 🔹 Étape 3 : Créer une GeoDataFrame à partir des colonnes lon/lat
geometry = [Point(xy) for xy in zip(df_resources["lon"], df_resources["lat"])]
gdf_resources = gpd.GeoDataFrame(df_resources, geometry=geometry, crs="EPSG:4326")

# 🔹 Étape 4 : Charger les frontières des pays (Natural Earth depuis ton dossier local)
world_shp_path = r"C:\plateforme-agricole-complete-v2\data\Natural Earth 110m Cultural Vectors\ne_110m_admin_0_countries.shp"
world = gpd.read_file(world_shp_path)

# 🔹 Étape 5 : Spatial join pour associer chaque point à un pays
gdf_joined = gpd.sjoin(gdf_resources, world[["geometry", "NAME"]], how="left", predicate="intersects")
gdf_joined.rename(columns={"NAME": "country"}, inplace=True)

# 🔹 Étape 6 : Agréger les données par pays
df_aggregated = gdf_joined.groupby("country").mean(numeric_only=True).reset_index()

# 🔹 Étape 7 : Fusion avec ton DataFrame climat_prod
df_climat_prod = pd.read_csv(r"C:\plateforme-agricole-complete-v2\SmartSènè\climat_prod.csv")  # adapte si besoin
df_final = pd.merge(df_climat_prod, df_aggregated, on="country", how="left")

# 🔹 Étape 8 : Sauvegarde du résultat
output_path = r"C:\plateforme-agricole-complete-v2\SmartSènè\climat_prod_enrichi.csv"
df_final.to_csv(output_path, index=False)

print("Fusion réussie ! Aperçu :")
print(df_final.head())
