#💻 Script : Agrégation météo par saison culturale
import pandas as pd

def aggregate_meteo_by_season(df_csv, output_csv="soil_weather_engrais_aggregated_extended.csv"):
    # 📥 Charger le jeu de données
    df = pd.read_csv(df_csv)

    # 🕒 Parse la date
    if 'DATE' not in df.columns:
        raise KeyError("❌ La colonne 'DATE' est absente. Vérifie le nom ou structure du fichier.")

    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['Month'] = df['DATE'].dt.month
    df['Year'] = df['DATE'].dt.year

    # 🌱 Définir saison culturale
    df['Season'] = df['Month'].apply(lambda m: 'Apr–Sep' if 4 <= m <= 9 else 'Oct–Mar')

    # 🔍 Identifier les variables météo numériques
    exclude_cols = ['Country', 'Latitude', 'Longitude', 'DATE', 'Month', 'Year', 'Season']
    meteo_vars = [col for col in df.columns if col not in exclude_cols and df[col].dtype in ['float64', 'int64']]

    # 📊 Agrégation par point + année + saison
    group_cols = ['Country', 'Latitude', 'Longitude', 'Year', 'Season']
    agg_df = df.groupby(group_cols)[meteo_vars].agg(['mean', 'max', 'min', 'std'])

    # 🔧 Aplatir les colonnes multi-index
    agg_df.columns = ['{}_{}'.format(var, stat) for var, stat in agg_df.columns]
    agg_df = agg_df.reset_index()

    # 💾 Sauvegarde
    agg_df.to_csv(output_csv, index=False)
    print(f"\n✅ Agrégation météo saisonnière terminée → {output_csv}")
    print(f"📊 Lignes : {len(agg_df)} | Variables météo agrégées : {len(meteo_vars)}")

    return agg_df

# 🔧 Exemple d’usage :
aggregate_meteo_by_season(r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_joined_extended.csv")
