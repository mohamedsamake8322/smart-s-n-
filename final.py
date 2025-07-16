import pandas as pd
import os
from scipy.spatial import cKDTree
import numpy as np

# 🧠 Table d'alias météo → noms sol attendus
alias_map = {
    "Angola": ["Angola"],
    "Benin": ["Benin", "Bénin", "Republic of Benin"],
    "Burkina": ["Burkina Faso"],
    "Cameroon": ["Cameroon", "Cameroun"],
    "Chad": ["Chad"],
    "Congo": ["Congo", "Republic of the Congo", "Democratic Republic of the Congo"],
    "Djibouti": ["Djibouti"],
    "Egypt": ["Egypt", "Arab Republic of Egypt"],
    "Equatorial": ["Equatorial Guinea"],
    "Ethiopia": ["Ethiopia"],
    "Gabon": ["Gabon"],
    "Gambia": ["Gambia", "The Gambia"],
    "Ghana": ["Ghana"],
    "Guinea": ["Guinea", "Guinea-Bissau"],
    "Ivory": ["Côte d'Ivoire", "Ivory Coast"],
    "Kenya": ["Kenya"],
    "Malawi": ["Malawi"],
    "Malaysia": [],  # À exclure
    "Mali": ["Mali"],
    "Mauritania": ["Mauritania"],
    "Morocco": ["Morocco", "Maroc"],
    "Mozambique": ["Mozambique"],
    "Namibia": ["Namibia"],
    "Niger": ["Niger"],
    "Nigeria": ["Nigeria"],
    "Senegal": ["Senegal"],
    "South": ["South Africa"],
    "Sudan": ["Sudan"],
    "Tanzania": ["Tanzania"],
    "Togo": ["Togo"],
    "Uganda": ["Uganda"],
    "Zambia": ["Zambia"],
    "Zimbabwe": ["Zimbabwe"]
}

def match_country(sol_df, meteo_name):
    aliases = alias_map.get(meteo_name, [meteo_name])
    return sol_df[sol_df['Country'].apply(lambda x: any(alias.lower() in str(x).lower() for alias in aliases))]

def fusion_meteo_sol_continental(folder_meteo, fichier_sol, output_path="soil_weather_africa_joined.csv", max_distance_deg=0.1):
    df_sol_all = pd.read_csv(fichier_sol)
    df_sol_all['soil_Longitude'] = pd.to_numeric(df_sol_all['Longitude'], errors='coerce').round(4)
    df_sol_all['soil_Latitude']  = pd.to_numeric(df_sol_all['Latitude'], errors='coerce').round(4)
    df_sol_all = df_sol_all.dropna(subset=['soil_Longitude', 'soil_Latitude'])

    all_dfs = []

    for file in os.listdir(folder_meteo):
        if not file.endswith(".csv"):
            continue
        meteo_nom = file.replace("weather_", "").replace(".csv", "")
        path = os.path.join(folder_meteo, file)

        try:
            df_met = pd.read_csv(path)
            if not {'Longitude', 'Latitude', 'Country', 'DATE'}.issubset(df_met.columns):
                print(f"❌ {file} : colonnes essentielles manquantes, ignoré")
                continue

            df_met['Longitude'] = pd.to_numeric(df_met['Longitude'], errors='coerce').round(4)
            df_met['Latitude']  = pd.to_numeric(df_met['Latitude'], errors='coerce').round(4)
            df_met = df_met.dropna(subset=['Longitude', 'Latitude'])

            if df_met.empty:
                print(f"❌ {file} : 0 point météo")
                continue

            df_sol_match = match_country(df_sol_all, meteo_nom)
            if df_sol_match.empty:
                print(f"⚠️ {file} → Aucun point sol trouvé pour : {meteo_nom}")
                continue

            tree = cKDTree(df_sol_match[['soil_Longitude', 'soil_Latitude']].values)
            met_coords = df_met[['Longitude', 'Latitude']].values
            dist, idx = tree.query(met_coords, distance_upper_bound=max_distance_deg)

            valid = dist < max_distance_deg
            if valid.sum() == 0:
                print(f"⚠️ {file} : aucun point météo matché à {max_distance_deg}°")
                continue

            df_met_valid = df_met.iloc[np.where(valid)[0]].reset_index(drop=True)
            df_sol_valid = df_sol_match.iloc[idx[valid]].reset_index(drop=True)

            df_fusion = pd.concat([df_sol_valid, df_met_valid], axis=1)
            pays_fusionnes = df_met_valid['Country'].unique()
            print(f"✅ {file} fusionné : {len(df_met_valid)} points | Pays : {', '.join(pays_fusionnes)}")

            all_dfs.append(df_fusion)

        except Exception as e:
            print(f"🔥 Erreur dans {file} : {e}")

    # 🔄 Fusion finale
    all_dfs = [df.reset_index(drop=True) for df in all_dfs]
    if all_dfs:
        df_final = pd.concat(all_dfs, ignore_index=True)
        df_final.to_csv(output_path, index=False)
        print(f"\n✅ Fusion continentale terminée → {output_path}")
        print(f"📌 Points couverts : {len(df_final)} | Pays inclus : {df_final['Country'].nunique()}")
        return df_final
    else:
        print("❌ Aucun fichier météo fusionné.")
        return pd.DataFrame()
