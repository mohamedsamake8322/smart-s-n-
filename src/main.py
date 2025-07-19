import argparse
import pandas as pd
from extract_ndvi_pipeline import extract_ndvi_batch
from agro_fusion import fuse_with_agronomic_data
from yield_predictor import train_model, predict_yield
from optimizer import optimize_inputs

def main(year, culture, export_format):
    print("🚀 Initialisation du moteur SènèSmart Africa...")

    # Étape 1 : Charger les coordonnées filtrées
    coords_df = pd.read_csv("african_coordinates.csv")
    coords_df = coords_df[(coords_df["year"] == year) & (coords_df["culture"] == culture)]

    # Étape 2 : Extraire les NDVI pour ces zones
    ndvi_df = extract_ndvi_batch(coords_df)
    ndvi_df.to_csv("outputs/ndvi_africa.csv", index=False)

    # Étape 3 : Fusionner avec les données agronomiques
    df_fusion = fuse_with_agronomic_data(ndvi_df)
    df_fusion.to_csv("outputs/data_for_model.csv", index=False)

    # Étape 4 : Entraîner le modèle et faire des prédictions
    model = train_model(df_fusion)
    predictions = predict_yield(model, df_fusion)

    # Étape 5 : Optimiser les intrants pour chaque point
    intrants = []
    for _, row in df_fusion.iterrows():
        opt = optimize_inputs(row["culture"], row["country"], row["yield_target"])
        intrants.append(opt)

    df_intrants = pd.DataFrame(intrants)

    # Étape 6 : Export des résultats
    if export_format == "excel":
        df_intrants.to_excel("outputs/rapport_intrants_producteurs.xlsx", index=False)
    else:
        df_intrants.to_csv("outputs/rapport_intrants_producteurs.csv", index=False)

    print("✅ Rapport généré avec optimisation par culture et pays")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SènèSmart Engine Africa 🚀")
    parser.add_argument("--year", type=int, required=True, help="Année ciblée")
    parser.add_argument("--culture", type=str, required=True, help="Culture ciblée (maize, millet, etc.)")
    parser.add_argument("--export", type=str, choices=["excel", "csv"], default="csv", help="Format d’export")

    args = parser.parse_args()
    main(args.year, args.culture, args.export)
