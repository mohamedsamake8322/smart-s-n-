import pandas as pd
import geopandas as gpd
import os

# === CONFIGURATION ===
BASE_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Fichiers
chirps_file = os.path.join(BASE_DIR, "CHIRPS_DAILY_PENTAD.csv")
smap_file = os.path.join(BASE_DIR, "SMAP_SoilMoisture.csv")
faostat_file = os.path.join(BASE_DIR, "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv")
gedi_file = os.path.join(BASE_DIR, "GEDI_Mangrove_CSV.csv")
land_water_file = os.path.join(BASE_DIR, "X_land_water_cleanedRessources en terres et en eau.csv")

# === 1. Lecture des fichiers ===
print("📥 Lecture des fichiers...")
chirps = pd.read_csv(chirps_file)
smap = pd.read_csv(smap_file)
faostat = pd.read_csv(faostat_file)
gedi = pd.read_csv(gedi_file)
land_water = pd.read_csv(land_water_file)

# === 2. Uniformisation des colonnes pays / année ===
print("🔄 Harmonisation des colonnes...")
# CHIRPS
if "country" not in chirps.columns:
    chirps.rename(columns={"Country": "country", "Year": "year"}, inplace=True)

# SMAP
if "country" not in smap.columns:
    smap.rename(columns={"Country": "country", "Year": "year"}, inplace=True)

# FAOSTAT
if "country" not in faostat.columns:
    faostat.rename(columns={"Area": "country", "Year": "year"}, inplace=True)

# GEDI
if "country" not in gedi.columns:
    gedi.rename(columns={"ADM0_NAME": "country"}, inplace=True)

# === 3. Spatial join pour land_water et gedi ===
print("🌍 Récupération contours pays...")
world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))[["name", "geometry"]]
world.rename(columns={"name": "country"}, inplace=True)

# Land_water
print("🗺 Traitement Land/Water...")
gdf_land = gpd.GeoDataFrame(land_water, geometry=gpd.points_from_xy(land_water.lon, land_water.lat), crs="EPSG:4326")
gdf_land = gpd.sjoin(gdf_land, world, how="left", predicate="within")
land_agg = gdf_land.groupby("country").mean(numeric_only=True).reset_index()

# GEDI
print("🗺 Traitement GEDI...")
gdf_gedi = gpd.GeoDataFrame(gedi, geometry=gpd.GeoSeries.from_wkt(gedi[".geo"]), crs="EPSG:4326")
gdf_gedi = gdf_gedi.drop(columns=[".geo", "system:index"], errors="ignore")
gedi_agg = gdf_gedi.groupby("country").mean(numeric_only=True).reset_index()

# === 4. Fusion ===
print("🔗 Fusion des datasets...")
df = chirps.merge(smap, on=["country", "year"], how="outer", suffixes=("_chirps", "_smap"))
df = df.merge(faostat, on=["country", "year"], how="outer")
df = df.merge(land_agg, on="country", how="left")
df = df.merge(gedi_agg, on="country", how="left")

# === 5. Résultat final ===
print("✅ Fusion terminée !")
print(df.head())

# Sauvegarde
output_file = os.path.join(BASE_DIR, "fusion_finale.csv")
df.to_csv(output_file, index=False)
print(f"💾 Fichier final sauvegardé ici : {output_file}")
