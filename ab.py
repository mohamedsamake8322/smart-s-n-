import pandas as pd
import geopandas as gpd
import os

# 📂 Charger ton fichier CSV
csv_path = "iSDA_soil_data.csv"  # ← à remplacer par le chemin réel
if not os.path.isfile(csv_path):
    raise FileNotFoundError(f"Le fichier '{csv_path}' est introuvable.")

df_soil = pd.read_csv(csv_path)

# ✅ Vérifier les colonnes nécessaires
required_cols = ["longitude", "latitude"]
missing_cols = [col for col in required_cols if col not in df_soil.columns]
if missing_cols:
    raise ValueError(f"Colonnes manquantes dans le DataFrame : {missing_cols}")

# 🌐 Créer le GeoDataFrame
gdf_soil = gpd.GeoDataFrame(
    df_soil,
    geometry=gpd.points_from_xy(df_soil["longitude"], df_soil["latitude"]),
    crs="EPSG:4326"
)

# 💾 Exporter vers GeoJSON
output_path = "isdasoil_points.geojson"
gdf_soil.to_file(output_path, driver="GeoJSON")

print(f"✅ Export terminé : {output_path}")
