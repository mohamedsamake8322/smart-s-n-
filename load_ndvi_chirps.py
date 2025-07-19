import datacube
import matplotlib.pyplot as plt
import numpy as np

dc = datacube.Datacube(app='ndvi-chirps')

# Charger données Sentinel-2
s2 = dc.load(product='s2_l2a', time=('2025-07-01', '2025-07-31'),
             latitude=(-1.05, -1.00), longitude=(34.50, 34.60))

# Calcul NDVI
ndvi = (s2.nir - s2.red) / (s2.nir + s2.red)
ndvi_mean = ndvi.mean(dim=['x', 'y'])

# Afficher la courbe NDVI
ndvi_mean.plot.line(marker='o')
plt.title("NDVI moyen - Juillet 2025")
plt.ylabel("NDVI")
plt.grid()
plt.show()
rain = dc.load(product='chirps', time=('2025-07-01', '2025-07-31'),
               latitude=(-1.05, -1.00), longitude=(34.50, 34.60))
rain_mean = rain.precip.mean(dim=['x', 'y'])
