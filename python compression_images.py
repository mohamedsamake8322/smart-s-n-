import os
from PIL import Image
import shutil

def compress_and_preserve_date(input_path, output_path, target_size_kb=2000, step=5, min_quality=10):
    img = Image.open(input_path).convert("RGB")
    temp_file = output_path + ".temp.jpg"
    original_stat = os.stat(input_path)
    quality = 95

    while quality >= min_quality:
        img.save(temp_file, format='JPEG', quality=quality, optimize=True)
        size_kb = os.path.getsize(temp_file) // 1024
        print(f"{os.path.basename(input_path)} - Qualité {quality}: {size_kb} KB")
        if size_kb <= target_size_kb:
            break
        quality -= step

    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    shutil.move(temp_file, output_path)
    os.utime(output_path, (original_stat.st_atime, original_stat.st_mtime))


# Répertoires source et destination
source_folder = r"C:\Users\moham\Pictures\2"
output_folder = r"C:\Users\moham\Pictures\3"

for filename in os.listdir(source_folder):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        input_file = os.path.join(source_folder, filename)
        output_file = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
        compress_and_preserve_date(input_file, output_file)
