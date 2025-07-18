# 🧠 NDVI Extractor — DEAfrica Starter

# 🌍 Import des bibliothèques
import os
import datacube
from deafrica_tools.datahandling import load_ard
from deafrica_tools.bandindices import calculate_indices
import matplotlib.pyplot as plt
import numpy as np

# 📦 Correction environnement GDAL (pour éviter les erreurs)
os.environ["GDAL_DATA"] = os.path.join(os.environ["CONDA_PREFIX"], "Library", "share", "gdal")

# 📦 Initialiser le Data Cube
dc = datacube.Datacube(app="ndvi_extractor")

# 📍 Définir la zone d'intérêt (buffer ~2.5km autour du point)
latitude = 19.66
longitude = 4.3
buffer = 0.025

lat_range = (latitude - buffer, latitude + buffer)
lon_range = (longitude - buffer, longitude + buffer)
time_range = ("2021-01-01", "2021-12-31")

# 📥 Charger les données Sentinel-2
ds = load_ard(
    dc=dc,
    products=["s2_l2a"],
    x=lon_range,
    y=lat_range,
    time=time_range,
    output_crs="EPSG:4326",
    resolution=(-10, 10),
    group_by="solar_day",
    cloud_mask=True
)

print(f"✅ Dataset chargé avec {len(ds.time)} observations")

# 🌿 Calcul de l’indice NDVI
ds = calculate_indices(ds, index="NDVI", satellite_mission="s2")

# 📈 NDVI moyen sur l’année
ndvi_mean = ds.NDVI.mean(dim=["x", "y"])
ndvi_mean.plot(figsize=(10, 4), title="🌿 NDVI moyen sur 2021")
plt.tight_layout()
plt.show()

# 🔍 Statistiques résumées
print("📊 Statistiques NDVI :")
print(ndvi_mean.to_dataframe().describe())
