#Reprojection du fichier sol (EPSG:3857 → WGS84)
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def reproject_soil_coordinates(csv_path, epsg_input=3857, epsg_output=4326):
    # Chargement des données brutes
    df = pd.read_csv(csv_path)

    # Création de géométries avec les coordonnées x/y
    gdf = gpd.GeoDataFrame(df,
        geometry=[Point(xy) for xy in zip(df['x'], df['y'])],
        crs=f"EPSG:{epsg_input}"
    )

    # Reprojection vers WGS84
    gdf = gdf.to_crs(epsg=epsg_output)

    # Extraction des coordonnées GPS
    gdf['Longitude'] = gdf.geometry.x
    gdf['Latitude'] = gdf.geometry.y

    # Nettoyage des colonnes géo
    gdf.drop(columns=['x', 'y', 'geometry'], inplace=True)

    # Sauvegarde
    output_path = "soil_profile_africa_reprojected.csv"
    gdf.to_csv(output_path, index=False)
    print(f"✅ Fichier reprojeté sauvegardé : {output_path}")

    return gdf

# 🔧 Exemple d’usage :
soil_csv_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
soil_df = reproject_soil_coordinates(soil_csv_path)
