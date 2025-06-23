# 🧠 Script : generer_mapping_label.py
import pandas as pd
import json

# Charger le CSV fusionné
df = pd.read_csv("dataset_combiné.csv")

# Extraire les labels uniques
labels = sorted(df["label"].dropna().unique())

# Construction du mapping brut
mapping = {}
for label in labels:
    if "___" in label:
        culture, maladie = label.split("___", 1)
    else:
        culture, maladie = "Inconnue", label

    # Nettoyage facultatif
    culture = culture.replace("_", " ").replace(",", "").strip()
    maladie = maladie.replace("_", " ").replace(",", "").strip()

    mapping[label] = {
        "culture": culture,
        "maladie": maladie,
        "agent_causal": "À renseigner"
    }

# Export en JSON lisible
with open("mapping_maladies.json", "w", encoding="utf-8") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"✅ Mapping généré pour {len(mapping)} labels dans mapping_maladies.json")
