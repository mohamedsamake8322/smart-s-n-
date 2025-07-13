import streamlit as st
import ee
import geemap.foliumap as geemap

# 🔐 Authentification GEE
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# 🎯 Interface utilisateur Streamlit
st.title("🛰️ NDVI Viewer pour Sama AgroLink")
st.markdown("Entrez les coordonnées GPS de votre champ en Afrique :")

lat = st.number_input("Latitude", value=11.174)
lon = st.number_input("Longitude", value=-1.562)
buffer_m = st.slider("Rayon autour du champ (mètres)", 100, 2000, 1000)

if st.button("📡 Générer NDVI"):
    # 📍 Définition du point géographique
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(buffer_m).bounds()

    # 🛰️ Import collection Sentinel-2
    collection = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(point) \
        .filterDate('2023-06-01', '2023-07-01') \
        .sort('CLOUDY_PIXEL_PERCENTAGE')

    image = collection.first()

    # 🍃 Calcul NDVI
    ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

    # 🗺️ Affichage carte
    Map = geemap.Map(center=[lat, lon], zoom=12)
    ndvi_params = {'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']}
    Map.addLayer(ndvi, ndvi_params, 'NDVI')
    Map.addLayer(point, {}, 'Champ')
    Map.to_streamlit(height=600)

    # 🖼️ Lien image brute (bonus)
    url = ndvi.getThumbURL({
        'min': 0,
        'max': 1,
        'region': region,
        'dimensions': 512,
        'format': 'png'
    })
    st.markdown(f"📥 [Télécharger NDVI]({url})")

