import json
import os
import pandas as pd

# 📁 Dossiers d'entrée
FRG_JSON = "fertilization_outputs/fertilization_data.json"
MN_JSON = "minnesota_outputs/minnesota_data.json"
OUTPUT_DIR = "unified_fertilization"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 📌 Mapping noms de cultures (manuel, extensible)
culture_aliases = {
    "corn": "maize", "maize": "maize",
    "tomato": "tomato", "tomate": "tomato",
    "rice": "rice",
    "potato": "potato", "pomme de terre": "potato",
    "bean": "bean", "haricot": "bean",
    "cabbage": "cabbage", "chou": "cabbage",
    "onion": "onion", "oignon": "onion",
    "wheat": "wheat", "blé": "wheat",
    "soybean": "soybean", "soja": "soybean"
}

def normalize_culture(name):
    return culture_aliases.get(name.lower().strip(), name.lower().strip())

# 📥 Chargement
with open(FRG_JSON, "r", encoding="utf-8") as f1, open(MN_JSON, "r", encoding="utf-8") as f2:
    frg = json.load(f1)
    mn = json.load(f2)

# 🧠 Fusion
merged_data = {}
for src_data in [frg, mn]:
    for raw_name, entries in src_data.items():
        clean_name = normalize_culture(raw_name)
        merged_data.setdefault(clean_name, []).extend(entries)

# 📄 Export JSON
with open(os.path.join(OUTPUT_DIR, "fertilization_master.json"), "w", encoding="utf-8") as f:
    json.dump(merged_data, f, indent=2, ensure_ascii=False)

# 📊 Export CSV
flat_rows = []
for crop, rows in merged_data.items():
    for row in rows:
        flat_rows.append([crop] + row)

df = pd.DataFrame(flat_rows)
df.to_excel(os.path.join(OUTPUT_DIR, "unified_fertilization_table.xlsx"), index=False)

print(f"✅ Fusion terminée avec {len(merged_data)} cultures")
print("📁 Données disponibles dans :", os.path.abspath(OUTPUT_DIR))
