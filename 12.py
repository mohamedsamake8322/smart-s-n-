import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

# 📁 Dossier principal
base_path = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# 🔹 Étape 1 : Charger les fichiers climatiques et agricoles
df_chirps = pd.read_csv(os.path.join(base_path, "CHIRPS_DAILY_PENTAD.csv"))
df_smap = pd.read_csv(os.path.join(base_path, "SMAP_SoilMoisture.csv"))
df_prod = pd.read_csv(os.path.join(base_path, "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv"))
df_gedi = pd.read_csv(os.path.join(base_path, "GEDI_Mangrove_CSV.csv"))

# 🔹 Étape 2 : Agréger par pays et année
chirps_agg = df_chirps.groupby(["country", "year"])["rainfall"].mean().reset_index()
smap_agg = df_smap.groupby(["country", "year"])["soil_moisture"].mean().reset_index()
prod_agg = df_prod.groupby(["country", "year"])["yield"].mean().reset_index()
gedi_agg = df_gedi.groupby(["country", "year"])[["ndvi", "biomass"]].mean().reset_index()

# 🔹 Étape 3 : Fusionner toutes les sources
df_climat_prod = chirps_agg \
    .merge(smap_agg, on=["country", "year"], how="outer") \
    .merge(prod_agg, on=["country", "year"], how="outer") \
    .merge(gedi_agg, on=["country", "year"], how="outer")

# 🔹 Étape 4 : Charger le fichier de ressources géolocalisées
resources_path = os.path.join(base_path, "X_land_water_cleanedRessources en terres et en eau.csv")
df_resources = pd.read_csv(resources_path)

# 🔹 Étape 5 : Créer une GeoDataFrame à partir des colonnes lon/lat
geometry = [Point(xy) for xy in zip(df_resources["lon"], df_resources["lat"])]
gdf_resources = gpd.GeoDataFrame(df_resources, geometry=geometry, crs="EPSG:4326")

# 🔹 Étape 6 : Charger les frontières des pays (shapefile local)
world_shp_path = r"C:\plateforme-agricole-complete-v2\data\Natural Earth 110m Cultural Vectors\ne_110m_admin_0_countries.shp"
world = gpd.read_file(world_shp_path)

# 🔹 Étape 7 : Spatial join pour associer chaque point à un pays
gdf_joined = gpd.sjoin(gdf_resources, world[["geometry", "NAME"]], how="left", predicate="intersects")
gdf_joined.rename(columns={"NAME": "country"}, inplace=True)

# 🔹 Étape 8 : Agréger les ressources par pays
df_aggregated = gdf_joined.groupby("country").mean(numeric_only=True).reset_index()

# 🔹 Étape 9 : Fusion finale avec climat_prod
df_final = pd.merge(df_climat_prod, df_aggregated, on="country", how="left")

# 🔹 Étape 10 : Sauvegarde du résultat
output_path = os.path.join(base_path, "climat_prod_enrichi.csv")
df_final.to_csv(output_path, index=False)

print("✅ Fusion multi-sources réussie ! Aperçu :")
print(df_final.head())
