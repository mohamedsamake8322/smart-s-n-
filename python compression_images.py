import os
from PIL import Image
import shutil

def resize_and_preserve_dates(input_path, output_path, scale=0.5):
    # Ouvrir et redimensionner
    img = Image.open(input_path)
    width, height = img.size
    new_size = (int(width * scale), int(height * scale))
    resized_img = img.resize(new_size, Image.LANCZOS)

    # Préserver les dates
    stat_info = os.stat(input_path)

    # Création du dossier cible si besoin
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Sauvegarder (au format d’origine si possible)
    if input_path.lower().endswith('.png'):
        resized_img.save(output_path, format='PNG', optimize=True)
    else:
        resized_img.convert("RGB").save(output_path, format='JPEG', quality=90, optimize=True)

    os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))


# Dossiers
source_dir = r"C:\Users\moham\Pictures\2"
target_dir = r"C:\Users\moham\Pictures\3"

# Traitement en lot
for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        src_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(target_dir, filename)
        resize_and_preserve_dates(src_file, dest_file)
