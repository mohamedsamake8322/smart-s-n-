#💻 Script : audit_pays_compatibles.py
import pandas as pd

def audit_pays_compatibles(
    rendement_csv,
    engrais_csv,
    meteo_csv,
    annees_ciblees=None
):
    # 📥 Charger les fichiers
    df_r = pd.read_csv(rendement_csv)
    df_e = pd.read_csv(engrais_csv)
    df_m = pd.read_csv(meteo_csv)

    # 🧼 Nettoyage des clés
    for df in [df_r, df_e, df_m]:
        df['Country'] = df.get('Country', df.get('Area', '')).astype(str).str.strip()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')

    # 📅 Filtrer par années cibles
    if annees_ciblees:
        df_r = df_r[df_r['Year'].isin(annees_ciblees)]
        df_e = df_e[df_e['Year'].isin(annees_ciblees)]
        df_m = df_m[df_m['Year'].isin(annees_ciblees)]

    # 🌍 Pays disponibles dans chaque source
    pays_r = set(df_r['Country'].unique())
    pays_e = set(df_e['Country'].unique())
    pays_m = set(df_m['Country'].unique())
    tous_pays = sorted(pays_r | pays_e | pays_m)

    rows = []
    for pays in tous_pays:
        rend = '✅' if pays in pays_r else '❌'
        fert = '✅' if pays in pays_e else '❌'
        meteo = '✅' if pays in pays_m else '❌'

        annees_r = set(df_r[df_r['Country'] == pays]['Year'].dropna())
        annees_e = set(df_e[df_e['Country'] == pays]['Year'].dropna())
        annees_m = set(df_m[df_m['Country'] == pays]['Year'].dropna())
        annees_communes = sorted(annees_r & annees_e & annees_m)

        rows.append({
            "Pays": pays,
            "Rendement FAO dispo": rend,
            "Fertilisation FAO dispo": fert,
            "Météo + sol dispo": meteo,
            "Années communes": annees_communes
        })

    audit_df = pd.DataFrame(rows)
    audit_df.to_csv("audit_compatibilite_pays.csv", index=False)
    print("\n✅ Audit terminé → audit_compatibilite_pays.csv")

    return audit_df

# 🔧 Exemple d’usage
audit_pays_compatibles(
    rendement_csv=r"C:\plateforme-agricole-complete-v2\culture_rendement_afrique.csv",
    engrais_csv=r"C:\plateforme-agricole-complete-v2\engrais_nutriment_kgha.csv",
    meteo_csv=r"C:\plateforme-agricole-complete-v2\soil_weather_engrais_joined_extended.csv",
    annees_ciblees=list(range(2015, 2024))
)
