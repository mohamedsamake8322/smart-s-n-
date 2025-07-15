import pandas as pd
import os

# 📁 Dossiers d'origine
base_path = r"C:\Users\moham\Music\3"
files = {
    "2.5min": os.path.join(base_path, "2.5 min", "worldclim_2.5min_afrique_par_pays.csv"),
    "5min": os.path.join(base_path, "5 min", "worldclim_5min_afrique_par_pays.csv"),
    "10min": os.path.join(base_path, "10 min", "worldclim_10min_afrique_par_pays.csv"),
}

# 🔁 Lecture et renommage des colonnes
clim_dataframes = []
for res, path in files.items():
    df = pd.read_csv(path)
    df = df.rename(columns={
        "precip_moy": f"precip_{res}",
        "tmax_moy": f"tmax_{res}",
        "tmin_moy": f"tmin_{res}"
    })
    df["mois"] = df["mois"].astype(int)
    clim_dataframes.append(df)

# 🔗 Fusion progressive sur ['pays', 'mois']
merged = clim_dataframes[0]
for df in clim_dataframes[1:]:
    merged = pd.merge(merged, df, on=["pays", "mois"], how="outer")

# 🧽 Nettoyage final
merged = merged.drop_duplicates(subset=["pays", "mois"])
merged = merged.sort_values(by=["pays", "mois"])

# 💾 Sauvegarde
output_path = os.path.join(base_path, "worldclim_resolution_comparative.csv")
merged.to_csv(output_path, index=False)

print(f"✅ Fichier fusionné sauvegardé : {output_path}")
