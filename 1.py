import geopandas as gpd
import os

path = "gadm_africa_geojson"
merged = gpd.GeoDataFrame()

for file in os.listdir(path):
    if file.endswith(".geojson"):
        gdf = gpd.read_file(os.path.join(path, file))
        merged = merged.append(gdf, ignore_index=True)

print(f"🔗 Total entités fusionnées : {len(merged)}")
merged.plot()
