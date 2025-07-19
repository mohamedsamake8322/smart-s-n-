from datacube.index import Index
from datacube.model import DatasetType
import yaml

# Charger le fichier YAML
with open("s2_l2a_definition.yaml", "r", encoding="utf-8") as f:
    definition = yaml.safe_load(f)

# Créer un index
index = Index()

# Injecter via l'API
index.products.add_document(definition)
print("✅ Produit ajouté via API Python")
