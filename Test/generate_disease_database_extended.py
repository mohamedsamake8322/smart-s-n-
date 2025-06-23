import json
from utils.disease_database_extended import disease_manager

# ✅ Récupère les maladies déjà enregistrées via add_disease(...)
diseases = disease_manager.diseases

print(f"✅ {len(diseases)} maladies récupérées depuis disease_manager")

# ✅ Sauvegarde dans un fichier standard
with open("data/extended_disease_database.json", "w", encoding="utf-8") as f:
    json.dump(diseases, f, ensure_ascii=False, indent=2)

print("📁 Export terminé dans data/extended_disease_database.json")
