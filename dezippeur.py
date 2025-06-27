import zipfile
import time
import os

start = time.time()
zip_path = r"C:\plateforme-agricole-complete-v2\Moh\plantdataset.zip"
extract_to = r"H:\My Drive\My drive"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    file_list = zip_ref.namelist()
    total = 0

    for file in file_list:
        if file.startswith("plantdataset/train/") or file.startswith("plantdataset/val/"):
            zip_ref.extract(file, extract_to)
            total += 1
            print(f"[{total}] {file} extrait")

end = time.time()
print(f"\n✅ Extraction sélective terminée en {end - start:.2f} secondes.")
