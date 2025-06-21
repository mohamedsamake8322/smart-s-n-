from utils.disease_database import DiseaseDatabase
from utils.disease_database_extended import DISEASE_DATABASE  # dict[str, dict]

def get_merged_diseases():
    base_db = DiseaseDatabase()
    db1 = base_db.diseases_data   # Dict[str, Dict]
    db2 = DISEASE_DATABASE        # Dict[str, Dict]

    # Fusion des deux bases : priorité à db1 si conflits
    combined = {**db2, **db1}

    # Normalisation : on s'assure que chaque entrée a un champ "name"
    for key, entry in combined.items():
        entry.setdefault("name", key)

    return list(combined.values())
