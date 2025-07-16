#💻 Script : Fusion finale pour modélisation continentale
import pandas as pd

def fusion_final_rendement_model(
    meteo_ferti_csv,
    rendement_csv,
    output_path="dataset_rendement_model_extended.csv"
):
    # 📥 Charger les jeux
    df_meteo = pd.read_csv(meteo_ferti_csv)
    df_rendement = pd.read_csv(rendement_csv)

    # 🧼 Nettoyer les clés
    df_meteo['Country'] = df_meteo['Country'].astype(str).str.strip()
    df_meteo['Year'] = pd.to_numeric(df_meteo['Year'], errors='coerce')

    df_rendement['Country'] = df_rendement['Country'].astype(str).str.strip()
    df_rendement['Year'] = pd.to_numeric(df_rendement['Year'], errors='coerce')
    df_rendement['CropName'] = df_rendement['CropName'].astype(str).str.strip()

    # 🔗 Fusion par pays + année
    df_merged = pd.merge(
        df_meteo, df_rendement,
        on=['Country', 'Year'],
        how='left'
    )

    # 💾 Export
    df_merged.to_csv(output_path, index=False)
    print(f"\n✅ Fusion finale terminée → {output_path}")
    print(f"📊 Lignes : {len(df_merged)} | Pays : {df_merged['Country'].nunique()} | Années : {sorted(df_merged['Year'].dropna().unique())}")

    return df_merged

# 🔧 Exemple d’usage :
fusion_final_rendement_model(
    meteo_ferti_csv=r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_aggregated_extended.csv",
    rendement_csv=r"C:\plateforme-agricole-complete-v2\culture_rendement_afrique.csv"
)
