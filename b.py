import pandas as pd

def charger_csv(path):
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1")

def fusionner_csv(file1, file2, output_file, keys=None):
    # Charger
    df1 = charger_csv(file1)
    df2 = charger_csv(file2)

    # Renommer pour compatibilité
    rename_map = {"adm2_id": "ADM2_ID", "Year": "year", "VALUE": "value"}
    df1.rename(columns=rename_map, inplace=True)
    df2.rename(columns=rename_map, inplace=True)

    # Si les clés ne sont pas précisées, essayer ADM2_ID + year
    if keys is None:
        possibles = ["ADM2_ID", "year"]
        keys = [k for k in possibles if k in df1.columns and k in df2.columns]

    if not keys:
        print(f"⚠️ Pas de clés communes entre {file1} et {file2}")
        return None

    print(f"🔑 Fusion sur : {keys}")

    # Forcer les types en str pour éviter les erreurs
    for k in keys:
        df1[k] = df1[k].astype(str)
        df2[k] = df2[k].astype(str)

    # Fusion
    merged = pd.merge(df1, df2, on=keys, how="inner")

    # Sauvegarde
    merged.to_csv(output_file, index=False)
    print(f"✅ Fusion terminée : {output_file} ({len(merged)} lignes)")

    return merged


# Exemple Soil + MODIS
fusionner_csv(
    r"C:\Users\moham\Music\Moh\fusion_completesoil.csv",
    r"C:\Users\moham\Music\Moh\MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv",
    r"C:\Users\moham\Music\Moh\fusion_soil_modis.csv"
)

# Exemple SPEI + WAPOR
fusionner_csv(
    r"C:\Users\moham\Music\Moh\SPEI_Mali_ADM2_20250821_1546.csv",
    r"C:\Users\moham\Music\Moh\WAPOR_fusion_long_clean_clean.csv",
    r"C:\Users\moham\Music\Moh\fusion_spei_wapor.csv"
)
