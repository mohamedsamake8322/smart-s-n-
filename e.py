#💻 Script proposé : aggregate_meteo_seasonal.py
import pandas as pd

def aggregate_meteo_by_season(df_csv, output_csv="soil_weather_engrais_aggregated.csv"):
    df = pd.read_csv(df_csv)
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce')
    df['Month'] = df['DATE'].dt.month
    df['Year'] = df['DATE'].dt.year

    # 🌱 Définir saison
    df['Season'] = df['Month'].apply(lambda m: 'Apr–Sep' if 4 <= m <= 9 else 'Oct–Mar')

    # 🧪 Variables météo à agréger
    meteo_vars = [col for col in df.columns if col not in ['Country', 'Latitude', 'Longitude', 'DATE', 'Month', 'Year', 'Season'] and df[col].dtype in ['float64', 'int64']]

    # 🔗 Grouper par position + année + saison
    group_cols = ['Country', 'Latitude', 'Longitude', 'Year', 'Season']
    agg_df = df.groupby(group_cols)[meteo_vars].agg(['mean', 'max', 'min', 'std'])

    # 🧼 Aplatir les colonnes multi-index
    agg_df.columns = ['{}_{}'.format(var, stat) for var, stat in agg_df.columns]
    agg_df = agg_df.reset_index()

    # 💾 Sauvegarde
    agg_df.to_csv(output_csv, index=False)
    print(f"✅ Agrégation météo par saison terminée : {output_csv}")

    return agg_df

# 🔧 Exemple d’usage
aggregate_meteo_by_season("soil_weather_engrais_joined.csv")
