from pathlib import Path
import geopandas as gpd

# Base de tes fichiers déjà rangés
base_dir = Path(r"C:\plateforme-agricole-complete-v2\geoboundaries")

# Parcourir chaque niveau ADM
for adm_dir in sorted(base_dir.glob("ADM*")):
    if not adm_dir.is_dir():
        continue
    print(f"\n📂 {adm_dir.name}")
    print("=" * (4 + len(adm_dir.name)))

    for country_dir in sorted(adm_dir.iterdir()):
        if not country_dir.is_dir():
            continue

        # Chercher le .geojson principal (pas simplifié)
        geojson_files = [f for f in country_dir.glob("*.geojson") if "_simplified" not in f.name]

        if not geojson_files:
            print(f"  🌍 {country_dir.name}: ⚠ Aucun fichier principal trouvé")
            continue

        geojson_path = geojson_files[0]  # On prend le premier trouvé
        try:
            gdf = gpd.read_file(geojson_path)
            columns = list(gdf.columns)
            sample_names = gdf.iloc[:3].to_dict(orient="records")  # premiers enregistrements
            print(f"  🌍 {country_dir.name} : {len(gdf)} entités")
            print(f"     📄 Colonnes: {columns}")
            print(f"     📝 Exemples: {[rec for rec in sample_names]}")
        except Exception as e:
            print(f"  🌍 {country_dir.name}: Erreur de lecture ({e})")
