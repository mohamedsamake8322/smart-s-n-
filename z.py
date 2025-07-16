#💻 Script : Convertir les engrais (Nutriment) en kg/ha
import pandas as pd

def convert_npk_to_kgha(nutrient_csv, crop_csv, output_path="engrais_nutriment_kgha.csv"):
    # Charger engrais par nutriment
    df_nutrient = pd.read_csv(nutrient_csv)
    df_nutrient['Value'] = pd.to_numeric(df_nutrient['Value'], errors='coerce')
    df_nutrient = df_nutrient[df_nutrient['Unit'] == 't']
    df_nutrient = df_nutrient[df_nutrient['Element'].isin(['Production', 'Import quantity'])]

    # Nettoyer les colonnes pays et année
    df_nutrient['Area'] = df_nutrient['Area'].str.strip()
    df_nutrient['Year'] = pd.to_numeric(df_nutrient['Year'], errors='coerce')

    # Charger culture (superficie récoltée)
    df_crop = pd.read_csv(crop_csv, header=None)
    df_crop.columns = ['dummy1', 'AreaCode', 'Country', 'dummy2', 'ItemCode', 'Item', 'ElementCode',
                   'Element', 'YearCode', 'Year', 'Unit', 'Value', 'Flag', 'Note']

    df_crop['Unit'] = df_crop['Unit'].astype(str).str.strip()
    df_crop = df_crop[df_crop['Unit'] == 'ha']
    df_crop['Value'] = pd.to_numeric(df_crop['Value'], errors='coerce')

    # Agréger la superficie par pays et année
    df_area = df_crop.groupby(['Country', 'Year'])['Value'].sum().reset_index()
    df_area = df_area.rename(columns={'Value': 'TotalArea_ha'})

    # Fusionner
    df_merged = pd.merge(df_nutrient, df_area, left_on=['Area', 'Year'], right_on=['Country', 'Year'], how='left')

    # Calcul kg/ha
    df_merged['kg_per_ha'] = (df_merged['Value'] * 1000) / df_merged['TotalArea_ha']

    # Sauvegarde
    df_merged.to_csv(output_path, index=False)
    print(f"✅ Conversion engrais en kg/ha terminée. Fichier : {output_path}")

    return df_merged

# 🔧 Exemple d’usage :
convert_npk_to_kgha(
    r"C:\plateforme-agricole-complete-v2\Boua\FAOSTAT_data_en_7-12-2025_engrais_nutriment.csv",
    r"C:\plateforme-agricole-complete-v2\Boua\Production_Crops_Livestock_Afrique.csv"
)
