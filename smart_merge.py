import pandas as pd
import os
import json

BASE_PATH = r"C:\plateforme-agricole-complete-v2\merged_outputs"
MERGE_SCHEMA_PATH = os.path.join(BASE_PATH, "merge_schema.json")
OUTPUT_PATH = os.path.join(BASE_PATH, "final_dataset.csv.gz")

def load_file(filename, chunksize=None):
    path = os.path.join(BASE_PATH, filename)
    try:
        print(f"📥 Lecture : {filename}")
        reader = pd.read_csv(path, dtype=str, chunksize=chunksize, low_memory=False)
        df = pd.concat([chunk for chunk in reader], ignore_index=True) if chunksize else reader
        df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
        return df
    except Exception as e:
        print(f"⛔ Erreur avec {filename} : {e}")
        return None

def smart_merge(base, df, keys):
    # 🧠 Fusion légère avec 'left' pour préserver la structure du bloc de base
    return pd.merge(base, df, how="left", on=keys)

with open(MERGE_SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema = json.load(f)

groups = schema.get("groups", [])
fallbacks = schema.get("fallbacks", {})
chunk_sensitive = ["vegetation.csv.gz", "monthly_climate.csv.gz"]

final_blocks = []

for group in groups:
    print(f"\n🔗 Fusion du groupe : {group['name']}")
    dfs = []
    base_file = group["files"][0]
    chunksize = 50000 if base_file in chunk_sensitive else None
    base = load_file(base_file, chunksize)
    if base is None:
        print(f"⚠️ Base invalide pour {group['name']}, fusion ignorée")
        continue
    dfs.append(base)

    for file in group["files"][1:]:
        chunksize = 50000 if file in chunk_sensitive else None
        df = load_file(file, chunksize)
        if df is not None:
            dfs.append(df)

    # 🔍 Détermination des clés valides
    keys = [k for k in group["keys"] if all(k in df.columns for df in dfs)]
    if not keys:
        for k in group["keys"]:
            for fb in fallbacks.get(k, []):
                if all(fb in df.columns for df in dfs):
                    keys.append(fb)
        if not keys:
            print(f"⚠️ Clés introuvables pour {group['name']}, fusion ignorée")
            continue

    # ✂️ Réduction des colonnes inutiles
    dfs = [df[keys + [col for col in df.columns if col not in keys][:5]] for df in dfs]

    merged = dfs[0]
    for df in dfs[1:]:
        merged = smart_merge(merged, df, keys)

    # 💾 Sauvegarde partielle
    part_path = os.path.join(BASE_PATH, f"{group['name']}_merged.csv.gz")
    merged.to_csv(part_path, index=False, compression="gzip")
    print(f"✅ Bloc '{group['name']}' sauvegardé → {part_path}")
    final_blocks.append(part_path)

# 🧷 Assemblage final par concaténation ligne à ligne
print("\n📦 Fusion finale en cours...")
frames = [pd.read_csv(p, dtype=str, low_memory=False) for p in final_blocks]
final = pd.concat(frames, ignore_index=True)
final.to_csv(OUTPUT_PATH, index=False, compression="gzip")
print(f"\n✅ Fichier global final créé : {OUTPUT_PATH}")
