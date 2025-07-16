import pandas as pd
import os

folder_meteo = r"C:\plateforme-agricole-complete-v2\weather_cleaned"

for file in os.listdir(folder_meteo):
    if not file.endswith(".csv"):
        continue

    df = pd.read_csv(os.path.join(folder_meteo, file))
    count = len(df)
    print(f"{file}: {count} points météo")
