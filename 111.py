import geopandas as gpd
from pathlib import Path

# Chemin d'entrée
input_path = Path(r"C:\Users\moham\Music\Album 4\geoBoundariesCGAZ_ADM0.geojson")

# Chemin de sortie
output_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries\ADM0")
output_dir.mkdir(parents=True, exist_ok=True)

# Charger le fichier GeoJSON
print("📥 Chargement du fichier global...")
gdf = gpd.read_file(input_path)
print(f"✅ Fichier chargé : {len(gdf)} entités trouvées.")

# Liste des pays uniques
countries = gdf["shapeName"].unique()
print(f"🌍 {len(countries)} pays à exporter...\n")

# Exporter chaque pays
for i, country_name in enumerate(countries, 1):
    print(f"🔄 [{i}/{len(countries)}] Export de : {country_name}")
    country_gdf = gdf[gdf["shapeName"] == country_name]
    filename = f"{country_name.replace(' ', '_')}.geojson"
    country_gdf.to_file(output_dir / filename, driver="GeoJSON")

print("\n✅ Export terminé : tous les pays ADM0 sont enregistrés.")
