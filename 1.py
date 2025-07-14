import geopandas as gpd
import pandas as pd
import os

path = "gadm_africa_geojson"
geojson_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".geojson")]

# 🔄 Fusion avec pd.concat()
gdfs = [gpd.read_file(f) for f in geojson_files]
merged = pd.concat(gdfs, ignore_index=True)

print(f"🔗 Total entités fusionnées : {len(merged)}")
merged.plot()
