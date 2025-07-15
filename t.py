import os
import rasterio
import numpy as np
import pandas as pd

# 📁 Répertoire de base
base_dir = r"C:\Users\moham\Music\3"

# 🔁 Fonction pour lire et calculer la moyenne d’un raster
def get_mean_from_tif(tif_path):
    with rasterio.open(tif_path) as src:
        data = src.read(1).astype(float)
        data[data == src.nodata] = np.nan
        return np.nanmean(data)

# 📁 Sous-dossiers par variable
folders = {
    'precip': os.path.join(base_dir, 'Precipitation'),
    'tmax': os.path.join(base_dir, 'Température max'),
    'tmin': os.path.join(base_dir, 'Température min'),
}

# 🗃️ Préparation du DataFrame
results = []

# 🔁 On suppose que les fichiers ont des noms comme wc2.1_2.5m_pr_01.tif
for month in range(1, 13):
    row = {'mois': month}
    month_str = f"{month:02d}"
    for var, folder in folders.items():
        for file in os.listdir(folder):
            if file.endswith(f"{month_str}.tif"):
                path = os.path.join(folder, file)
                mean_val = get_mean_from_tif(path)
                row[f"{var}_moy"] = round(mean_val, 2)
                break
    results.append(row)

# 📄 Création du DataFrame final
df = pd.DataFrame(results)
df['année'] = 'historique'
df = df[['année', 'mois', 'precip_moy', 'tmax_moy', 'tmin_moy']]

# 💾 Export CSV
output_csv = os.path.join(base_dir, "worldclim_mensuel_moy_afrique.csv")
df.to_csv(output_csv, index=False)

print(f"✅ Fichier CSV généré : {output_csv}")
