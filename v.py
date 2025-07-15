import pandas as pd
import os

# 📁 Dossier contenant les fichiers
weather_folder = r"C:\Users\moham\Music\3\worldclim"

# 🔍 Localiser les fichiers
files = {
    "2.5min": os.path.join(weather_folder, "worldclim_2.5min_afrique_par_pays.csv"),
    "5min": os.path.join(weather_folder, "worldclim_5min_afrique_par_pays.csv"),
    "10min": os.path.join(weather_folder, "worldclim_10min_afrique_par_pays.csv"),
}

# 🧰 Charger et renommer les colonnes
frames = []
for res, filepath in files.items():
    if not os.path.exists(filepath):
        print(f"⛔ Fichier absent : {filepath}")
        continue

    df = pd.read_csv(filepath)
    df = df.rename(columns={
        "precip_moy": f"precip_{res}",
        "tmax_moy": f"tmax_{res}",
        "tmin_moy": f"tmin_{res}"
    })
    df["mois"] = df["mois"].astype(int)
    frames.append(df)

# 🔗 Fusion des fichiers par 'pays' et 'mois'
if len(frames) == 3:
    merged = frames[0]
    for other_df in frames[1:]:
        merged = pd.merge(merged, other_df, on=["pays", "mois"], how="outer")

    # 📦 Nettoyage et tri
    merged = merged.drop_duplicates(subset=["pays", "mois"])
    merged = merged.sort_values(["pays", "mois"])

    # 💾 Sauvegarde
    output_file = os.path.join(weather_folder, "worldclim_comparatif_resolutions.csv")
    merged.to_csv(output_file, index=False)
    print(f"✅ Fichier fusionné créé : {output_file}")
else:
    print("⚠️ Fusion impossible : au moins un fichier météo est manquant.")
