# 📦 Chargement des packages
import datacube
from deafrica_tools.load_isda import load_isda

dc = datacube.Datacube(app='iSDAsoil_full_loader')

# 🧠 Liste des variables à charger
variables = [
    'profondeur_du_substrat_rocheux',
    'densité_volumique',
    'carbone_organique',
    'carbone_total',
    'ph',
    'azote_total',
    'phosphore_extractible',
    'extractible_au_potassium',
    'calcium_extractible',
    'magnésium_extractible',
    'extractible_au_soufre',
    'zinc_extractible',
    'extractible_de_fer',
    'aluminium_extractible',
    'argile_contenu',
    'contenu_sable',
    'teneur_en_limon',
    'contenu_en_pierre',
    'classe_de_texture',
    'capacité_d’échange_de_cations',
    'FCC'
]

# 🌍 Définir ta zone d’intérêt (ex. : Afrique de l’Ouest)
lat_range = (-5.0, 15.0)  # latitude min, max
lon_range = (-20.0, 10.0) # longitude min, max

# 📊 Charger chaque variable
loaded_data = {}
for var in variables:
    print(f"⏳ Chargement : {var}")
    try:
        data = load_isda(dc=dc,
                         variable=var,
                         lat=lat_range,
                         lon=lon_range)
        loaded_data[var] = data
        print(f"✅ Terminé : {var}")
    except Exception as e:
        print(f"⚠️ Échec pour {var} : {e}")
