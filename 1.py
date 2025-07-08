import os
from PIL import Image
import io

def compress_jpeg_if_beneficial(img, original_path, output_path, target_reduction=0.8):
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    new_size = buffer.tell()
    old_size = os.path.getsize(original_path)

    if new_size < old_size * target_reduction:
        with open(output_path, 'wb') as f:
            f.write(buffer.getvalue())
        return new_size
    else:
        shutil.copy2(original_path, output_path)
        return old_size

def compress_preserving_visual_quality(input_path, output_path):
    img = Image.open(input_path)
    ext = os.path.splitext(input_path)[1].lower()
    stat_info = os.stat(input_path)

    # Force RGB (sans transparence) pour JPEG
    if img.mode in ("RGBA", "LA"):
        img = img.convert("RGB")

    if ext in ['.jpg', '.jpeg']:
        final_size = compress_jpeg_if_beneficial(img, input_path, output_path)

    elif ext == '.png':
        if "transparency" not in img.info and img.mode != "RGBA":
            output_path = output_path.rsplit('.', 1)[0] + ".jpg"
            final_size = compress_jpeg_if_beneficial(img.convert("RGB"), input_path, output_path)
        else:
            # PNG avec transparence — pas de conversion
            img.save(output_path, format='PNG', optimize=True)
            final_size = os.path.getsize(output_path)
    else:
        print(f"Format non pris en charge : {input_path}")
        return

    os.utime(output_path, (stat_info.st_atime, stat_info.st_mtime))
    return os.path.getsize(input_path), final_size

# === TRAITEMENT EN LOT AVEC COMPARAISON AVANT/APRÈS ===

source_dir = r"C:\Users\moham\Pictures\2"
target_dir = r"C:\Users\moham\Pictures\3"
import shutil

for filename in os.listdir(source_dir):
    if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        src = os.path.join(source_dir, filename)
        dest = os.path.join(target_dir, filename)

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        try:
            before, after = compress_preserving_visual_quality(src, dest)
            gain = (before - after) // 1024
            print(f"{filename}: {before//1024} KB → {after//1024} KB (Gain : {gain} KB)")
        except Exception as e:
            print(f"Erreur avec {filename} : {e}")
