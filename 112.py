from pathlib import Path

# Base où sont rangés les fichiers
base_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries")

# Parcourir chaque niveau ADM
for adm_dir in sorted(base_dir.glob("ADM*")):
    if not adm_dir.is_dir():
        continue
    print(f"\n📂 Niveau {adm_dir.name}")
    print("=" * (8 + len(adm_dir.name)))

    # Parcourir chaque pays dans ce niveau
    for country_dir in sorted(adm_dir.iterdir()):
        if not country_dir.is_dir():
            continue
        print(f"  🌍 {country_dir.name} :")

        files = list(country_dir.glob("*"))
        if not files:
            print("    ⚠ Aucun fichier trouvé.")
        else:
            for f in files:
                print(f"    - {f.name}")
