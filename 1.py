import os
from PIL import Image
import io

def compress_to_target_size(input_path, output_path, target_size_bytes=150_000):
    img = Image.open(input_path)
    stat_info = os.stat(input_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ext = os.path.splitext(input_path)[1].lower()

    success = False

    if ext in ['.jpg', '.jpeg']:
        for quality in range(90, 4, -5):  # Descendre jusqu’à qualité 5
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            if buffer.tell() <= target_size_bytes:
                with open(output_path, 'wb') as f_out:
                    f_out.write(buffer.getvalue())
                success = True
                break
        if not success:
            img.save(output_path, format='JPEG', quality=5, optimize=True)

    elif ext == '.png':
        if "A" not in img.getbands():  # Si pas de canal alpha
            # Convertir en JPEG pour meilleur gain
            img = img.convert("RGB")
            output_path = output_path.rsplit('.', 1)[0] + ".jpg"
            compress_to_target_size(input_path, output_path, target_size_bytes)
            return
        else:
            img = img.convert('P', palette=Image.ADAPTIVE)
            img.save(output_path, format='PNG', optimize=True)

            if os.path.getsize(output_path) > target_size_bytes:
                # Réessai en JPEG forcé si palette ne suffit pas
                img = img.convert("RGB")
                output_path = output_path.rsplit('.', 1)[0] + ".jpg"
                compress_to_target_size(input_path, output_path, target_size_bytes)
                return

    os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))


# === TRAITEMENT PAR LOT AVEC AFFICHAGE DES TAILLES ===
source_dir = r"C:\Users\moham\Pictures\2"
target_dir = r"C:\Users\moham\Pictures\3"

for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        src_file = os.path.join(source_dir, filename)
        dest_file = os.path.join(target_dir, filename)

        original_size = os.path.getsize(src_file)
        compress_to_target_size(src_file, dest_file)

        if os.path.exists(dest_file):
            new_size = os.path.getsize(dest_file)
            saved_kb = (original_size - new_size) // 1024
            print(f"{filename}: {original_size//1024} KB → {new_size//1024} KB  (Gain : {saved_kb} KB)")
