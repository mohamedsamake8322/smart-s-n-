import os
import pandas as pd
import shutil
from sklearn.model_selection import train_test_split

# 🔧 Paramètres
csv_path = "dataset_combiné.csv"  # le CSV généré précédemment
output_dir = "plantdataset"
split_ratio = 0.8  # 80% train, 20% val

# 📂 Préparation des dossiers
for subset in ["train", "val"]:
    os.makedirs(os.path.join(output_dir, subset), exist_ok=True)

# 📑 Chargement du CSV
df = pd.read_csv(csv_path)
labels = df["label"].unique()

# 🔁 Traitement par classe
for label in labels:
    df_label = df[df["label"] == label]
    train_df, val_df = train_test_split(df_label, train_size=split_ratio, shuffle=True, random_state=42)

    for subset_name, subset_df in [("train", train_df), ("val", val_df)]:
        dest_class_dir = os.path.join(output_dir, subset_name, label)
        os.makedirs(dest_class_dir, exist_ok=True)

        for _, row in subset_df.iterrows():
            src_path = row["image_path"]
            filename = os.path.basename(src_path)
            dest_path = os.path.join(dest_class_dir, filename)

            try:
                shutil.copy(src_path, dest_path)
            except Exception as e:
                print(f"Erreur pour {src_path} → {e}")

print("✅ Répartition terminée dans 'plantdataset/train' et 'plantdataset/val'")
