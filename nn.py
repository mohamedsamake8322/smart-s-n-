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
    # 🧱 Charger le sol
    df_sol = pd.read_csv(fichier_sol)
    df_sol['Longitude'] = pd.to_numeric(df_sol['Longitude'], errors='coerce').round(4)
    df_sol['Latitude'] = pd.to_numeric(df_sol['Latitude'], errors='coerce').round(4)
    df_sol = df_sol.dropna(subset=['Longitude', 'Latitude'])
    df_sol_prefixed = df_sol.add_prefix("soil_")

    # 📍 Construire arbre spatial
    sol_coords = df_sol_prefixed[['soil_Longitude', 'soil_Latitude']].values
    tree = cKDTree(sol_coords)

    # 📦 Traiter chaque fichier météo
    all_dfs = []
    for file in os.listdir(folder_meteo):
        if not file.endswith(".csv"):
            continue
        path = os.path.join(folder_meteo, file)

        try:
            df_met = pd.read_csv(path)
            if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
                print(f"❌ {file} : Colonnes essentielles manquantes, ignoré")
                continue

            df_met['Longitude'] = pd.to_numeric(df_met['Longitude'], errors='coerce').round(4)
            df_met['Latitude']  = pd.to_numeric(df_met['Latitude'], errors='coerce').round(4)
            df_met = df_met.dropna(subset=['Longitude', 'Latitude'])

            met_coords = df_met[['Longitude', 'Latitude']].values

            # 🧪 Matching spatial
            dist, idx = tree.query(met_coords, distance_upper_bound=max_distance_deg)
            valid = dist < max_distance_deg
            if valid.sum() == 0:
                print(f"⚠️ {file} : aucun point météo matché avec le sol")
                continue

            df_met_valid = df_met.iloc[np.where(valid)[0]].reset_index(drop=True)
            df_sol_match = df_sol_prefixed.iloc[idx[valid]].reset_index(drop=True)

            df_fusion = pd.concat([df_sol_match, df_met_valid], axis=1)
            all_dfs.append(df_fusion)

            pays = df_met_valid['Country'].unique()
            print(f"✅ {file} fusionné : {len(df_met_valid)} points | Pays : {', '.join(pays)}")

        except Exception as e:
            print(f"🔥 Erreur dans {file} : {e}")

    # 📊 Concaténation finale
    df_final = pd.concat(all_dfs, ignore_index=True)
    df_final.to_csv(output_path, index=False)

    print(f"\n✅ Fusion météo-sol continentale terminée → {output_path}")
    print(f"📌 Points couverts : {len(df_final)} | Pays inclus : {df_final['Country'].nunique()}")

    return df_final

# 🔧 Exemple d’usage :
fusion_meteo_sol_continental(
    folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned",
    fichier_sol  = r"C:\plateforme-agricole-complete-v2\soil_profile_africa_reprojected.csv"
)
