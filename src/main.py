import sys
import os
import argparse
import pandas as pd
from datetime import datetime

# 🔧 Ajout dynamique du chemin vers deafrica_tools
deafrica_module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'deafrica-tools', 'deafrica_tools'))
if os.path.exists(deafrica_module_path):
    sys.path.append(deafrica_module_path)
else:
    print(f"❌ Module deafrica_tools introuvable à : {deafrica_module_path}")
    sys.exit(1)

# 📂 Crée le dossier "outputs" si nécessaire
os.makedirs("outputs", exist_ok=True)

# 🧠 Imports internes
from extract_ndvi_pipeline import extract_ndvi_batch
from agro_fusion import fuse_with_agronomic_data
from yield_predictor import train_model, predict_yield
from optimizer import optimize_inputs

def main(year, culture, export_format):
    print("🚀 Initialisation du moteur SènèSmart Africa...")
    print("🕒 Exécution le", datetime.now().strftime("%Y-%m-%d %H:%M"))

    # 📥 Étape 1 : Chargement des coordonnées
    if not os.path.exists("african_coordinates.csv"):
        print("❌ Fichier 'african_coordinates.csv' introuvable.")
        sys.exit(1)

    coords_df = pd.read_csv("african_coordinates.csv")
    coords_df = coords_df[(coords_df["year"] == year) & (coords_df["culture"] == culture)]

    if coords_df.empty:
        print(f"⚠️ Aucun point trouvé pour l’année {year} et la culture {culture}")
        sys.exit(1)

    # 🛰️ Étape 2 : Extraction NDVI
    ndvi_df = extract_ndvi_batch(coords_df)
    ndvi_df.to_csv("outputs/ndvi_africa.csv", index=False)
    print("📁 NDVI exporté : outputs/ndvi_africa.csv")

    # 🌱 Étape 3 : Fusion avec données agronomiques
    df_fusion = fuse_with_agronomic_data(ndvi_df)
    df_fusion.to_csv("outputs/data_for_model.csv", index=False)
    print("📁 Données fusionnées : outputs/data_for_model.csv")

    # 📈 Étape 4 : Prédiction de rendement
    model = train_model(df_fusion)
    predictions = predict_yield(model, df_fusion)

    # 🧪 Étape 5 : Optimisation des intrants
    intrants = []
    for _, row in df_fusion.iterrows():
        opt = optimize_inputs(row["culture"], row["country"], row["yield_target"])
        intrants.append(opt)

    df_intrants = pd.DataFrame(intrants)

    # 📤 Étape 6 : Export du rapport
    if export_format == "excel":
        output_path = "outputs/rapport_intrants_producteurs.xlsx"
        df_intrants.to_excel(output_path, index=False)
    else:
        output_path = "outputs/rapport_intrants_producteurs.csv"
        df_intrants.to_csv(output_path, index=False)

    print(f"✅ Rapport généré : {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SènèSmart Engine Africa 🚀")
    parser.add_argument("--year", type=int, required=True, help="Année ciblée")
    parser.add_argument("--culture", type=str, required=True, help="Culture ciblée (maize, millet, etc.)")
    parser.add_argument("--export", type=str, choices=["excel", "csv"], default="csv", help="Format d’export")

    args = parser.parse_args()
    main(args.year, args.culture, args.export)
