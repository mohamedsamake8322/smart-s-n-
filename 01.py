import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
import json

# 📥 Charger X_enriched
x_enriched = pd.read_csv("SmartSènè/X_dataset_enriched Écarts de rendement et de production_Rendements et production réels.csv")
x_enriched['geometry'] = x_enriched.apply(lambda row: Point(row['lon'], row['lat']), axis=1)
gdf_points = gpd.GeoDataFrame(x_enriched, geometry='geometry', crs="EPSG:4326")

# 📥 Charger GEDI et parser les géométries
gedi_raw = pd.read_csv("SmartSènè/GEDI_Mangrove_CSV.csv")
gedi_raw = gedi_raw.dropna(subset=['.geo'])  # Supprimer les lignes sans géométrie

def parse_geo(geo_str):
    geo_dict = json.loads(geo_str)
    return shape(geo_dict)

gedi_raw['geometry'] = gedi_raw['.geo'].apply(parse_geo)
gdf_polygons = gpd.GeoDataFrame(gedi_raw, geometry='geometry', crs="EPSG:4326")

# 🔗 Fusion spatiale : joindre les points aux polygones GEDI
merged = gpd.sjoin(gdf_points, gdf_polygons, how='left', predicate='within')

# 🧹 Nettoyage
merged.drop(columns=['geometry', 'index_right'], inplace=True)

# 💾 Sauvegarde compressée gzip
merged.to_csv("SmartSènè/X_enriched_plus_GEDI_spatial.csv.gz", index=False, compression="gzip")
print("✅ Fusion géospatiale terminée : SmartSènè/X_enriched_plus_GEDI_spatial.csv.gz")
