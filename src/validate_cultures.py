import pandas as pd
from collections import Counter

# Charger le fichier CSV
csv_path = "african_coordinates.csv"
df = pd.read_csv(csv_path)

# Nettoyage et normalisation des cultures
raw_cultures = df["culture"].astype(str).str.strip().str.lower()
culture_counts = Counter(raw_cultures)

# Dictionnaire d’alias pour suggestions
CULTURE_ALIASES = {
    "maize": ["maize", "maïs", "mais", "milho"],
    "millet": ["millet", "millets", "millett"],
    "rice": ["rice", "riz", "ríz", "ryce"]
}

def suggest_alias(value):
    for canon, aliases in CULTURE_ALIASES.items():
        if value in [a.lower().strip() for a in aliases]:
            return canon
    return "❓ inconnu"

# Résumé des cultures détectées
print("🌾 Cultures détectées dans le fichier :")
for culture, count in culture_counts.items():
    suggestion = suggest_alias(culture)
    print(f" - {culture:<12} ➤ {count} point(s) ➤ standardisé : {suggestion}")

# Résumé des années
print("\n📆 Années disponibles :")
print(sorted(df["year"].unique()))
