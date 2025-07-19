import datacube
import yaml

# Charger le fichier YAML
with open("s2_l2a_definition.yaml", "r", encoding="utf-8") as f:
    definition = yaml.safe_load(f)

# Créer un Datacube et récupérer l'index
dc = datacube.Datacube(app='force-add-product')
index = dc.index

# Injecter le produit
index.products.add_document(definition)
print("✅ Produit ajouté via API Python")
