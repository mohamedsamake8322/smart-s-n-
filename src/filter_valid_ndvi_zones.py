import sys
import os
import pandas as pd
deafrica_module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'deafrica-tools', 'deafrica_tools'))
if os.path.exists(deafrica_module_path):
    sys.path.append(deafrica_module_path)
else:
    print(f"❌ Module deafrica_tools introuvable à : {deafrica_module_path}")
    sys.exit(1)
from datacube import Datacube
from datahandling import load_ard


dc = Datacube(app="ndvi_filter")

def filter_valid_zones(df_coords, buffer=0.1):
    valid_zones = []

    for idx, row in df_coords.iterrows():
        lat, lon, year = row["latitude"], row["longitude"], row["year"]
        lat_range = (lat - buffer, lat + buffer)
        lon_range = (lon - buffer, lon + buffer)
        time_range = (f"{year}-01-01", f"{year}-12-31")

        try:
            ds = load_ard(dc, products=["s2_l2a"], x=lon_range, y=lat_range,
                          time=time_range, output_crs="EPSG:4326", cloud_mask=True)
            if ds is not None and ds.time.size > 0:
                valid_zones.append(row)
            else:
                print(f"🚫 Zone rejetée {idx}: aucune observation Sentinel-2")
        except Exception as e:
            print(f"⚠️ Erreur zone {idx}: {e}")

    print(f"✅ Zones valides retenues : {len(valid_zones)}")
    return pd.DataFrame(valid_zones)

if __name__ == "__main__":
    df = pd.read_csv("african_coordinates.csv")
    filtered_df = filter_valid_zones(df)
    filtered_df.to_csv("african_coordinates_valid.csv", index=False)
