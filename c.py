import os
from difflib import get_close_matches

def collect_labels_recursive(root_dir):
    """
    Explore tous les sous-dossiers contenant des images et extrait les chemins comme labels potentiels.
    """
    labels = set()
    for dirpath, _, files in os.walk(root_dir):
        images = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            label = os.path.basename(dirpath)
            labels.add(label)
    return sorted(labels)

def détecter_doublons(labels, seuil_similarité=0.85):
    doublons = []
    for i, label in enumerate(labels):
        proches = get_close_matches(label, labels[i+1:], n=3, cutoff=seuil_similarité)
        for match in proches:
            doublons.append((label, match))
    return doublons

# 📁 À adapter selon ta machine
base_dir = r"C:\Downloads\plantdataset\plantvillage dataset"

# 📋 Extraction des labels potentiels
labels = collect_labels_recursive(base_dir)
print(f"\n🎯 {len(labels)} labels détectés (profondément) dans :\n{base_dir}\n")
for l in labels:
    print("-", l)

# 🔍 Doublons suspects
suspects = détecter_doublons(labels)
if suspects:
    print("\n⚠️ Doublons ou noms très proches détectés :\n")
    for a, b in suspects:
        print(f"🔁 {a}  ≈  {b}")
else:
    print("\n✅ Aucun doublon apparent détecté (selon la similarité définie)")
