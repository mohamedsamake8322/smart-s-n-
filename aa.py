#🧠 MODULE 1 — Préparation des données agronomiques (fusion météo + intrants + rendement)
# data_pipeline.py
import pandas as pd

def prepare_dataset():
    df_weather = pd.read_csv("merged_weather_africa.csv", parse_dates=["date"])
    df_weather["year"] = df_weather["date"].dt.year
    df_weather = df_weather.groupby(["country", "year", "latitude", "longitude", "variable"])["value"].mean().reset_index()
    df_weather = df_weather.pivot_table(index=["country", "year", "latitude", "longitude"], columns="variable", values="value").reset_index()

    df_engrais = pd.read_csv("Fertilizers by Nutrient FAOSTAT.csv")
    df_engrais = df_engrais[df_engrais["Element"].isin(["Import quantity", "Production"])]
    df_engrais = df_engrais.groupby(["Area", "Year", "Element"])["Value"].sum().unstack().reset_index()
    df_engrais.rename(columns={"Area": "country", "Year": "year"}, inplace=True)

    df_pest = pd.read_csv("Pesticides Use FAOSTAT.csv")
    df_pest = df_pest[df_pest["Element"] == "Agricultural Use"]
    df_pest = df_pest.groupby(["Area", "Year"])["Value"].sum().reset_index()
    df_pest.rename(columns={"Area": "country", "Year": "year", "Value": "pesticides_use"}, inplace=True)

    df_intrants = pd.merge(df_engrais, df_pest, on=["country", "year"], how="outer")

    df_yield = pd.read_csv("FAOSTAT Yield Data.csv")
    df_yield["Element"] = df_yield["Element"].str.lower().str.strip()
    df_yield = df_yield[df_yield["Element"] == "yield"]
    df_yield = df_yield.rename(columns={"Area": "country", "Year": "year", "Item": "culture", "Value": "yield_target"})
    df_yield = df_yield[["country", "year", "culture", "yield_target"]].dropna()

    df_base = pd.merge(df_weather, df_intrants, on=["country", "year"], how="left")
    df_final = pd.merge(df_base, df_yield, on=["country", "year"], how="left")
    df_final = df_final.dropna(subset=["yield_target"])

    df_final.to_csv("dataset_agricole_prepared.csv", index=False)
    print(f"✅ Dataset enregistré avec {len(df_final)} lignes")

if __name__ == "__main__":
    prepare_dataset()
