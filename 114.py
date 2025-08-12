import shutil
from pathlib import Path

# Chemin où se trouvent actuellement tes fichiers geoBoundaries
source_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries")

# Dossier où on va ranger par ADM
output_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries_sorted")
output_dir.mkdir(parents=True, exist_ok=True)

# Parcours de tous les fichiers .geojson
for file in source_dir.glob("**/*.geojson"):
    name_parts = file.stem.split("-")

    # Vérifie si le nom contient un niveau ADM
    adm_level = None
    for level in ["ADM0", "ADM1", "ADM2", "ADM3", "ADM4", "ADM5"]:
        if level in name_parts:
            adm_level = level
            break

    if adm_level:
        # Crée le dossier correspondant au niveau
        level_dir = output_dir / adm_level
        level_dir.mkdir(parents=True, exist_ok=True)

        # Copie le fichier
        shutil.copy(file, level_dir / file.name)
        print(f"📂 {file.name} → {adm_level}")

print("✅ Tri terminé !")
