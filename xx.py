#💻 Script de vérification croisée : couverture pays + années
import pandas as pd

def diagnostic_couverture(ferti_meteo_csv, rendement_csv):
    # 📥 Charger les deux jeux
    df_ferti = pd.read_csv(ferti_meteo_csv)
    df_rendement = pd.read_csv(rendement_csv)

    # 🧼 Nettoyer
    df_ferti['Country'] = df_ferti['Country'].str.strip()
    df_ferti['Year'] = pd.to_numeric(df_ferti['Year'], errors='coerce')

    df_rendement['Country'] = df_rendement['Country'].str.strip()
    df_rendement['Year'] = pd.to_numeric(df_rendement['Year'], errors='coerce')

    # 📊 Pays et années présents
    pays_ferti = set(df_ferti['Country'].unique())
    pays_rendement = set(df_rendement['Country'].unique())
    pays_communs = pays_ferti & pays_rendement

    print("🌍 Nombre de pays météo+ferti :", len(pays_ferti))
    print("🌾 Nombre de pays avec rendement :", len(pays_rendement))
    print("🔗 Pays présents dans les deux :", len(pays_communs))
    print("🧾 Liste des pays communs :", sorted(pays_communs))

    # 🧭 Vérification des années croisées
    df_ferti_years = df_ferti.groupby('Country')['Year'].unique()
    df_rendement_years = df_rendement.groupby('Country')['Year'].unique()

    print("\n🕒 Exemples de couverture année par pays (météo + fertilisation vs rendement):")
    for country in sorted(pays_communs):
        y_ferti = df_ferti_years.get(country, [])
        y_rend = df_rendement_years.get(country, [])
        print(f"  ▸ {country}: meteo+ferti → {sorted(y_ferti)}, rendement → {sorted(y_rend)}")

# 🔧 Exemple d’usage :
diagnostic_couverture(
    r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_aggregated.csv",
    r"C:\plateforme-agricole-complete-v2\culture_rendement_afrique.csv"
)
