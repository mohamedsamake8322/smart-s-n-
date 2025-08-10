import requests
import rasterio
import pandas as pd
import gzip
from io import BytesIO

# Liste des liens Dropbox modifiés pour téléchargement direct
dropbox_links = {
    "WCsat_0-5cm": "https://www.dropbox.com/scl/fi/eyzc1kqt3y03j69ghksve/WCsat_0-5cm_M_250m.tif?rlkey=7zdirml78gcl5n5ethhoihbsn&st=3pk4mnqt&dl=1",
    "WCsat_5-15cm": "https://www.dropbox.com/scl/fi/jzcbzkxjmsy75jsgnajjh/WCsat_5-15cm_M_250m.tif?rlkey=mqobr6dn9ipaacxav812hw9ht&st=c3zx2ivs&dl=1",
    "WCsat_15-30cm": "https://www.dropbox.com/scl/fi/joww3ldmubv9thcz6m8xw/WCsat_15-30cm_M_250m.tif?rlkey=5tec18gkbuad2hku89em6ib6a&st=lrtjpirq&dl=1",
    "WCsat_30-60cm": "https://www.dropbox.com/scl/fi/quvcu4j472n7s6phevq9a/WCsat_30-60cm_M_250m.tif?rlkey=syjiaz055bhq9wdixmjlvmkxz&st=zjpxuh80&dl=1",
    "WCsat_60-100cm": "https://www.dropbox.com/scl/fi/qjlir9oab3h0fyle2hd62/WCsat_60-100cm_M_250m.tif?rlkey=orcw3sva8pm220id4he3d82b2&st=uiwa9bf4&dl=1",
    "WCsat_100-200cm": "https://www.dropbox.com/scl/fi/soqqi1saw8h0smlqoik2z/WCsat_100-200cm_M_250m.tif?rlkey=mwxf786f93nb9yc1p56357np7&st=e44aq6q8&dl=1"
}

def download_and_convert(url, output_name):
    print(f"📥 Downloading: {output_name}")
    response = requests.get(url)
    response.raise_for_status()
    tif_data = BytesIO(response.content)

    with rasterio.open(tif_data) as src:
        band = src.read(1)
        transform = src.transform
        nodata = src.nodata

        rows, cols = band.shape
        data = []

        for row in range(rows):
            for col in range(cols):
                value = band[row, col]
                if nodata is not None and value == nodata:
                    continue
                lon, lat = transform * (col, row)
                data.append((lon, lat, value))

    df = pd.DataFrame(data, columns=["longitude", "latitude", "value"])

    output_file = f"{output_name}.csv.gz"
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        df.to_csv(f, index=False)

    print(f"✅ Saved: {output_file}")

# Traitement en série
for name, link in dropbox_links.items():
    download_and_convert(link, name)
