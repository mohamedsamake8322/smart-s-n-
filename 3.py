import rioxarray as rxr
import pandas as pd
import os

# Dossier racine
base_folder = "soilgrids_africa"

# Propriétés et profondeurs
properties = ["soc", "cec", "phh2o", "clay", "silt", "sand"]
depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

# Dictionnaire pour stocker les DataFrames
dfs = {}

for prop in properties:
    stack = []
    for depth in depths:
        file_path = os.path.join(base_folder, prop, f"{prop}_{depth}_mean.tif")
        raster = rxr.open_rasterio(file_path).squeeze()

        # Récupérer x, y, valeurs
        x = raster.x.values
        y = raster.y.values
        v = raster.values

        df = pd.DataFrame({
            "x": x.repeat(len(y)),
            "y": list(y) * len(x),
            f"{prop}_{depth}": v.flatten()
        })

        # Filtrer les valeurs manquantes
        df = df[df[f"{prop}_{depth}"] != -32768]
        stack.append(df)

    # Fusion verticale des couches d'une même propriété
    df_prop = stack[0]
    for d in stack[1:]:
        df_prop = df_prop.merge(d, on=["x", "y"], how="outer")

    dfs[prop] = df_prop.reset_index(drop=True)

# 🔗 Fusion horizontale des propriétés
df_final = dfs[properties[0]]
for p in properties[1:]:
    df_final = df_final.merge(dfs[p], on=["x", "y"], how="outer")

print(df_final.head())
