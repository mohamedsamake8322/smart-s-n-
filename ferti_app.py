import streamlit as st # type: ignore
import json
import pandas as pd # type: ignore
from fpdf import FPDF # type: ignore

# ----- CONFIG -----
ENGRAIS_DB = {
    "Urée": {"N": 0.46},
    "MAP": {"P2O5": 0.52, "N": 0.11},
    "KCl": {"K2O": 0.60},
    "Sulfate de magnésium": {"MgO": 0.16},
    "Soufre (Sulfate)": {"S": 0.18},
    "Sulfate de zinc": {"Zn": 0.22},
    "Borax": {"B": 0.11}
}

EFFICIENCES = {
    "N": 0.7, "P2O5": 0.5, "K2O": 0.6,
    "MgO": 0.5, "S": 0.6, "Zn": 0.3, "B": 0.3
}

FERTI_PATH = "C:/plateforme-agricole-complete-v2/fertilization_phased_db.json"
BESOINS_PATH = "C:/plateforme-agricole-complete-v2/besoins des plantes en nutriments.json"

# ----- CHARGER DONNÉES -----
with open(FERTI_PATH, encoding='utf-8') as f:
    fertibase = json.load(f)
with open(BESOINS_PATH, encoding='utf-8') as f:
    raw_data = json.load(f)
besoins_db = {}

for bloc in raw_data:
    if "cultures" in bloc:
        besoins_db.update(bloc["cultures"])
    else:
        besoins_db.update(bloc)


# ----- UI -----
st.title("🌾 Plan de Fertilisation par Phase avec Export PDF")
culture_code = st.selectbox("🌿 Culture", list(besoins_db.keys()))
surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)
rendement = st.number_input("Rendement visé (t/ha)", min_value=0.1, value=5.0)

if st.button("🔍 Générer plan + Export PDF"):
    culture = besoins_db[culture_code]
    export = culture["export_par_tonne"]
    fractionnement = fertibase[culture_code]["fractionnement"]

    phase_data = []

    for phase, nutriments in fractionnement.items():
        for elmt, ratio in nutriments.items():
            if elmt in export:
                unit = export[elmt]["unite"]
                val = export[elmt]["valeur"]
                quant = (val / 1000 if unit.endswith("g/t") else val) * rendement * surface
                besoin = round(quant / EFFICIENCES.get(elmt, 1), 2)
                dose = round(besoin * ratio, 2)

                # Associer un engrais
                engrais = next((nom for nom, comp in ENGRAIS_DB.items() if elmt in comp), None)
                dose_engrais = round(dose / ENGRAIS_DB[engrais][elmt], 2) if engrais else None

                phase_data.append({
                    "Phase": phase,
                    "Élément": elmt,
                    "Dose kg": dose,
                    "Engrais": engrais,
                    "Dose engrais (kg)": dose_engrais
                })

    df = pd.DataFrame(phase_data)
    st.markdown("### 📋 Plan par phase")
    st.dataframe(df)

    # --- PDF EXPORT ---
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Plan de fertilisation – {culture['nom_commun']}", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Superficie: {surface} ha | Rendement cible: {rendement} t/ha", ln=True)
    pdf.ln(5)

    for phase in df["Phase"].unique():
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"• {phase}", ln=True)
        sous_df = df[df["Phase"] == phase]
        for _, row in sous_df.iterrows():
            el = row["Élément"]
            dose = row["Dose kg"]
            engrais = row["Engrais"]
            dose_e = row["Dose engrais (kg)"]
            pdf.set_font("Arial", "", 11)
            pdf.cell(0, 9, f"{el}: {dose} kg → {engrais} ({dose_e} kg)", ln=True)
        pdf.ln(2)

    file_path = f"{culture_code}_fertilisation_plan.pdf"
    pdf.output(file_path)
    with open(file_path, "rb") as f:
        st.download_button(label="📄 Télécharger le plan PDF", data=f, file_name=file_path, mime="application/pdf")
