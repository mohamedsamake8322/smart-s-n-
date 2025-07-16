#💻 Script : Fusion sol-météo avec engrais NPK + types
import pandas as pd

def fusion_fertilisation_complete(
    soil_weather_csv,
    npk_kgha_csv,
    engrais_type_csv,
    output_path="soil_weather_engrais_joined.csv"
):
    # 📥 Charger tous les fichiers
    df_soil_weather = pd.read_csv(soil_weather_csv)
    df_npk = pd.read_csv(npk_kgha_csv)
    df_engrais_type = pd.read_csv(engrais_type_csv)

    # 🧼 Nettoyer les colonnes pays + année
    df_soil_weather['Country'] = df_soil_weather['Country'].str.strip()
    df_soil_weather['Year'] = pd.to_numeric(df_soil_weather['DATE'].str[:4], errors='coerce')  # extrait l'année depuis la date

    df_npk['Area'] = df_npk['Area'].str.strip()
    df_npk['Year'] = pd.to_numeric(df_npk['Year'], errors='coerce')

    df_engrais_type['Area'] = df_engrais_type['Area'].str.strip()
    df_engrais_type['Year'] = pd.to_numeric(df_engrais_type['Year'], errors='coerce')

    # 🔗 Fusion sol+météo avec NPK kg/ha (production + import séparés si besoin)
    df_npk_total = df_npk.groupby(['Area', 'Year'])['kg_per_ha'].sum().reset_index()
    df_npk_total = df_npk_total.rename(columns={'Area': 'Country', 'kg_per_ha': 'NPK_total_kgha'})

    df_master = pd.merge(df_soil_weather, df_npk_total, on=['Country', 'Year'], how='left')

    # 🔗 Fusion avec type d'engrais
    df_engrais_type = df_engrais_type.rename(columns={'Area': 'Country'})
    df_master = pd.merge(df_master, df_engrais_type, on=['Country', 'Year'], how='left')

    # 💾 Sauvegarde
    df_master.to_csv(output_path, index=False)
    print(f"✅ Fusion fertilisation complète terminée : {output_path}")

    return df_master

# 🔧 Exemple d’usage
fusion_fertilisation_complete(
    r"C:\plateforme-agricole-complete-v2\soil_weather_africa_joined.csv",
    r"C:\plateforme-agricole-complete-v2\engrais_nutriment_kgha.csv",
    r"C:\plateforme-agricole-complete-v2\engrais_produit_encoded.csv"
)
