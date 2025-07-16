#💻 Script : Fusion continentale météo + sol
import pandas as pd
import os
from scipy.spatial import cKDTree
import numpy as np

def fusion_meteo_sol_continental(
    folder_meteo,
    fichier_sol,
    output_path="soil_weather_africa_joined.csv",
    max_distance_deg=0.05  # seuil de matching spatial
):
    # 🧱 Charger sol
    df_sol = pd.read_csv(fichier_sol)
    df_sol['Longitude'] = df_sol['Longitude'].round(4)
    df_sol['Latitude'] = df_sol['Latitude'].round(4)
    sol_coords = df_sol[['Longitude', 'Latitude']].dropna().values
    tree = cKDTree(sol_coords)

    # 📦 Lire tous les fichiers météo
    all_dfs = []
    for file in os.listdir(folder_meteo):
        if not file.endswith(".csv"):
            continue
        path = os.path.join(folder_meteo, file)
        df_met = pd.read_csv(path)
        if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
            continue

        df_met['Longitude'] = df_met['Longitude'].round(4)
        df_met['Latitude'] = df_met['Latitude'].round(4)
        met_coords = df_met[['Longitude', 'Latitude']].dropna().values

        # 🧪 Matching spatial
        dist, idx = tree.query(met_coords, distance_upper_bound=max_distance_deg)
        valid = dist < max_distance_deg
        df_met_valid = df_met.iloc[np.where(valid)[0]].copy()
        df_sol_match = df_sol.iloc[idx[valid]].reset_index(drop=True)

        df_fusion = pd.concat([df_sol_match.reset_index(drop=True),
                               df_met_valid.reset_index(drop=True)],
                              axis=1)

        all_dfs.append(df_fusion)

    # 📊 Concaténer tout
    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final.to_csv(output_path, index=False)

    print(f"\n✅ Fusion météo-sol continentale terminée → {output_path}")
    print(f"📌 Points couverts : {len(df_final)} | Pays : {df_final['Country'].nunique()}")

    return df_final

# 🔧 Exemple d’usage :
fusion_meteo_sol_continental(
    folder_meteo=r"C:\plateforme-agricole-complete-v2\weather_by_country",
    fichier_sol=r"C:\plateforme-agricole-complete-v2\soil_profile_africa_reprojected.csv"
)
