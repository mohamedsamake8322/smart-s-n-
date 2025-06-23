#🧠 Étape 1 – Recréer dataset_combiné.csv depuis ta base nettoyée
import os
import pandas as pd

def explorer_images(dataset_dir):
    """
    Explore récursivement le dossier et extrait image_path + label + source.
    """
    data = []
    for root, _, files in os.walk(dataset_dir):
        images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            label = os.path.basename(root)
            for img in images:
                data.append({
                    "image_path": os.path.join(root, img),
                    "label": label,
                    "source": "plantvillage"
                })
    return pd.DataFrame(data)

# 📍 Chemin vers le dossier nettoyé
dataset_path = r"C:\plateforme-agricole-complete-v2\plantdataset\train"
df = explorer_images(dataset_path)

# 💾 Sauvegarde
df.to_csv("dataset_combiné.csv", index=False)
print(f"✅ {len(df)} images listées dans 'dataset_combiné.csv'")

