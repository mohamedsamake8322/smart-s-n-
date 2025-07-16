#💻 Script : Fusion complète pour modèle de rendement
import pandas as pd

def fusion_final_rendement_model(
    meteo_engrais_csv,
    rendement_csv,
    output_path="dataset_rendement_model.csv"
):
    # 📥 Charger météo + fertilisation agrégée
    df_meteo_ferti = pd.read_csv(meteo_engrais_csv)
    df_rendement = pd.read_csv(rendement_csv)

    # 🧼 Nettoyer les clés
    df_meteo_ferti['Country'] = df_meteo_ferti['Country'].str.strip()
    df_meteo_ferti['Year'] = pd.to_numeric(df_meteo_ferti['Year'], errors='coerce')

    df_rendement['Country'] = df_rendement['Country'].str.strip()
    df_rendement['Year'] = pd.to_numeric(df_rendement['Year'], errors='coerce')
    df_rendement['CropName'] = df_rendement['CropName'].str.strip()

    # 🔗 Fusion par pays + année (et culture si disponible ensuite)
    df_merged = pd.merge(df_meteo_ferti, df_rendement,
                         left_on=['Country', 'Year'],
                         right_on=['Country', 'Year'],
                         how='left')

    # 💾 Sauvegarde
    df_merged.to_csv(output_path, index=False)
    print(f"✅ Jeu de données prêt pour modélisation : {output_path}")

    return df_merged

# 🔧 Exemple d’usage
fusion_final_rendement_model(
    r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_aggregated.csv",
    r"C:\plateforme-agricole-complete-v2\culture_rendement_afrique.csv"
)
