import os
import shutil

# Chemins source et destination
src_folder = r"C:\plateforme-agricole-complete-v2\Personnel\New folder"
dst_folder = r"C:\plateforme-agricole-complete-v2\weather_data_africa"

# Crée le dossier de destination s'il n'existe pas
os.makedirs(dst_folder, exist_ok=True)

# Parcours de tous les fichiers dans le dossier source
for filename in os.listdir(src_folder):
    src_file = os.path.join(src_folder, filename)

    # Ignore si ce n'est pas un fichier
    if not os.path.isfile(src_file):
        continue

    # Chemin de destination initial
    base_name, ext = os.path.splitext(filename)
    dst_file = os.path.join(dst_folder, filename)

    # Si un fichier de même nom existe, on ajoute un suffixe
    counter = 1
    while os.path.exists(dst_file):
        new_name = f"{base_name}_copy{counter}{ext}"
        dst_file = os.path.join(dst_folder, new_name)
        counter += 1

    # Déplacement
    shutil.move(src_file, dst_file)
    print(f"Déplacé : {filename} → {os.path.basename(dst_file)}")

print("✅ Tous les fichiers ont été déplacés sans écrasement.")
