fichier = r"C:\plateforme-agricole-complete-v2\plantdataset\EN_mapping_fiches_maladies.json"

with open(fichier, "r", encoding="utf-8") as f:
    contenu = f.read()

print(f"Nombre total de caractères dans le fichier : {len(contenu)}")
