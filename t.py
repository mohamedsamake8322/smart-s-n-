import os
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
import pandas as pd
from tqdm import tqdm
import geopandas as gpd

# Chemin local du shapefile dézippé
shapefile_path = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp"

gdf = gpd.read_file(shapefile_path)
africa = gdf[gdf['CONTINENT'] == 'Africa'].to_crs("EPSG:4326")

# 📁 Répertoire des .tif
base_dir = r"C:\Users\moham\Music\3\2.5 min"
folders = {
    'precip': os.path.join(base_dir, 'Precipitation'),
    'tmax': os.path.join(base_dir, 'Température max'),
    'tmin': os.path.join(base_dir, 'Température min'),
}

# 🌍 Charger les pays d'Afrique (via Natural Earth)
gdf = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
africa = gdf[gdf['continent'] == 'Africa'].to_crs("EPSG:4326")

# 🔁 Fonction pour lire et calculer la moyenne par pays
def zonal_mean_by_country(tif_path, country_geom):
    with rasterio.open(tif_path) as src:
        try:
            out_image, _ = mask(src, [country_geom], crop=True)
            data = out_image[0].astype(float)
            data[data == src.nodata] = np.nan
            return np.nanmean(data)
        except Exception:
            return np.nan

# 📄 Résultats
results = []

# 🔁 Pour chaque mois
for month in tqdm(range(1, 13), desc="📆 Traitement des mois"):
    month_str = f"{month:02d}"

    # 📂 Chemins TIF de ce mois
    tif_paths = {}
    for var, folder in folders.items():
        for file in os.listdir(folder):
            if file.endswith(f"{month_str}.tif"):
                tif_paths[var] = os.path.join(folder, file)
                break

    # 📍 Pour chaque pays
    for _, row in africa.iterrows():
        country = row['name']
        geom = row['geometry']
        entry = {
            'pays': country,
            'mois': month,
        }
        for var in ['precip', 'tmax', 'tmin']:
            val = zonal_mean_by_country(tif_paths[var], geom)
            entry[f"{var}_moy"] = round(val, 2) if not np.isnan(val) else None
        results.append(entry)

# 📄 Sauvegarde
df = pd.DataFrame(results)
output_csv = os.path.join(base_dir, "worldclim_2.5min_afrique_par_pays.csv")
df.to_csv(output_csv, index=False)

print(f"✅ Extraction terminée : {output_csv}")
