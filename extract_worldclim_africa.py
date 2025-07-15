import ee

# Initialiser Earth Engine
ee.Initialize()

# 📍 Définir la zone Afrique
africa = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0") \
           .filter(ee.Filter.inList('ADM0_NAME', [
               'Algeria', 'Angola', 'Benin', 'Botswana', 'Burkina Faso', 'Burundi',
               'Cameroon', 'Cape Verde', 'Central African Republic', 'Chad', 'Comoros',
               'Congo', 'Côte d\'Ivoire', 'Djibouti', 'DR Congo', 'Egypt', 'Equatorial Guinea',
               'Eritrea', 'Eswatini', 'Ethiopia', 'Gabon', 'Gambia', 'Ghana', 'Guinea',
               'Guinea-Bissau', 'Kenya', 'Lesotho', 'Liberia', 'Libya', 'Madagascar', 'Malawi',
               'Mali', 'Mauritania', 'Mauritius', 'Morocco', 'Mozambique', 'Namibia', 'Niger',
               'Nigeria', 'Rwanda', 'Sao Tome and Principe', 'Senegal', 'Seychelles', 'Sierra Leone',
               'Somalia', 'South Africa', 'South Sudan', 'Sudan', 'Togo', 'Tunisia', 'Uganda',
               'Tanzania', 'Zambia', 'Zimbabwe'
           ]))

# 🔧 Paramètres
gcms = ['UKESM1-0-LL', 'EC-Earth3-Veg']
ssps = ['ssp245', 'ssp585']
periods = ['2021_2040', '2041_2060']
variables = ['pr', 'tmax', 'tmin']  # PR, TX, TN

def export_worldclim_image(gcm, ssp, period, variable):
    path = f"WORLDCLIM/V2/FUTURE/{gcm}_{ssp}_{period}_{variable}"
    try:
        image = ee.Image(path).clip(africa)
        task = ee.batch.Export.image.toDrive(
            image=image.toFloat(),
            description=f"{gcm}_{ssp}_{period}_{variable}_Africa",
            folder="worldclim_africa",
            fileNamePrefix=f"{gcm}_{ssp}_{period}_{variable}_Africa",
            region=africa.geometry(),
            scale=10000,
            maxPixels=1e13
        )
        task.start()
        print(f"✅ Export démarré pour : {gcm} | {ssp} | {period} | {variable}")
    except Exception as e:
        print(f"❌ Erreur pour {gcm}_{ssp}_{period}_{variable}:", e)

# 🚀 Boucle sur toutes les combinaisons
for gcm in gcms:
    for ssp in ssps:
        for period in periods:
            for var in variables:
                export_worldclim_image(gcm, ssp, period, var)
