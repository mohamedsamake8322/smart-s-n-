import rioxarray as rxr
import pandas as pd
import os

# Dossier contenant les fichiers SOC
folder = "soilgrids_africa/soc"
depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm", "60-100cm", "100-200cm"]

stack = []

for depth in depths:
    tif_path = os.path.join(folder, f"soc_{depth}_mean.tif")
    raster = rxr.open_rasterio(tif_path).squeeze()

    # Extraction des coordonnées
    y_coords = raster.y.values
    x_coords = raster.x.values
    values = raster.values

    # Flatten et association
    df = pd.DataFrame({
        "x": x_coords.repeat(len(y_coords)),
        "y": y_coords.tolist() * len(x_coords),
        f"soc_{depth}": values.flatten()
    })

    # Filtrer les valeurs manquantes (_FillValue)
    df = df[df[f"soc_{depth}"] != -32768]
    stack.append(df.reset_index(drop=True))

# Fusion des DataFrames sur x/y
df_final = stack[0][["x", "y", "soc_0-5cm"]]
for i in range(1, len(stack)):
    df_final = df_final.merge(stack[i], on=["x", "y"], how="outer")

print(df_final.head())
