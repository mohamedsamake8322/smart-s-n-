from datacube import Datacube
from deafrica_tools.datahandling import load_ard
from deafrica_tools.bandindices import calculate_indices
import pandas as pd

dc = Datacube(app="senesmart")

df_coords = pd.read_csv("african_coordinates.csv")
ndvi_stats = []

for idx, row in df_coords.iterrows():
    lat, lon, year = row["latitude"], row["longitude"], row["year"]
    lat_range = (lat - 0.05, lat + 0.05)
    lon_range = (lon - 0.05, lon + 0.05)
    time_range = (f"{year}-01-01", f"{year}-12-31")

    try:
        ds = load_ard(dc, products=["s2_l2a"], x=lon_range, y=lat_range,
                      time=time_range, output_crs="EPSG:4326", cloud_mask=True)
        ds = calculate_indices(ds, index="NDVI", satellite_mission="s2")
        ndvi_mean = ds.NDVI.mean(dim=["x", "y"]).mean().item()
        ndvi_stats.append({
            "country": row["country"],
            "year": year,
            "latitude": lat,
            "longitude": lon,
            "culture": row["culture"],
            "ndvi_mean": round(ndvi_mean, 4)
        })
    except Exception as e:
        print(f"⚠️ Erreur zone {idx}: {e}")

df_ndvi = pd.DataFrame(ndvi_stats)
df_ndvi.to_csv("ndvi_africa.csv", index=False)
