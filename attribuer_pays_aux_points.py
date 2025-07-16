import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

def attribuer_pays_aux_points(
    fichier_points,
    shapefile_pays,
    output_path="soil_profile_africa_with_country.csv"
):
    # 📥 Charger les points sol bruts
    df = pd.read_csv(fichier_points)
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df = df.dropna(subset=['Longitude', 'Latitude'])

    # 🌍 Créer les géométries des points
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df['Longitude'], df['Latitude'])],
        crs="EPSG:4326"
    )

    # 🗺️ Charger shapefile des pays (Natural Earth)
    gdf_pays = gpd.read_file(shapefile_pays)
    gdf_pays = gdf_pays.to_crs("EPSG:4326")  # reprojecte si nécessaire

    # 🔗 Spatial join
    gdf_joined = gpd.sjoin(
        gdf_points,
        gdf_pays[['ADMIN', 'geometry']],
        how="left",
        predicate="intersects"
    )
    gdf_joined.rename(columns={"ADMIN": "Country"}, inplace=True)

    # 🧼 Nettoyage & export
    gdf_joined.drop(columns=['geometry', 'index_right'], errors='ignore').to_csv(output_path, index=False)

    print(f"✅ Fichier enrichi enregistré : {output_path}")
    print(f"🌍 Pays détectés : {gdf_joined['Country'].nunique()}")
    print(gdf_joined['Country'].value_counts().head())

# 🔧 Exemple d’usage
attribuer_pays_aux_points(
    fichier_points = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv",
    shapefile_pays = r"C:\Users\moham\Documents\naturalearth_lowres\ne_110m_admin_0_countries.shp",
    output_path = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_with_country.csv"
)
