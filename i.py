#📁 Étape 2 – Répartition des images en train/ et val/ (par défaut : 80/20)
import os
import shutil
import pandas as pd
from sklearn.model_selection import train_test_split

# 🔧 Paramètres
csv_path = "dataset_combiné.csv"
output_dir = "plantdataset"
split_ratio = 0.8

# 📑 Charger le CSV
df = pd.read_csv(csv_path)

# 💡 Répartition par classe
for label in df["label"].unique():
    subset = df[df["label"] == label]
    train_df, val_df = train_test_split(subset, train_size=split_ratio, shuffle=True, random_state=42)

    for split_name, split_df in [("train", train_df), ("val", val_df)]:
        target_dir = os.path.join(output_dir, split_name, label)
        os.makedirs(target_dir, exist_ok=True)
        for _, row in split_df.iterrows():
            src = row["image_path"]
            fname = os.path.basename(src)
            dst = os.path.join(target_dir, fname)
            if not os.path.exists(dst):
                try:
                    shutil.copy2(src, dst)
                except Exception as e:
                    print(f"⚠️ Erreur sur {src} → {e}")

print("✅ Images copiées dans plantdataset/train/ et plantdataset/val/")
