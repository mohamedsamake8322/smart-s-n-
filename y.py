#💻 Script : Extraction du rendement FAO (kg/ha)
import pandas as pd

def extract_rendement_fao(crop_csv, output_csv="culture_rendement_afrique.csv"):
    # 📥 Charger le fichier brut FAO cultures
    df = pd.read_csv(crop_csv, header=None)
    df.columns = ['dummy1', 'AreaCode', 'Country', 'ItemCode', 'CropCode', 'CropName',
                  'ElementCode', 'Element', 'YearCode', 'Year', 'Unit', 'Value', 'Flag', 'Note']

    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Country'] = df['Country'].str.strip()
    df['CropName'] = df['CropName'].str.strip()

    # 🔹 Séparer les lignes de production et de surface
    df_prod = df[df['Element'] == 'Production']
    df_area = df[df['Element'] == 'Area harvested']

    # 🔗 Fusion des deux par pays, année, culture
    df_merged = pd.merge(
        df_prod[['Country', 'Year', 'CropName', 'Value']],
        df_area[['Country', 'Year', 'CropName', 'Value']],
        on=['Country', 'Year', 'CropName'],
        suffixes=('_production_tonnes', '_area_ha'),
        how='inner'
    )

    # 🧪 Calcul du rendement kg/ha
    df_merged['Yield_kg_ha'] = (df_merged['Value_production_tonnes'] * 1000) / df_merged['Value_area_ha']

    # 💾 Sauvegarde
    df_merged.to_csv(output_csv, index=False)
    print(f"✅ Rendements extraits et calculés : {output_csv}")

    return df_merged

# 🔧 Exemple d’usage
extract_rendement_fao(
    r"C:\plateforme-agricole-complete-v2\Boua\Production_Crops_Livestock_Afrique.csv"
)
