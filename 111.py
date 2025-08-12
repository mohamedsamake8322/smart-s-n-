import geopandas as gpd
from pathlib import Path

# Chemin d'entrée (fichier global)
input_path = Path(r"C:\Users\moham\Music\Album 4\geoBoundariesCGAZ_ADM0.geojson")

# Chemin de sortie (dossier par pays)
output_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries\ADM0")
output_dir.mkdir(parents=True, exist_ok=True)

# Charger le fichier GeoJSON
gdf = gpd.read_file(input_path)

# Exporter chaque pays individuellement
for country_name in gdf["shapeName"].unique():
    country_gdf = gdf[gdf["shapeName"] == country_name]
    filename = f"{country_name.replace(' ', '_')}.geojson"
    country_gdf.to_file(output_dir / filename, driver="GeoJSON")

print("✅ Export terminé : chaque pays ADM0 est dans son propre fichier.")
