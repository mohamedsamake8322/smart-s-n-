import os
import dask.dataframe as dd

# 📌 Mapping pays (à adapter selon ton contexte)
country_mapping = {
    "Algérie": "Algeria", "Angola": "Angola", "Bénin": "Benin", "Botswana": "Botswana",
    "Burkina Faso": "Burkina Faso", "Burundi": "Burundi", "Cabo Verde": "Cape Verde",
    "Cameroun": "Cameroon", "République centrafricaine": "CAR", "Tchad": "Chad",
    "Comores": "Comoros", "République du Congo": "Congo", "République démocratique du Congo": "DR Congo",
    "Côte d'Ivoire": "Ivory Coast", "Djibouti": "Djibouti", "Égypte": "Egypt",
    "Guinée équatoriale": "Equatorial Guinea", "Érythrée": "Eritrea", "Eswatini": "Swaziland",
    "Éthiopie": "Ethiopia", "Gabon": "Gabon", "Gambie": "The Gambia", "Ghana": "Ghana",
    "Guinée": "Guinea", "Guinée-Bissau": "Guinea Bissau", "Kenya": "Kenya", "Lesotho": "Lesotho",
    "Libéria": "Liberia", "Libye": "Libya", "Madagascar": "Madagascar", "Malawi": "Malawi",
    "Mali": "Mali", "Mauritanie": "Mauritania", "Maurice": "Mauritius", "Maroc": "Morocco",
    "Mozambique": "Mozambique", "Namibie": "Namibia", "Niger": "Niger", "Nigéria": "Nigeria",
    "Rwanda": "Rwanda", "Sao Tomé-et-Principe": "Sao Tome and Principe", "Sénégal": "Senegal",
    "Seychelles": "Seychelles", "Sierra Leone": "Sierra Leone", "Somalie": "Somalia",
    "Afrique du Sud": "South Africa", "Soudan du Sud": "South Sudan", "Soudan": "Sudan",
    "Tanzanie": "Tanzania", "Togo": "Togo", "Tunisie": "Tunisia", "Ouganda": "Uganda",
    "Zambie": "Zambia", "Zimbabwe": "Zimbabwe",
}

# ✅ Nettoyage et standardisation des colonnes
def clean_dask_df(df, name):
    df = df.rename(columns=lambda x: x.strip().replace(' ', '_'))
    df = df.rename(columns={
        'Year_Code': 'Year',
        'Area': 'ADM0_NAME',
        'Area_Code_(M49)': 'ADM0_CODE'
    })
    print(f"📋 Colonnes dans {name} : {list(df.columns)}")

    if 'ADM0_NAME' in df.columns:
        df['ADM0_NAME'] = df['ADM0_NAME'].map(country_mapping).fillna(df['ADM0_NAME'], meta=('ADM0_NAME', 'object'))
    if 'Year' in df.columns:
        df['Year'] = dd.to_numeric(df['Year'], errors='coerce')
    return df

# 🔗 Fusion progressive avec filtrage
def fusion_progressive(dfs):
    required_cols = {"ADM0_NAME", "Year"}
    dfs_valid = [df for df in dfs if required_cols.issubset(set(df.columns))]
    print(f"\n🔗 Fusion de {len(dfs_valid)} blocs sur {len(dfs)}")
    fused = dfs_valid[0]
    for df in dfs_valid[1:]:
        fused = fused.merge(df, how="outer", on=["ADM0_NAME", "Year"])
    return fused

# 📂 Chargement des fichiers
def charger_csv(path, name):
    try:
        df = dd.read_csv(path, dtype={'Item_Code_(CPC)': 'object'}, assume_missing=True)
        df = clean_dask_df(df, name)
        print(f"✅ {name} chargé avec {len(df):,} lignes")
        return df
    except Exception as e:
        print(f"❌ Erreur chargement {name} : {e}")
        return None

# 📁 Liste des fichiers à charger
fichiers = {
    "chirps": "data/chirps.csv",
    "nutrient_balance": "data/nutrient_balance.csv",
    "trade_matrix": "data/trade_matrix.csv",
    "fert_nutrient": "data/fert_nutrient.csv",
    "fert_product": "data/fert_product.csv",
    "gedi": "data/gedi.csv",
    "land_cover": "data/land_cover.csv",
    "land_use": "data/land_use.csv",
    "smap": "data/smap.csv",
    "production": "data/production.csv",
    "manure": "data/manure.csv",
    "resources": "data/resources.csv"
}

# 📦 Chargement des DataFrames
dfs = []
for name, path in fichiers.items():
    df = charger_csv(path, name)
    if df is not None:
        dfs.append(df)

# 🔗 Fusion finale
df_final = fusion_progressive(dfs)
df_final_pd = df_final.compute()

# 💾 Sauvegarde
output_path = "output/fusion_agriculture.csv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
df_final_pd.to_csv(output_path, index=False)
print(f"\n💾 Fichier fusionné sauvegardé dans : {output_path}")

# 📊 Rapport final
print("\n📊 Résumé du fichier fusionné :")
print(f"- Nombre de lignes : {len(df_final_pd):,}")
print(f"- Nombre de colonnes : {len(df_final_pd.columns)}")
print(f"- Taille approximative : {round(os.path.getsize(output_path) / (1024**2), 2)} MB")
print(f"- Colonnes : {list(df_final_pd.columns)}")
