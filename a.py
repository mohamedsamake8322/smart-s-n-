import re

# Charger le texte extrait depuis le PDF
with open("contenu_pdf.txt", "r", encoding="utf-8") as f:
    texte = f.read()

# Définir les sections à exclure (MAJUSCULES utilisées dans le PDF)
sections_a_supprimer = [
    "CAUSAL AGENT",
    "DISTRIBUTION",
    "SYMPTOMS",
    "CONDITIONS FOR DISEASE DEVELOPMENT",
    "CONTROL",
    "DISEASE CYCLE",
    "MANAGEMENT",
    "REFERENCES",
    "ECONOMIC IMPORTANCE"
    # ➕ ajoute d'autres si besoin
]

# Supprimer les sections et leur contenu jusqu'à la prochaine section ou saut de ligne double
pattern = r"(" + "|".join(re.escape(titre) for titre in sections_a_supprimer) + r")\n(.*?)(?=\n[A-Z\s]{3,}|$)"
texte_nettoye = re.sub(pattern, "", texte, flags=re.DOTALL)

# Supprimer les en-têtes de catégories générales (comme "BACTERIAL")
texte_nettoye = re.sub(r"^[A-Z\s]{3,}$", "", texte_nettoye, flags=re.MULTILINE)

# Sauvegarder le texte propre
with open("maladies_sans_sections.txt", "w", encoding="utf-8") as f:
    f.write(texte_nettoye.strip())

print("✅ Texte nettoyé enregistré dans 'maladies_sans_sections.txt'")
