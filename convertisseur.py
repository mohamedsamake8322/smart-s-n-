import os
import re

# 📁 Répertoire racine à parcourir
REPERTOIRE = "C:/plateforme-agricole-complete-v2"
SELECTED_LANG_VAR = "selected_lang"

def remplacer_t_crochets(path):
    with open(path, encoding="utf-8") as f:
        contenu = f.read()

    # ✅ Corrige l'expression pour détecter t["..."] avec éventuels espaces
    nouveau_contenu = re.sub(
        r't\s*\[\s*"([^"]+)"\s*\]',
        lambda m: f'translate_text("{m.group(1)}", {SELECTED_LANG_VAR})',
        contenu
    )

    # ✅ Corrige t.get("clé", "valeur par défaut")
    nouveau_contenu = re.sub(
        r't\.get\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\)',
        lambda m: f'translate_text("{m.group(2)}", {SELECTED_LANG_VAR})',
        nouveau_contenu
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(nouveau_contenu)

# 🚶‍♂️ Parcours récursif du répertoire
for dossier, _, fichiers in os.walk(REPERTOIRE):
    for fichier in fichiers:
        if fichier.endswith(".py"):
            remplacer_t_crochets(os.path.join(dossier, fichier))

print("✅ Conversion terminée.")
