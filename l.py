import json
from pathlib import Path

# Charger le fichier brut fusionné que tu m’as envoyé
path = Path("C:\\plateforme-agricole-complete-v2\\besoins_des_plantes_en_nutriments.json")

with open(path, "r", encoding="utf-8") as f:
    buffer = ""
    raw_blocks = []
    for line in f:
        line = line.strip()
        if not line:
            continue
        buffer += line
        try:
            parsed = json.loads(buffer)
            raw_blocks.append(parsed)
            buffer = ""
        except json.JSONDecodeError:
            buffer += " "

# Sortie : un fichier avec un bloc JSON par culture dans un seul fichier
with open("cultures_par_bloc.json", "w", encoding="utf-8") as out:
    for block in raw_blocks:
        json.dump(block, out, indent=2, ensure_ascii=False)
        out.write("\n\n")  # Séparation lisible entre les blocs

print("✅ Cultures exportées individuellement dans cultures_par_bloc.json (1 bloc par culture).")
