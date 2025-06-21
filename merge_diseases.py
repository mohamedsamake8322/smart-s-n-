from utils.disease_database import DiseaseDatabase
from utils.disease_database_extended import DISEASE_DATABASE
import json

# ⚙️ Charger les deux bases
db1 = DiseaseDatabase().diseases_data
db2 = DISEASE_DATABASE

# 🧬 Fusion avec priorité à db1
combined = {**db2, **db1}

# 🧼 Normalisation : s'assurer que chaque entrée a un champ "name"
for key, entry in combined.items():
    entry.setdefault("name", key)

# 💾 Sauvegarde dans un fichier JSON exploitable
with open("data/all_diseases.json", "w", encoding="utf-8") as f:
    json.dump(list(combined.values()), f, ensure_ascii=False, indent=2)

print(f"✅ Fusion réussie avec {len(combined)} maladies enregistrées.")
