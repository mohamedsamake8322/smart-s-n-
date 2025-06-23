import os

chemin = r"C:\plateforme-agricole-complete-v2\plantdataset\train"

# Lister uniquement les dossiers
dossiers = [nom for nom in os.listdir(chemin) if os.path.isdir(os.path.join(chemin, nom))]

print("📁 Dossiers trouvés :")
for dossier in dossiers:
    print("-", dossier)
