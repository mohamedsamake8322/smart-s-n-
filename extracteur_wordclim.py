import os
import requests
from zipfile import ZipFile
from io import BytesIO
import rasterio
from rasterio.mask import mask
import json

# 📁 Dossier de travail
root_folder = r"C:\worldclim_futur_afrique"
os.makedirs(root_folder, exist_ok=True)

# 🌍 Bounding box Afrique (WGS84)
afrique_bbox = {
    "type": "Polygon",
    "coordinates": [[
        [-25.0, -35.0],
        [-25.0, 38.0],
        [55.0, 38.0],
        [55.0, -35.0],
        [-25.0, -35.0]
    ]]
}

# 📦 Paramètres
variables = ["pr", "tx", "tn", "bioc"]
period = "2021-2040"
ssp = "585"
resolution = "2.5m"
gcms = ["MPI-ESM1-2-HR", "UKESM1-0-LL"]

# 🔗 URL modèle
base_url = "https://geodata.ucdavis.edu/cmip6/{var}/{res}/ssp{ssp}/{gcm}_{period}_{var}.zip"

for gcm in gcms:
    for var in variables:
        url = base_url.format(var=var, res=resolution, ssp=ssp, gcm=gcm, period=period)
        print(f"⬇️ Téléchargement : {url}")
        try:
            r = requests.get(url)
            if r.status_code != 200:
                print(f"⛔ Erreur de téléchargement pour {gcm} {var}")
                continue

            with ZipFile(BytesIO(r.content)) as zip_ref:
                zip_ref.extractall(os.path.join(root_folder, f"{gcm}_{var}"))

            # 📂 Liste des fichiers .tif extraits
            tif_files = [f for f in os.listdir(os.path.join(root_folder, f"{gcm}_{var}")) if f.endswith(".tif")]

            for tif in tif_files:
                tif_path = os.path.join(root_folder, f"{gcm}_{var}", tif)
                with rasterio.open(tif_path) as src:
                    out_image, out_transform = mask(src, [afrique_bbox], crop=True)
                    out_meta = src.meta.copy()
                    out_meta.update({
                        "height": out_image.shape[1],
                        "width": out_image.shape[2],
                        "transform": out_transform
                    })

                    # 📤 Export du raster découpé
                    out_file = os.path.join(root_folder, f"{gcm}_{var}_afrique", tif)
                    os.makedirs(os.path.dirname(out_file), exist_ok=True)
                    with rasterio.open(out_file, "w", **out_meta) as dest:
                        dest.write(out_image)
                    print(f"✅ Découpe {tif} → Afrique : {out_file}")

        except Exception as e:
            print(f"⛔ Erreur traitement {gcm} {var} : {e}")
