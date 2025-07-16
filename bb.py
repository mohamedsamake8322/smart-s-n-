import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 📥 Chargement du fichier CSV
df_sol = pd.read_csv("soil_profile_africa_reprojected.csv")

# 🧭 Création des points géographiques
geometry = [Point(xy) for xy in zip(df_sol['Longitude'], df_sol['Latitude'])]
gdf_sol = gpd.GeoDataFrame(df_sol, geometry=geometry, crs="EPSG:4326")

try:
    # 🗺️ Chargement du shapefile
    shapefile_path = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp"
    africa = gpd.read_file(shapefile_path)

    print("🔎 Colonnes disponibles :", africa.columns.tolist())

    # 🌍 Filtrage des pays africains par la colonne 'CONTINENT'
    if 'CONTINENT' in africa.columns:
        africa = africa[africa['CONTINENT'] == 'Africa']
    else:
        raise KeyError("La colonne 'CONTINENT' est introuvable dans le shapefile.")

    # 🔁 Jointure spatiale en utilisant la colonne correcte ('ADMIN')
    gdf_sol_with_country = gpd.sjoin(
        gdf_sol,
        africa[['ADMIN', 'geometry']],
        how="left",
        predicate="intersects"
    )

    # 📛 Renommage
    gdf_sol_with_country.rename(columns={"ADMIN": "Country"}, inplace=True)

    # 💾 Sauvegarde du fichier enrichi
    gdf_sol_with_country.drop(columns="geometry").to_csv("soil_profile_africa_with_country.csv", index=False)

    print("✅ Fichier enrichi avec les pays sauvegardé sous : soil_profile_africa_with_country.csv")

except Exception as e:
    print(f"❌ Une erreur s’est produite : {e}")
