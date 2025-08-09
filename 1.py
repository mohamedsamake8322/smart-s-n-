import pandas as pd
import geopandas as gpd  # pyright: ignore[reportMissingModuleSource]
import os
import json
from shapely.geometry import Point, shape  # pyright: ignore[reportMissingModuleSource]

BASE_DIR = r"C:\plateforme-agricole-complete-v2\SmartSènè"

# Fichiers
chirps_file = os.path.join(BASE_DIR, "CHIRPS_DAILY_PENTAD.csv")
smap_file = os.path.join(BASE_DIR, "SMAP_SoilMoisture.csv")
faostat_file = os.path.join(BASE_DIR, "ProductionIndicesFAOSTAT_data_en_7-22-2025.csv")
gedi_file = os.path.join(BASE_DIR, "GEDI_Mangrove_CSV.csv")
land_water_file = os.path.join(BASE_DIR, "X_land_water_cleanedRessources en terres et en eau.csv")

print("📥 Lecture des fichiers...")
chirps = pd.read_csv(chirps_file)
smap = pd.read_csv(smap_file)
faostat = pd.read_csv(faostat_file)
gedi = pd.read_csv(gedi_file)
land_water = pd.read_csv(land_water_file)

print("🔄 Harmonisation des colonnes...")
chirps.rename(columns={"ADM0_NAME": "country", "STR1_YEAR": "year", "CHIRPS_Daily": "rainfall"}, inplace=True)
smap.rename(columns={"ADM0_NAME": "country", "STR1_YEAR": "year", "mean": "soil_moisture"}, inplace=True)
faostat.rename(columns={"Area": "country", "Year": "year", "Value": "yield"}, inplace=True)
gedi.rename(columns={"ADM0_NAME": "country"}, inplace=True)

print("🌍 Récupération contours pays...")
world_shp_path = r"C:\plateforme-agricole-complete-v2\data\Natural Earth 110m Cultural Vectors\ne_110m_admin_0_countries.shp"
world = gpd.read_file(world_shp_path)[["NAME", "geometry"]]
world.rename(columns={"NAME": "country"}, inplace=True)

print("🗺 Traitement Land/Water...")
gdf_land = gpd.GeoDataFrame(land_water, geometry=gpd.points_from_xy(land_water.lon, land_water.lat), crs="EPSG:4326")
gdf_land = gpd.sjoin(gdf_land, world, how="left", predicate="within")
land_agg = gdf_land.groupby("country").mean(numeric_only=True).reset_index()

print("🗺 Traitement GEDI...")

def geojson_to_geom(geojson_str):
    try:
        geojson_dict = json.loads(geojson_str)
        return shape(geojson_dict)
    except Exception as e:
        print(f"Erreur conversion GeoJSON: {e}")
        return None

gedi["geometry"] = gedi[".geo"].apply(geojson_to_geom)
gdf_gedi = gpd.GeoDataFrame(gedi, geometry="geometry", crs="EPSG:4326")
gdf_gedi = gdf_gedi.drop(columns=[".geo", "system:index"], errors="ignore")
gedi_agg = gdf_gedi.groupby("country").mean(numeric_only=True).reset_index()

print("🔗 Fusion des datasets...")
df = chirps.merge(smap, on=["country", "year"], how="outer", suffixes=("_chirps", "_smap"))
df = df.merge(faostat, on=["country", "year"], how="outer")
df = df.merge(land_agg, on="country", how="left")
df = df.merge(gedi_agg, on="country", how="left")

print("🧹 Suppression des doublons...")
# Détection des doublons sur les colonnes clés
before = len(df)
df.drop_duplicates(subset=["country", "year"], keep="first", inplace=True)
after = len(df)
print(f"🔍 {before - after} doublon(s) supprimé(s).")

print("✅ Fusion terminée !")
print(df.head())
print("📁 Sauvegarde des doublons détectés...")
duplicates = df[df.duplicated(subset=["country", "year"], keep=False)]
duplicates.to_csv(os.path.join(BASE_DIR, "doublons_detectés.csv"), index=False)
print(f"📝 {len(duplicates)} doublons enregistrés dans 'doublons_detectés.csv'.")

print("🧹 Nettoyage des colonnes techniques...")
cols_to_drop = [col for col in df.columns if "system:index" in col or "ADM0_CODE" in col]
df.drop(columns=cols_to_drop, inplace=True)
print(f"🧾 Colonnes supprimées : {cols_to_drop}")

print("🔍 Audit de la fusion...")

def audit_source(df_source, name):
    countries = set(df_source["country"].dropna().unique())
    years = set(df_source["year"].dropna().unique()) if "year" in df_source.columns else set()
    print(f"📦 {name} → {len(countries)} pays, {len(years)} années")
    return countries, years

# Audit des sources
countries_chirps, years_chirps = audit_source(chirps, "CHIRPS")
countries_smap, years_smap = audit_source(smap, "SMAP")
countries_faostat, years_faostat = audit_source(faostat, "FAOSTAT")

# Audit du résultat fusionné
countries_final = set(df["country"].dropna().unique())
years_final = set(df["year"].dropna().unique())

# Vérification des pertes
missing_countries = (countries_chirps | countries_smap | countries_faostat) - countries_final
missing_years = (years_chirps | years_smap | years_faostat) - years_final

if missing_countries:
    print(f"⚠️ Pays manquants après fusion : {sorted(missing_countries)}")
else:
    print("✅ Tous les pays sources sont présents dans la fusion.")

if missing_years:
    print(f"⚠️ Années manquantes après fusion : {sorted(missing_years)}")
else:
    print("✅ Toutes les années sources sont présentes dans la fusion.")

# Export compressé
output_file = os.path.join(BASE_DIR, "fusion_finale.csv.gz")
df.to_csv(output_file, index=False, compression="gzip")
print(f"💾 Fichier final compressé sauvegardé ici : {output_file}")
import seaborn as sns
import matplotlib.pyplot as plt

pivot = df.pivot_table(index="country", columns="year", values="rainfall", aggfunc="count", fill_value=0)
plt.figure(figsize=(12, 8))
sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5)
plt.title("📊 Couverture des données par pays et année")
plt.xlabel("Année")
plt.ylabel("Pays")
plt.tight_layout()
plt.show()
