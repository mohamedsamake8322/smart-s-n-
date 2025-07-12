import pandas as pd

def download_fao_yield(culture="Maize", country="Mali"):
    url = "https://fenixservices.fao.org/faostat/static/bulkdownloads/Production_Crops_E_All_Data.zip"
    df = pd.read_csv(url, compression="zip", encoding="ISO-8859-1")
    df = df[(df["Item"] == culture) & (df["Area"] == country)]
    df = df[["Area", "Item", "Year", "Value"]].rename(columns={"Value": "Yield_kg_per_ha"})
    df.to_csv(f"{country}_{culture}_yield.csv", index=False)
    print("✅ Données FAO sauvegardées")

download_fao_yield("Maize", "Mali")
