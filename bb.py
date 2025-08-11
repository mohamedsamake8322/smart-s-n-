import pyarrow.dataset as ds

# Chemin vers ton fichier Parquet
file_path = r"C:\plateforme-agricole-complete-v2\WCsat\wcsat_0-5com_data.parquet"

# Ouvre le dataset Parquet
dataset = ds.dataset(file_path, format="parquet")

# Récupère seulement les 10 premières lignes
table = dataset.head(10)

# Conversion en DataFrame Pandas
df = table.to_pandas()

# Affiche le résultat
print(df)
