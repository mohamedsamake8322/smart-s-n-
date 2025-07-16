#💻 Script proposé : fusion multi-pays sol + météo + fertilisation
import pandas as pd

def fusion_multi_pays(
    soil_weather_csv,
    engrais_npk_csv,
    engrais_types_csv,
    output_path="soil_weather_engrais_joined_extended.csv",
    annees_ciblees=None  # ex: [2015, 2016, ..., 2023]
):
    # 📥 Charger fichiers
    df_main = pd.read_csv(soil_weather_csv)
    df_npk = pd.read_csv(engrais_npk_csv)
    df_types = pd.read_csv(engrais_types_csv)

    # 🧼 Nettoyer clés
    df_main['Country'] = df_main['Country'].str.strip()
    df_main['Year'] = pd.to_numeric(df_main['DATE'].str[:4], errors='coerce')

    df_npk['Area'] = df_npk['Area'].str.strip()
    df_npk['Year'] = pd.to_numeric(df_npk['Year'], errors='coerce')
    df_npk = df_npk.groupby(['Area', 'Year'])['kg_per_ha'].sum().reset_index()
    df_npk = df_npk.rename(columns={'Area': 'Country', 'kg_per_ha': 'NPK_total_kgha'})

    df_types['Area'] = df_types['Area'].str.strip()
    df_types['Year'] = pd.to_numeric(df_types['Year'], errors='coerce')
    df_types = df_types.rename(columns={'Area': 'Country'})

    # 📅 Filtrer si liste d’années cible fournie
    if annees_ciblees:
        df_main = df_main[df_main['Year'].isin(annees_ciblees)]
        df_npk = df_npk[df_npk['Year'].isin(annees_ciblees)]
        df_types = df_types[df_types['Year'].isin(annees_ciblees)]

    # 🔗 Fusion fertilisation
    df = pd.merge(df_main, df_npk, on=['Country', 'Year'], how='left')
    df = pd.merge(df, df_types, on=['Country', 'Year'], how='left')

    # 💾 Sauvegarde
    df.to_csv(output_path, index=False)
    print(f"✅ Fusion multi-pays complétée : {output_path}")
    print(f"📊 Pays inclus : {df['Country'].nunique()}, années : {sorted(df['Year'].dropna().unique())}")

    return df

# 🔧 Exemple d’usage :
fusion_multi_pays(
    soil_weather_csv=r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_aggregated.csv",  # ton fichier météo-sol élargi
    engrais_npk_csv=r"C:\plateforme-agricole-complete-v2\engrais_nutriment_kgha.csv",
    engrais_types_csv=r"C:\plateforme-agricole-complete-v2\engrais_produit_encoded.csv",
    annees_ciblees=list(range(2015, 2024))
)
