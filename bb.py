#
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import tqdm

# Chargement du fichier CSV
df_sol = pd.read_csv("soil_profile_africa_reprojected.csv")

# Création de la géométrie à partir des coordonnées
geometry = [Point(xy) for xy in zip(df_sol['Longitude'], df_sol['Latitude'])]
gdf_sol = gpd.GeoDataFrame(df_sol, geometry=geometry, crs="EPSG:4326")

# Chargement du shapefile des pays africains (à télécharger au préalable)
# Exemple : shapefile du continent africain issu de Natural Earth (ne_10m_admin_0_countries)
africa = gpd.read_file("africa_countries.shp")  # Assure-toi que ce fichier contient les pays africains

# Jointure spatiale pour associer chaque point à son pays
gdf_sol_with_country = gpd.sjoin(gdf_sol, africa[['ADMIN', 'geometry']], how="left", predicate="intersects")
gdf_sol_with_country.rename(columns={"ADMIN": "Country"}, inplace=True)

# Sauvegarde du fichier enrichi
gdf_sol_with_country.drop(columns="geometry").to_csv("soil_profile_africa_with_country.csv", index=False)

print("✅ Fichier enrichi avec les pays sauvegardé sous : soil_profile_africa_with_country.csv")
