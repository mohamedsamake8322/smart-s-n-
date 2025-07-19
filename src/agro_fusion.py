import pandas as pd

def fuse_with_agronomic_data(ndvi_df, agro_path="dataset_agricole_prepared.csv"):
    df_agro = pd.read_csv(agro_path)
    df_agro["latitude"] = df_agro["latitude"].round(4)
    df_agro["longitude"] = df_agro["longitude"].round(4)

    ndvi_df["latitude"] = ndvi_df["latitude"].round(4)
    ndvi_df["longitude"] = ndvi_df["longitude"].round(4)

    df_fusion = pd.merge(df_agro, ndvi_df, on=["country", "year", "latitude", "longitude", "culture"], how="inner")
    print(f"✅ Fusion réussie : {len(df_fusion)} lignes")
    return df_fusion
