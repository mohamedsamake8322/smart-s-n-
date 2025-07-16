#💻 Script : Encodage des engrais par type
import pandas as pd

def encode_engrais_types(product_csv, output_path="engrais_produit_encoded.csv"):
    # 📥 Charger le fichier produit
    df = pd.read_csv(product_csv)
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df['Area'] = df['Area'].str.strip()
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df['Item'] = df['Item'].str.strip()

    # 🧼 Garder uniquement les lignes utiles
    df = df[df['Unit'] == 't']
    df = df[df['Element'].isin(['Import quantity', 'Production'])]

    # 🧠 Pivot par pays, année et type d'engrais
    df_pivot = df.pivot_table(index=['Area', 'Year'], columns='Item', values='Value', aggfunc='sum')

    # 🧪 Remplacer les NaN par 0 (pas d'importation/production)
    df_encoded = df_pivot.fillna(0).reset_index()

    # 💾 Sauvegarde
    df_encoded.to_csv(output_path, index=False)
    print(f"✅ Encodage des types d'engrais terminé : {output_path}")

    return df_encoded

# 🔧 Exemple d’usage
encode_engrais_types(
    r"C:\plateforme-agricole-complete-v2\Boua\FAOSTAT_data_en_7-12-2025_engrais_par_produit.csv"
)
