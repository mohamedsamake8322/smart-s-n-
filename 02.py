import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

# 📥 1. Charger les données de sol
soil_csv_path = "C:/plateforme-agricole-complete-v2/open-soil-data/data/iSDA_soil_data.csv"
df_soil = pd.read_csv(soil_csv_path)

# 🌍 2. Charger les frontières des pays (shapefile)
countries_shp_path = "C:/plateforme-agricole-complete-v2/data/Natural Earth 110m Cultural Vectors/ne_110m_admin_0_countries.shp"
gdf_countries = gpd.read_file(countries_shp_path)

# 🧭 3. Convertir les données de sol en GeoDataFrame
df_soil['geometry'] = df_soil.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
gdf_soil = gpd.GeoDataFrame(df_soil, geometry='geometry', crs="EPSG:4326")

# 🔗 4. Spatial join : associer chaque point à un pays
gdf_joined = gpd.sjoin(gdf_soil, gdf_countries[['geometry', 'ADMIN']], how='left', predicate='within')

# 🏷️ 5. Renommer la colonne du pays
gdf_joined.rename(columns={'ADMIN': 'country'}, inplace=True)

# 🧹 6. Nettoyer et exporter en CSV
gdf_joined.drop(columns='geometry').to_csv("C:/plateforme-agricole-complete-v2/soil_data_with_country.csv", index=False)

print("✅ Fichier exporté avec les pays : soil_data_with_country.csv")
