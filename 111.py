import zipfile
from pathlib import Path
import re
import shutil

# Dossier contenant les ZIP
zip_dir = Path(r"C:\Users\moham\Music\Zip")

# Dossier de sortie
output_base = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries")
output_base.mkdir(parents=True, exist_ok=True)

# Expression régulière pour extraire pays et ADM depuis le nom
pattern = re.compile(r"geoBoundaries-([A-Z]{3})-(ADM\d)-", re.IGNORECASE)

# Parcours des fichiers ZIP
for zip_path in zip_dir.glob("*.zip"):
    match = pattern.search(zip_path.name)
    if not match:
        print(f"❌ Nom de fichier non reconnu : {zip_path.name}")
        continue

    country_code = match.group(1).upper()
    adm_level = match.group(2).upper()

    # Chemin du dossier de destination
    dest_dir = output_base / adm_level / country_code
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"📦 Extraction : {zip_path.name} → {dest_dir}")

    # Décompresser dans un dossier temporaire
    temp_dir = output_base / "_temp"
    temp_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Déplacer les fichiers extraits vers le bon dossier
    for item in temp_dir.iterdir():
        shutil.move(str(item), dest_dir / item.name)

    # Nettoyer le dossier temporaire
    shutil.rmtree(temp_dir)

print("✅ Organisation terminée !")
