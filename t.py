import os
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
import pandas as pd
from tqdm import tqdm

# 📍 Chemin du shapefile
shapefile_path = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp"

# 🌍 Charger les pays d'Afrique
gdf = gpd.read_file(shapefile_path)
africa = gdf[gdf['CONTINENT'].str.lower() == 'africa'].to_crs("EPSG:4326")

# 📁 Répertoires des variables climatiques
base_dir = r"C:\Users\moham\Music\3\2.5 min"
folders = {
    'precip': os.path.join(base_dir, 'Precipitation'),
    'tmax': os.path.join(base_dir, 'Température max'),
    'tmin': os.path.join(base_dir, 'Température min'),
}

# 🔁 Fonction pour la moyenne zonale
def zonal_mean_by_country(tif_path, country_geom):
    try:
        with rasterio.open(tif_path) as src:
            out_image, _ = mask(src, [country_geom], crop=True)
            data = out_image[0].astype(float)
            data[data == src.nodata] = np.nan
            return np.nanmean(data)
    except Exception:
        return np.nan

# 📊 Stockage des résultats
results = []

# 📆 Boucle mensuelle
for month in tqdm(range(1, 13), desc="📆 Traitement des mois"):
    month_str = f"{month:02d}"
    tif_paths = {var: None for var in folders}

    # 📂 Récupérer le fichier .tif correspondant pour chaque variable
    for var, folder in folders.items():
        matched_files = [file for file in os.listdir(folder) if file.endswith(f"{month_str}.tif")]
        if matched_files:
            tif_paths[var] = os.path.join(folder, matched_files[0])

    # 📍 Boucle par pays
    for _, row in africa.iterrows():
        entry = {
            'pays': row['NAME'],
            'mois': month,
        }

        for var in ['precip', 'tmax', 'tmin']:
            tif_path = tif_paths[var]
            val = zonal_mean_by_country(tif_path, row['geometry']) if tif_path else None
            entry[f"{var}_moy"] = round(val, 2) if val is not None and not np.isnan(val) else None

        results.append(entry)

# 💾 Export CSV
df = pd.DataFrame(results)
output_csv = os.path.join(base_dir, "worldclim_2.5min_afrique_par_pays.csv")
df.to_csv(output_csv, index=False)

print(f"✅ Extraction terminée : {output_csv}")
