import os
import pandas as pd
import re

def clean_weather_file(filepath):
    df = pd.read_csv(filepath)
    if 'Longitude' in df.columns:
        df['Longitude'] = df['Longitude'].astype(str).str.replace('.csv', '', regex=False)
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')

    pattern = r'^(.*)_(-?\d+(?:\.\d+)?)$'
    melted = []

    for col in df.columns:
        match = re.match(pattern, col)
        if match:
            variable, lon = match.groups()
            subset = df[['Country', 'Latitude', 'DATE']].copy()
            subset['Longitude'] = float(lon)
            subset['Variable'] = variable
            subset['Value'] = df[col]
            melted.append(subset)

    if not melted:
        return pd.DataFrame()  # Retourner vide si le fichier est déjà propre ou non exploitable

    tidy_df = pd.concat(melted, ignore_index=True)
    clean_df = tidy_df.pivot_table(index=['Country', 'Latitude', 'Longitude', 'DATE'],
                                   columns='Variable', values='Value').reset_index()
    return clean_df


def process_weather_folder(folder_path):
    all_data = []

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            full_path = os.path.join(folder_path, filename)
            print(f"🔍 Traitement de : {filename}")
            try:
                df_clean = clean_weather_file(full_path)
                if not df_clean.empty:
                    all_data.append(df_clean)
            except Exception as e:
                print(f"⚠️ Erreur avec {filename}: {e}")

    if all_data:
        df_all_weather = pd.concat(all_data, ignore_index=True)
        df_all_weather.to_csv("weather_africa_cleaned.csv", index=False)
        print("✅ Fichier météo fusionné créé : weather_africa_cleaned.csv")
        return df_all_weather
    else:
        print("🚫 Aucun fichier météo exploitable trouvé.")
        return None

# Exemple d’usage :
weather_df = process_weather_folder(r"C:\plateforme-agricole-complete-v2\weather_by_country")
