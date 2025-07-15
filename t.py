import os
import rasterio
import numpy as np
import pandas as pd

# 📁 Répertoire de base (2.5 min uniquement)
base_dir = r"C:\Users\moham\Music\3\2.5 min"

# 🔧 Dossiers exacts
folders = {
    'precip': os.path.join(base_dir, 'Precipitation'),
    'tmax': os.path.join(base_dir, 'Température max'),
    'tmin': os.path.join(base_dir, 'Température min'),
}

# 🔁 Fonction pour lire et calculer la moyenne
def get_mean_from_tif(tif_path):
    with rasterio.open(tif_path) as src:
        data = src.read(1).astype(float)
        data[data == src.nodata] = np.nan
        return np.nanmean(data)

# 🗃️ Résultats
results = []

# 🔁 Pour chaque mois
for month in range(1, 13):
    row = {'mois': month}
    month_str = f"{month:02d}"
    for var, folder in folders.items():
        for file in os.listdir(folder):
            if file.endswith(f"{month_str}.tif"):
                tif_path = os.path.join(folder, file)
                mean_val = get_mean_from_tif(tif_path)
                row[f"{var}_moy"] = round(mean_val, 2)
                break
    results.append(row)

# 🧾 DataFrame
df = pd.DataFrame(results)
df['année'] = 'historique'
df = df[['année', 'mois', 'precip_moy', 'tmax_moy', 'tmin_moy']]

# 💾 Export CSV
output_path = os.path.join(base_dir, "worldclim_mensuel_2.5min_afrique.csv")
df.to_csv(output_path, index=False)

print(f"✅ CSV généré avec succès : {output_path}")
