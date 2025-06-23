import os
from difflib import get_close_matches

def collect_labels(base_dir):
    labels = set()
    for split in ["train", "val"]:
        split_dir = os.path.join(base_dir, split)
        if not os.path.exists(split_dir):
            continue
        for d in os.listdir(split_dir):
            full_path = os.path.join(split_dir, d)
            if os.path.isdir(full_path):
                labels.add(d)
    return sorted(labels)

def détecter_doublons(labels, seuil_similarité=0.85):
    doublons = []
    for i, label in enumerate(labels):
        proches = get_close_matches(label, labels[i+1:], n=3, cutoff=seuil_similarité)
        for match in proches:
            doublons.append((label, match))
    return doublons

# 📁 Chemin vers ton dossier unifié
base_path = r"C:\chemin\vers\v"  # à adapter !

# 📋 Récupération des classes
labels = collect_labels(base_path)
print(f"\n🎯 {len(labels)} classes détectées dans {base_path} :\n")
for label in labels:
    print("-", label)

# 🔍 Détection des doublons proches
suspects = détecter_doublons(labels)
if suspects:
    print("\n⚠️ Doublons ou noms très proches détectés :\n")
    for a, b in suspects:
        print(f"🔁 {a}  ≈  {b}")
else:
    print("\n✅ Aucun doublon apparent trouvé (au seuil donné).")
