def optimize_inputs(culture, country, rendement_vise, df_reference=None):
    if df_reference is None:
        import pandas as pd
        df_reference = pd.read_csv("dataset_agricole_prepared.csv")

    stats = df_reference[(df_reference["culture"] == culture) & (df_reference["country"] == country)]
    if stats.empty:
        return {
            "culture": culture,
            "country": country,
            "rendement visé": rendement_vise,
            "engrais estimé (kg/ha)": None,
            "pesticides estimé (kg/ha)": None
        }

    ratio_fert = stats["production"].mean() / stats["yield_target"].mean()
    ratio_pest = stats["pesticides_use"].mean() / stats["yield_target"].mean()

    return {
        "culture": culture,
        "country": country,
        "rendement visé": rendement_vise,
        "engrais estimé (kg/ha)": round(rendement_vise * ratio_fert, 2),
        "pesticides estimé (kg/ha)": round(rendement_vise * ratio_pest, 2)
    }
