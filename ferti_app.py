import streamlit as st  # type: ignore
import json
import os
import pandas as pd  # type: ignore
from fpdf import FPDF  # type: ignore
from datetime import datetime
import qrcode  # type: ignore
from io import BytesIO

# ----- CHEMIN DES POLICES -----
base_path = "C:/plateforme-agricole-complete-v2/fonts/dejavu-fonts-ttf-2.37/ttf/"
dejavu_regular = os.path.join(base_path, "DejaVuSans.ttf")
dejavu_bold = os.path.join(base_path, "DejaVuSans-Bold.ttf")

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
EFFICIENCES = {"N": 0.7, "P2O5": 0.5, "K2O": 0.6, "MgO": 0.5, "S": 0.6, "Zn": 0.3, "B": 0.3}
FERTI_PATH = "C:/plateforme-agricole-complete-v2/fertilization_phased_db.json"
BESOINS_PATH = "C:/plateforme-agricole-complete-v2/besoins des plantes en nutriments.json"

# ----- CHARGEMENT DONNÉES -----
with open(FERTI_PATH, encoding='utf-8') as f:
    fertibase = json.load(f)
with open(BESOINS_PATH, encoding='utf-8') as f:
    raw_data = json.load(f)

besoins_db = {}
for bloc in raw_data:
    besoins_db.update(bloc.get("cultures", bloc))

# ----- UI STREAMLIT -----
st.title("🌾 Plan de Fertilisation par Phase avec Export PDF")
culture_code = st.selectbox("🌿 Culture", list(besoins_db.keys()))
surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)
rendement = st.number_input("Rendement visé (t/ha)", min_value=0.1, value=5.0)

if st.button("🔍 Générer plan + Export PDF", key="generate_plan"):
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
    st.markdown("### 📋 Plan de fertilisation par phase")
    st.dataframe(df)

    # ----- CLASSE PDF -----
    class StyledPDF(FPDF):
        def header(self):
            self.set_fill_color(0, 102, 204)
            self.rect(0, 0, self.w, 20, 'F')
            self.set_font("DejaVu", "B", 14)
            self.set_text_color(255, 255, 255)
            self.set_y(6)
            self.cell(0, 8, "🧪 Plan de fertilisation – Smart Sènè Yield Predictor", align="C")
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("DejaVu", "", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Généré par Smart Sènè Yield Predictor | " + datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0, "C")

    # ----- CONSTRUCTION PDF -----
    pdf = StyledPDF()
    pdf.add_font("DejaVu", "", dejavu_regular)
    pdf.add_font("DejaVu", "B", dejavu_bold)
    pdf.add_page()
    pdf.set_font("DejaVu", "", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    pdf.cell(0, 10, f"🌿 Culture : {culture['nom_commun']}", ln=True)
    pdf.cell(0, 10, f"📐 Surface : {surface} ha    🎯 Rendement cible : {rendement} t/ha", ln=True)
    pdf.ln(5)

    for phase in df["Phase"].unique():
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 9, f"• Phase : {phase}", ln=True)
        for _, row in df[df["Phase"] == phase].iterrows():
            ligne = f"{row['Élément']} : {row['Dose kg']} kg → {row['Engrais']} ({row['Dose engrais (kg)']} kg)"
            pdf.set_font("DejaVu", "", 11)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 8, ligne, ln=True)

    pdf.ln(5)
    pdf.set_font("DejaVu", "B", 12)
    pdf.set_text_color(0, 51, 102)
    pdf.cell(0, 10, "📘 Légende des engrais utilisés :", ln=True)
    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(0, 0, 0)

    engrais_utilises = {row["Engrais"] for row in phase_data if row["Engrais"]}
    for engrais in sorted(engrais_utilises):
        nutriments = ENGRAIS_DB.get(engrais, {})
        contenu = ", ".join([f"{k} – {int(v * 100)} %" for k, v in nutriments.items()])
        pdf.cell(0, 8, f"- {engrais} : {contenu}", ln=True)

    # ----- QR CODE -----
    url = f"https://sama-agrolink.com/fertiplan/{culture_code}"
    qr_img = qrcode.make(url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)

    pdf.ln(10)
    pdf.set_font("DejaVu", "B", 12)
    pdf.cell(0, 10, "🔗 Accès en ligne :", ln=True)
    pdf.image(qr_buffer, w=30)
    pdf.set_font("DejaVu", "", 9)
    pdf.cell(0, 10, url, ln=True)

    # ----- EXPORT PDF -----
    file_path = f"{culture_code}_fertilisation_plan.pdf"
    pdf.output(file_path)
    with open(file_path, "rb") as f:
        st.download_button("📄 Télécharger le plan PDF", f, file_name=file_path, mime="application/pdf")

    # ----- EXPORT EXCEL -----
    excel_file = f"{culture_code}_fertilisation_plan.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f_excel:
        st.download_button("📥 Télécharger les données Excel", f_excel, file_name=excel_file, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
