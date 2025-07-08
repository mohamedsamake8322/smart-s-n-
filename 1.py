import os
from PIL import Image
import piexif
from io import BytesIO
import shutil

source_dir = r"C:\Users\moham\Pictures\2"
target_dir = r"C:\Users\moham\Pictures\3"
target_size_kb = 1000  # 1MB

def resize_to_target_size(input_path, output_path, target_kb):
    img = Image.open(input_path)

    # Conserver EXIF si présent
    exif_data = img.info.get('exif', b'')

    scale = 1.0
    while True:
        new_size = (int(img.width * scale), int(img.height * scale))
        resized_img = img.resize(new_size, Image.LANCZOS)

        buffer = BytesIO()
        resized_img.save(buffer, format='JPEG', quality=95, optimize=True, exif=exif_data)
        size_kb = buffer.tell() / 1024

        if size_kb <= target_kb or scale < 0.1:
            # Création du dossier cible si nécessaire
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Sauvegarde finale
            with open(output_path, 'wb') as f:
                f.write(buffer.getvalue())

            # Préserver les dates du fichier original
            stat_info = os.stat(input_path)
            os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))
            break

        scale -= 0.05  # Diminution progressive

# Traitement en lot
for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.jpg', '.jpeg')):
        src_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(target_dir, filename)
        resize_to_target_size(src_file, dest_file, target_size_kb)
