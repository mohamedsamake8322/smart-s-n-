import json
import os
import re

# 📁 Charger la base fusionnée
with open("unified_fertilization/fertilization_master.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 📥 Inputs utilisateur
culture = input("🌱 Entrez la culture : ").strip().lower()
surface = float(input("📐 Entrez la superficie (en hectares) : "))

# 🔍 Rechercher les lignes disponibles
recs = data.get(culture)
if not recs:
    print(f"❌ Aucune donnée disponible pour « {culture} »")
    exit()

print(f"\n✅ {len(recs)} recommandations trouvées pour « {culture} »\n")

# 🔬 Détection automatique de nutriments
nutrients = ['N', 'P2O5', 'K2O']
dose_pattern = re.compile(r"(N|P2O5|K2O)[\s:=\-]*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)

plans = []

for i, row in enumerate(recs, 1):
    row_text = " | ".join(str(cell) for cell in row)
    extracted = {}

    for match in dose_pattern.finditer(row_text):
        nutri = match.group(1).upper()
        amount = float(match.group(2))
        extracted[nutri] = amount

    if extracted:
        plans.append((row_text, extracted))

# 📊 Affichage
if not plans:
    print("⚠️ Aucun dosage N/P/K explicite détecté.")
else:
    for i, (source_text, doses) in enumerate(plans, 1):
        print(f"\n📋 Recommandation #{i}")
        print("Source :", source_text)
        print("-" * 50)
        print(f"{'Nutriment':<10} | {'Dose (kg/ha)':<12} | {'Surface':<6} | {'Total (kg)':<10}")
        print("-" * 50)
        for nut, dose in doses.items():
            total = dose * surface
            print(f"{nut:<10} | {dose:<12.2f} | {surface:<6} | {total:<10.2f}")
        print("-" * 50)

print("\n🎯 Fin de génération du plan structuré. Prêt pour export PDF ou interface utilisateur.")
