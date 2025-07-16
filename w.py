import pandas as pd
from sklearn.neighbors import KDTree
import numpy as np

def join_soil_weather(soil_csv, weather_csv, max_distance_km=5):
    print("📥 Chargement des données...")
    soil_df = pd.read_csv(soil_csv)
    weather_df = pd.read_csv(weather_csv)

    # 🔹 Conversion des coordonnées en float
    for df in [soil_df, weather_df]:
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    # 🔹 Suppression des lignes invalides
    soil_df = soil_df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    weather_df = weather_df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)

    print(f"✅ Points sol valides : {len(soil_df)}")
    print(f"✅ Points météo valides : {len(weather_df)}")

    # 🔹 Séparer les coordonnées météo pour le KDTree
    weather_coords = weather_df[['Latitude', 'Longitude']].to_numpy()

    # 🔹 Vérification des dimensions
    soil_coords = soil_df[['Latitude', 'Longitude']].to_numpy()
    if soil_coords.shape[1] != weather_coords.shape[1]:
        raise ValueError(f"❌ Dimensions non compatibles : sol {soil_coords.shape[1]} vs météo {weather_coords.shape[1]}")

    # 🔹 Construire le KDTree
    print("🌐 Construction du KDTree et appariement...")
    tree = KDTree(weather_coords, metric='euclidean')
    distances, indices = tree.query(soil_coords, k=1)

    # 🔹 Filtrer selon la distance max
    threshold_deg = max_distance_km / 111.0
    matched = distances[:, 0] <= threshold_deg
    print(f"🔍 Points appariés dans rayon de {max_distance_km} km : {np.sum(matched)}")

    if not np.any(matched):
        print("⚠️ Aucun appariement dans la distance spécifiée.")
        return pd.DataFrame()

    # 🔹 Séparer les lignes sol et météo appariées
    soil_df_matched = soil_df[matched].reset_index(drop=True)
    weather_df_matched = weather_df.iloc[indices[matched, 0]].reset_index(drop=True)

    # 🔹 Fusionner les deux
    combined_df = pd.concat([soil_df_matched, weather_df_matched.drop(columns=['Latitude', 'Longitude'])], axis=1)

    # 🔹 Sauvegarder
    output_path = "soil_weather_africa_joined.csv"
    combined_df.to_csv(output_path, index=False)
    print(f"✅ Fusion réussie. Fichier exporté : {output_path}")

    return combined_df

# 🔧 Exemple d’usage
if __name__ == "__main__":
    soil_weather = join_soil_weather(
        r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa_reprojected.csv",
        r"C:\plateforme-agricole-complete-v2\weather_africa_cleaned_filtered.csv",
        max_distance_km=5
    )
