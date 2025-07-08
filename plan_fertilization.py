import json

# 📁 Charger les bases de données
with open("knowledge/pheno_phases.json", "r", encoding="utf-8") as f:
    phenology = json.load(f)

with open("knowledge/fertilization_phased_db.json", "r", encoding="utf-8") as f:
    fertibase = json.load(f)

# 📥 Inputs utilisateur
culture = input("🌱 Entrez la culture : ").strip().lower()
surface = float(input("📐 Entrez la superficie (en hectares) : "))
rendement = input("🎯 Rendement souhaité (ex: 20 t/ha) : ").strip().lower()
mode_app = input("🧴 Méthode d’application (volée / localisée / fertirrigation) : ").strip().lower()
zone = input("📍 Zone géographique (pays ou région) : ").strip().lower()

# 🔍 Vérifier si la culture est connue
if culture not in phenology:
    print(f"❌ Culture « {culture} » inconnue dans la base phénologique.")
    exit()

# 🧬 Obtenir les phases
phases = phenology[culture]

# 🧠 Chercher le plan de fertilisation associé
try:
    plan = fertibase[culture][rendement][mode_app][zone]
except KeyError:
    print("❌ Aucune donnée disponible pour cette combinaison (culture, rendement, mode, zone).")
    exit()

# 📊 Affichage du plan par phase
print(f"\n📋 Plan de fertilisation par phase — {culture.upper()}, {surface} ha, {rendement}, {zone.title()}")
print("-" * 80)
print(f"{'Phase':<25} | {'Engrais':<20} | {'Dose (kg/ha)':<15} | {'Total (kg)':<10}")
print("-" * 80)

for phase in phases:
    if phase in plan:
        for dose in plan[phase]:
            engrais = dose["fertilizer"]
            par_ha = dose["dose_kg_ha"]
            total = par_ha * surface
            print(f"{phase:<25} | {engrais:<20} | {par_ha:<15.2f} | {total:<10.2f}")
    else:
        print(f"{phase:<25} | {'-':<20} | {'-':<15} | {'-':<10}")
print("-" * 80)
print("\n✅ Plan terminé. Prêt pour export PDF ou adaptation selon variété/date semis.")
