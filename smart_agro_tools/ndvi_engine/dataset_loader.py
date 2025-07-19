import pandas as pd

def load_agricultural_data(path):
    """
    Charge et structure le dataset agricole.

    Args:
        path (str): chemin vers le fichier CSV.

    Returns:
        pd.DataFrame: table structurée avec cultures, NDVI potentiels, et yield target.
    """
    df = pd.read_csv(path)
    df['culture'] = df['culture'].str.strip()
    return df
