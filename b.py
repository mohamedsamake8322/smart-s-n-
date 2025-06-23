# ✅ Script fusionné avec support récursif
import os
import pandas as pd

def explorer_dataset(root_dir, source_name, recursive=False):
    """
    Parcourt un dossier de dataset et retourne un DataFrame avec image_path, label et source.
    Si recursive=True, parcourt aussi les sous-dossiers imbriqués.
    """
    data = []

    if recursive:
        for root, dirs, files in os.walk(root_dir):
            images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                parts = os.path.normpath(root).split(os.sep)
                label = parts[-2] + "___" + parts[-1] if len(parts) >= 2 else parts[-1]
                for img in images:
                    data.append({
                        "image_path": os.path.join(root, img),
                        "label": label,
                        "source": source_name
                    })
    else:
        classes = sorted([d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d))])
        print(f"\n📂 Dataset: {source_name}")
        print(f"  - Nombre de classes trouvées : {len(classes)}\n")
        for classe in classes:
            class_path = os.path.join(root_dir, classe)
            images = [f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            print(f"    ↪ {classe} : {len(images)} images")
            for img in images:
                data.append({
                    "image_path": os.path.join(class_path, img),
                    "label": classe,
                    "source": source_name
                })

    return pd.DataFrame(data)

def afficher_statistiques(df, source_name):
    if df.empty:
        print(f"\n⚠️ Aucun fichier détecté dans {source_name}")
        return
    print(f"\n📊 Statistiques — {source_name}")
    print(f"Nombre total d’images : {len(df)}")
    print(f"Nombre de classes uniques : {df['label'].nunique()}")
    print(f"Exemples de classes : {df['label'].unique()[:5]}")


# 🔧 Chemins à ajuster selon ton système
plantvillage_path = r"C:\Downloads\archive\plantvillage dataset\color"
crop_disease_path = r"C:\Downloads\Dataset for Crop Pest and Disease Detection\Dataset for Crop Pest and Disease Detection\Raw Data"

# 🔍 Exploration des datasets
df_plant = explorer_dataset(plantvillage_path, "PlantVillage", recursive=False)
df_crop = explorer_dataset(crop_disease_path, "CropDisease", recursive=True)

# 📊 Statistiques
afficher_statistiques(df_plant, "PlantVillage")
afficher_statistiques(df_crop, "CropDisease")

# 🔗 Fusion des deux
df_combined = pd.concat([df_plant, df_crop], ignore_index=True)
df_combined.to_csv("dataset_combiné.csv", index=False)

print(f"\n✅ Fusion réussie : {len(df_combined)} images totales dans 'dataset_combiné.csv'")
print("📝 Colonnes disponibles : image_path, label, source")
