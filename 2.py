import json

# Chemin vers le fichier JSON
json_path = "EN_mapping_fiches_maladies.json"

# Liste brute des classes à comparer (extraites par script ou manuellement)
train_classes = [
    "Alfalfa mosaic virus", "Anthracnose", "Aphids", "Apple  apple scab", "Apple  black rot",
    # ... ajoute les 99 noms ici ou charge-les via le script de listing
]

# Charger le JSON
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Supposons que le JSON est sous forme { "nom_maladie": {...}, ... }
json_keys = set(data.keys())
train_keys = set(train_classes)

# Analyse
matches = train_keys & json_keys
missing = train_keys - json_keys
extra = json_keys - train_keys

print(f"✅ Correspondances trouvées : {len(matches)}")
print(f"❌ Classes manquantes dans le JSON : {len(missing)}")
for item in sorted(missing):
    print(f"- {item}")

print(f"\n📦 Clés en trop dans le JSON (non présentes dans train/val) : {len(extra)}")
for item in sorted(extra):
    print(f"- {item}")
