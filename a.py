import re
import json

# Charger le texte extrait du PDF
with open("contenu_pdf.txt", "r", encoding="utf-8") as f:
    texte = f.read()

# Liste des sections à extraire
sections = [
    "CAUSAL AGENT",
    "DISTRIBUTION",
    "SYMPTOMS",
    "CONDITIONS FOR DISEASE DEVELOPMENT",
    "CONTROL"
]

# Expression régulière pour détecter les titres de maladies (ex: BACTERIAL SPECK)
pattern_maladie = r"\n([A-Z\s]{5,})\n"

# Découper le texte par maladie
blocs = re.split(pattern_maladie, texte)
maladies = {}

# Parcourir les blocs deux par deux : [texte_avant, titre1, contenu1, titre2, contenu2, ...]
for i in range(1, len(blocs) - 1, 2):
    titre = blocs[i].strip()
    contenu = blocs[i + 1]

    maladie = {"nom": titre}
    for section in sections:
        # Extraire chaque section jusqu'à la suivante
        pattern_section = rf"{section}\n(.*?)(?=\n[A-Z\s]{3,}|$)"
        match = re.search(pattern_section, contenu, flags=re.DOTALL)
        if match:
            maladie[section.lower().replace(" ", "_")] = match.group(1).strip()

    maladies[titre] = maladie

# Sauvegarder le JSON
with open("maladies_structurées.json", "w", encoding="utf-8") as f:
    json.dump(maladies, f, ensure_ascii=False, indent=4)

print("✅ Fichier 'maladies_structurées.json' généré avec succès.")
