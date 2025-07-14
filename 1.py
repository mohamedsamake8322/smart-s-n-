import geopandas as gpd
import pandas as pd
import os

# 📁 Dossier contenant tous les GeoJSON par pays
path = "gadm_africa_geojson"
geojson_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".geojson")]

# 🔄 Fusion des GeoJSON
gdfs = [gpd.read_file(f) for f in geojson_files]
merged = pd.concat(gdfs, ignore_index=True)

# 📊 Infos
print(f"🔗 Total entités fusionnées : {len(merged)}")
# merged.plot()  # facultatif si tu veux visualiser

# 📂 Chemin d'export structuré
export_dir = "data/geo"
os.makedirs(export_dir, exist_ok=True)
output_path = os.path.join(export_dir, "africa_admin_level2.geojson")

# 💾 Sauvegarde du fichier fusionné
merged.to_file(output_path, driver="GeoJSON")
print(f"✅ Fichier fusionné sauvegardé ici : {output_path}")
