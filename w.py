import pandas as pd
from sklearn.neighbors import KDTree
import numpy as np

def join_soil_weather(soil_csv, weather_csv, max_distance_km=5):
    # 🔹 Charger les fichiers
    soil_df = pd.read_csv(soil_csv)
    weather_df = pd.read_csv(weather_csv)

    # 🔹 Conversion sécurisée des coordonnées en float
    soil_df['Latitude'] = pd.to_numeric(soil_df['Latitude'], errors='coerce')
    soil_df['Longitude'] = pd.to_numeric(soil_df['Longitude'], errors='coerce')
    weather_df['Latitude'] = pd.to_numeric(weather_df['Latitude'], errors='coerce')
    weather_df['Longitude'] = pd.to_numeric(weather_df['Longitude'], errors='coerce')

    # 🔹 Supprimer les lignes avec coordonnées manquantes
    soil_df = soil_df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    weather_df = weather_df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)

    # 🔹 Garder seulement les colonnes météo utiles
    exclude_cols = ['Country', 'DATE']
    weather_vars = [col for col in weather_df.columns if col not in exclude_cols]
    weather_subset = weather_df[weather_vars + ['Latitude', 'Longitude']]

    # 🔹 Préparer les tableaux de coordonnées
    soil_coords = soil_df[['Latitude', 'Longitude']].to_numpy()
    weather_coords = weather_subset[['Latitude', 'Longitude']].to_numpy()

    # 🔹 Vérification des dimensions
    if soil_coords.shape[1] != weather_coords.shape[1]:
        raise ValueError(f"❌ Dimensions non compatibles : sol {soil_coords.shape[1]} vs météo {weather_coords.shape[1]}")

    # 🔹 Construction du KDTree
    tree = KDTree(weather_coords, metric='euclidean')

    # 🔹 Recherche du point météo le plus proche
    distances, indices = tree.query(soil_coords, k=1)

    # 🔹 Filtrer selon la distance maximale (en degrés ≈ km / 111)
    threshold_deg = max_distance_km / 111.0
    matched = distances[:, 0] <= threshold_deg

    if not np.any(matched):
        print("⚠️ Aucun point météo à moins de", max_distance_km, "km des points sol.")
        return pd.DataFrame()

    # 🔹 Fusionner les points appariés
    soil_df_matched = soil_df[matched].reset_index(drop=True)
    weather_matched = weather_subset.iloc[indices[matched, 0]].reset_index(drop=True)
    combined_df = pd.concat([soil_df_matched, weather_matched], axis=1)

    # 🔹 Sauvegarde du fichier fusionné
    combined_df.to_csv("soil_weather_africa_joined.csv", index=False)
    print(f"✅ Fusion sol + météo réussie : {len(combined_df)} points appariés")

    return combined_df

# 🔧 Exemple d’usage
soil_weather = join_soil_weather(
    r"soil_profile_africa_reprojected.csv",
    r"weather_africa_cleaned_filtered.csv",
    max_distance_km=5
)
