import os
import rasterio
import pandas as pd
from rasterio.sample import sample_gen
from glob import glob

# 📍 Dossier contenant les résolutions
base_folder = r"C:\Users\moham\Music\3"

# 🧪 Fichier sol
soil_path = r"C:\plateforme-agricole-complete-v2\soilgrids_africa\soil_profile_africa.csv"
soil_df = pd.read_csv(soil_path)
coords = list(zip(soil_df["x"], soil_df["y"]))  # supposé être en WGS84 (degrés décimaux)

# 🎯 Résolution à utiliser
res_folder = os.path.join(base_folder, "2.5 min")  # ou "5 min", "10 min"

# 📂 Variables et sous-dossiers
variables = {
    "pr": "Précipitation",
    "tx": "Température max",
    "tn": "Températurevmin"
}

# 📦 Extraction
results = []

for var_key, subdir in variables.items():
    var_path = os.path.join(res_folder, subdir)
    tif_files = sorted(glob(os.path.join(var_path, "*.tif")))  # chaque fichier = 1 mois

    for tif in tif_files:
        try:
            with rasterio.open(tif) as src:
                sampled_values = list(src.sample(coords))
                basename = os.path.basename(tif)
                month = basename.split("_")[-1].replace(".tif", "")  # ex: wc2.1_2.5m_pr_01.tif → 01
                results.append({
                    "Variable": var_key.upper(),
                    "Month": month,
                    "Values": [v[0] if v else None for v in sampled_values]
                })
                print(f"✅ {var_key.upper()} / Mois {month} → {len(sampled_values)} points")
        except Exception as e:
            print(f"⛔ Erreur {var_key} {tif} : {e}")

# 📊 Fusion en DataFrame final
extracted_df = pd.DataFrame({
    "Latitude": soil_df["y"],
    "Longitude": soil_df["x"]
})

for row in results:
    col_name = f"{row['Variable']}_{row['Month']}"
    extracted_df[col_name] = row["Values"]

print(f"📈 Extraction terminée : {extracted_df.shape[0]} points, {extracted_df.shape[1]} colonnes")

# 💾 Sauvegarde
output = r"C:\plateforme-agricole-complete-v2\wordclim_historique_extrait.csv"
extracted_df.to_csv(output, index=False)
print(f"📁 Données sauvegardées ici : {output}")
