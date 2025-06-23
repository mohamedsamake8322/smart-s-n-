# 🐍 Script : uniformiser_labels_capitalize.py
import os

# 📁 Ton dossier train
train_dir = r"C:\plateforme-agricole-complete-v2\plantdataset\train"

renommés = 0

for nom in os.listdir(train_dir):
    ancien_chemin = os.path.join(train_dir, nom)
    if os.path.isdir(ancien_chemin):
        nouveau_nom = nom.lower().capitalize()
        nouveau_chemin = os.path.join(train_dir, nouveau_nom)

        if ancien_chemin != nouveau_chemin:
            if not os.path.exists(nouveau_chemin):
                os.rename(ancien_chemin, nouveau_chemin)
                renommés += 1
                print(f"✅ {nom} → {nouveau_nom}")
            else:
                print(f"⚠️ Conflit : '{nouveau_nom}' existe déjà")

print(f"\n🎯 {renommés} dossiers renommés avec format : Majuscule + minuscules")
