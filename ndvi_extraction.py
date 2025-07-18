# 🧠 NDVI Extractor — version optimisée sans deafrica_tools

import os
import datacube
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd

# 📦 Correction GDAL (pour éviter les erreurs de chemin)
os.environ["GDAL_DATA"] = os.path.join(os.environ["CONDA_PREFIX"], "Library", "share", "gdal")

# 📦 Initialisation du cube
dc = datacube.Datacube(app="sene_ndvi_extractor")

# 📍 Paramètres de la zone ciblée
latitude = 19.66
longitude = 4.3
buffer = 0.025  # ~2.5 km autour du point
lat_range = (latitude - buffer, latitude + buffer)
lon_range = (longitude - buffer, longitude + buffer)
time_range = ("2021-01-01", "2021-12-31")

# 📥 Chargement Sentinel-2 (NIR & Red uniquement)
ds = dc.load(
    product="s2_l2a",
    x=lon_range,
    y=lat_range,
    time=time_range,
    measurements=["nir", "red"],
    output_crs="EPSG:4326",
    resolution=(-10, 10),
    group_by="solar_day"
)

print(f"✅ Données chargées : {len(ds.time)} observations")

# 🌿 Calcul NDVI
ndvi = (ds.nir - ds.red) / (ds.nir + ds.red)
ndvi.attrs["units"] = "unitless"

# 📉 Nettoyage des valeurs aberrantes
ndvi = ndvi.where((ndvi >= -1.0) & (ndvi <= 1.0))

# 📈 Moyenne spatiale par date
ndvi_mean = ndvi.mean(dim=["x", "y"])

# 📤 Export CSV + plot
ndvi_df = ndvi_mean.to_dataframe(name="ndvi").reset_index()
ndvi_df.to_csv("ndvi_2021_zone_4.3_19.66.csv", index=False)

# 📊 Statistiques
print("📊 Résumé NDVI sur la période :")
print(ndvi_df["ndvi"].describe())

# 📈 Tracé visuel
plt.figure(figsize=(10, 4))
plt.plot(ndvi_df["time"], ndvi_df["ndvi"], marker="o", linestyle="-", color="green")
plt.title("🌿 NDVI moyen — 2021")
plt.xlabel("Date")
plt.ylabel("NDVI moyen")
plt.grid(True)
plt.tight_layout()
plt.show()
