import os

dossier_principal = r"C:\plateforme-agricole-complete-v2\illustrations"

for nom in os.listdir(dossier_principal):
    ancien_chemin = os.path.join(dossier_principal, nom)
    if os.path.isdir(ancien_chemin):
        nouveau_nom = nom.lower().title()
        nouveau_chemin = os.path.join(dossier_principal, nouveau_nom)
        if ancien_chemin != nouveau_chemin:
            print(f"Renommage: '{nom}' → '{nouveau_nom}'")
            os.rename(ancien_chemin, nouveau_chemin)
        else:
            print(f"Aucun changement pour: '{nom}'")
