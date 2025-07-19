from datacube import Datacube
from datahandling import load_ard
from bandindices import calculate_indices
import pandas as pd

# 📦 Initialisation du Datacube
dc = Datacube(app="ndvi_extraction")

def extract_ndvi_batch(df_coords, buffer=0.05):
    ndvi_stats = []

    for idx, row in df_coords.iterrows():
        lat, lon, year = row["latitude"], row["longitude"], row["year"]
        lat_range = (lat - buffer, lat + buffer)
        lon_range = (lon - buffer, lon + buffer)
        time_range = (f"{year}-01-01", f"{year}-12-31")

        try:
            ds = load_ard(dc, products=["s2_l2a"], x=lon_range, y=lat_range,
                          time=time_range, output_crs="EPSG:4326", cloud_mask=True)

            if ds is None or not hasattr(ds, "measurements") or ds.measurements is None:
                print(f"⚠️ Erreur zone {idx}: aucune donnée disponible (lat={lat}, lon={lon})")
                continue

            ds = calculate_indices(ds, index="NDVI", satellite_mission="s2")

            if ds is not None and hasattr(ds, "NDVI") and ds.NDVI.size > 0:
                ndvi_mean = ds.NDVI.mean(dim=["x", "y"]).mean().item()
            else:
                ndvi_mean = None

            ndvi_stats.append({
                "country": row["country"],
                "year": year,
                "latitude": lat,
                "longitude": lon,
                "culture": row["culture"],
                "ndvi_mean": ndvi_mean
            })

        except Exception as e:
            print(f"⚠️ Erreur zone {idx} ({lat}, {lon}): {e}")

    # ✅ Toujours retourner un DataFrame avec les bonnes colonnes
    return pd.DataFrame(ndvi_stats, columns=[
        "country", "year", "latitude", "longitude", "culture", "ndvi_mean"
    ])
