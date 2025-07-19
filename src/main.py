import sys
import os
import argparse
import pandas as pd
from datetime import datetime

# 🔧 Ajout du chemin vers deafrica_tools
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

    # 📥 Étape 1 : Chargement des coordonnées filtrées
    csv_path = "african_coordinates.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Fichier d’entrée manquant : {csv_path}")
        sys.exit(1)

    coords_df = pd.read_csv(csv_path)
    coords_df = coords_df[(coords_df["year"] == year) & (coords_df["culture"] == culture)]

    if coords_df.empty:
        print(f"⚠️ Aucun point trouvé pour l’année {year} et la culture '{culture}'")
        sys.exit(1)
    print(f"✅ Points géographiques filtrés : {len(coords_df)}")

    # 🛰️ Étape 2 : Extraction NDVI
    ndvi_df = extract_ndvi_batch(coords_df)
    ndvi_path = "outputs/ndvi_africa.csv"
    ndvi_df.to_csv(ndvi_path, index=False)
    print("📁 NDVI exporté :", ndvi_path)
    ndvi_df = ndvi_df.dropna(subset=["latitude", "longitude", "ndvi_mean"])
    if ndvi_df.empty:
            print("❌ Aucun point NDVI valide après extraction. Arrêt du pipeline.")
    sys.exit(1)
    # 🌾 Étape 3 : Fusion agronomique
    fusion_df = fuse_with_agronomic_data(ndvi_df)
    fusion_path = "outputs/data_for_model.csv"
    fusion_df.to_csv(fusion_path, index=False)
    print("📁 Fusion exportée :", fusion_path)

    # 📈 Étape 4 : Prédiction du rendement
    model = train_model(fusion_df)
    predictions = predict_yield(model, fusion_df)
    print("📊 Prédictions effectuées")

    # ⚗️ Étape 5 : Optimisation des intrants
    intrants = []
    for _, row in fusion_df.iterrows():
        opt = optimize_inputs(row["culture"], row["country"], row["yield_target"])
        intrants.append(opt)
    intrants_df = pd.DataFrame(intrants)

    # 📤 Étape 6 : Export final
    if export_format == "excel":
        output_path = "outputs/rapport_intrants_producteurs.xlsx"
        intrants_df.to_excel(output_path, index=False)
    else:
        output_path = "outputs/rapport_intrants_producteurs.csv"
        intrants_df.to_csv(output_path, index=False)
    print(f"✅ Rapport généré : {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SènèSmart Engine Africa 🚀")
    parser.add_argument("--year", type=int, required=True, help="Année ciblée")
    parser.add_argument("--culture", type=str, required=True, help="Culture ciblée (maize, millet, etc.)")
    parser.add_argument("--export", type=str, choices=["excel", "csv"], default="csv", help="Format d’export")

    args = parser.parse_args()
    main(args.year, args.culture, args.export)
