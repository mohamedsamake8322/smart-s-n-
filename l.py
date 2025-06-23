import os

# 📁 Chemin à adapter si besoin
chemin_train = r"C:\plateforme-agricole-complete-v2\plantdataset\train"

# 📋 Lister les sous-dossiers (chaque dossier = un label)
classes = sorted([
    dossier for dossier in os.listdir(chemin_train)
    if os.path.isdir(os.path.join(chemin_train, dossier))
])

print(f"\n🎯 {len(classes)} classes trouvées dans : {chemin_train}\n")
for nom in classes:
    print("-", nom)

# 💾 Optionnel : sauvegarder la liste
with open("liste_des_classes.txt", "w", encoding="utf-8") as f:
    for nom in classes:
        f.write(nom + "\n")

print("\n✅ Liste enregistrée dans 'liste_des_classes.txt'")
