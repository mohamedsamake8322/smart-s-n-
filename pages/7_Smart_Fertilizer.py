import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import qrcode
from io import BytesIO
import joblib
import numpy as np

# ----- CHEMIN DES POLICES -----
base_path = "C:/plateforme-agricole-complete-v2/fonts/dejavu-fonts-ttf-2.37/ttf/"
dejavu_regular = os.path.join(base_path, "DejaVuSans.ttf")
dejavu_bold = os.path.join(base_path, "DejaVuSans-Bold.ttf")

# ----- CONFIGURATION ENGRAIS -----
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

# ----- FRACTIONNEMENTS -----
FRACTIONNEMENTS = {
    "Maïs": {
        "Phase 1": {"N": 0.4, "P2O5": 0.3, "K2O": 0.3},
        "Phase 2": {"N": 0.3, "P2O5": 0.4, "K2O": 0.3},
        "Phase 3": {"N": 0.3, "P2O5": 0.3, "K2O": 0.4}
    },
    "Mil": {
        "Phase 1": {"N": 0.5, "P2O5": 0.3, "K2O": 0.2},
        "Phase 2": {"N": 0.3, "P2O5": 0.4, "K2O": 0.3},
        "Phase 3": {"N": 0.2, "P2O5": 0.3, "K2O": 0.5}
    }
}

# ----- CHARGEMENT DU MODELE XGBOOST -----
MODEL_PATH = "C:/plateforme-agricole-complete-v2/xgb_mali_model.pkl"
model = joblib.load(MODEL_PATH)

# ----- COLONNES ATTENDUES PAR LE MODELE -----
MODEL_COLUMNS = ['Year', 'Month', 'NDVI_mean', 'NDVI_min', 'NDVI_max', 'NDVI_stdDev',
                 'NDMI_mean', 'NDMI_min', 'NDMI_max', 'NDMI_stdDev',
                 'Area Code (M49)', 'Element Code', 'Item Code', 'Year Code', 'Source Code',
                 'Indicator Code', 'Months Code', 'mean',
                 'bio01','bio02','bio03','bio04','bio05','bio06','bio07','bio08','bio09',
                 'bio10','bio11','bio12','bio13','bio14','bio15','bio16','bio17','bio18','bio19',
                 'prec','tavg','tmax','tmin','CHIRPS_Daily','CHIRPS_Pentad','SMAP_SoilMoisture',
                 'GEDI_CanopyHeight','Mangrove2000','TidalWetlands2019']

# ----- UI STREAMLIT -----
st.title("🌾 SmartFactLaser – Prédiction de Rendement et Plan de Fertilisation")
culture = st.selectbox("🌿 Type de culture", list(FRACTIONNEMENTS.keys()))
surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)

# Entrées simplifiées pour prédiction
year = st.number_input("Année", min_value=2021, max_value=2025, value=2023)
month = st.selectbox("Mois", list(range(1, 13)))
ndvi = st.number_input("NDVI moyen", min_value=0.0, max_value=1.0, value=0.5)
ndmi = st.number_input("NDMI moyen", min_value=-1.0, max_value=1.0, value=0.1)
sm = st.number_input("Humidité du sol (SMAP)", min_value=0.0, value=0.2)
prec = st.number_input("Précipitations (mm)", min_value=0.0, value=50.0)
tavg = st.number_input("Température moyenne (°C)", min_value=-10.0, max_value=50.0, value=28.0)

if st.button("🔍 Prédire rendement + Générer plan PDF"):
    # ----- CONSTRUCTION DU DATAFRAME POUR XGBOOST -----
    X_input_dict = {col: 0 for col in MODEL_COLUMNS}  # Valeurs par défaut
    X_input_dict.update({
        'Year': year,
        'Month': month,
        'NDVI_mean': ndvi,
        'NDMI_mean': ndmi,
        'SMAP_SoilMoisture': sm,
        'prec': prec,
        'tavg': tavg
    })
    X_input = pd.DataFrame([X_input_dict])

    # ----- PRÉDICTION DU RENDEMENT -----
    pred_rendement = model.predict(X_input)[0]
    st.success(f"🎯 Rendement prédit : {round(pred_rendement,2)} t/ha")

    # ----- CALCUL PLAN DE FERTILISATION -----
    fractionnement = FRACTIONNEMENTS[culture]
    phase_data = []
    for phase, nutriments in fractionnement.items():
        for elmt, ratio in nutriments.items():
            dose = pred_rendement * surface * ratio / EFFICIENCES.get(elmt, 1)
            engrais = next((nom for nom, comp in ENGRAIS_DB.items() if elmt in comp), None)
            dose_engrais = round(dose / ENGRAIS_DB[engrais][elmt],2) if engrais else None
            phase_data.append({
                "Phase": phase,
                "Élément": elmt,
                "Dose kg": round(dose,2),
                "Engrais": engrais,
                "Dose engrais (kg)": dose_engrais
            })
    df = pd.DataFrame(phase_data)
    st.markdown("### 📋 Plan de fertilisation par phase")
    st.dataframe(df)

    # ----- EXPORT PDF -----
    class StyledPDF(FPDF):
        def header(self):
            self.set_fill_color(0,102,204)
            self.rect(0,0,self.w,20,'F')
            self.set_font("DejaVu","B",14)
            self.set_text_color(255,255,255)
            self.set_y(6)
            self.cell(0,8,"🧪 Plan de fertilisation – SmartFactLaser", align="C")
            self.ln(10)
        def footer(self):
            self.set_y(-15)
            self.set_font("DejaVu","",8)
            self.set_text_color(150,150,150)
            self.cell(0,10,"Généré par SmartFactLaser | "+datetime.now().strftime("%d/%m/%Y %H:%M"),0,0,"C")

    pdf = StyledPDF()
    pdf.add_font("DejaVu","",dejavu_regular)
    pdf.add_font("DejaVu","B",dejavu_bold)
    pdf.add_page()
    pdf.set_font("DejaVu","",12)
    pdf.cell(0,10,f"🌿 Culture : {culture}", ln=True)
    pdf.cell(0,10,f"📐 Surface : {surface} ha    🎯 Rendement prédit : {round(pred_rendement,2)} t/ha", ln=True)
    pdf.ln(5)
    for phase in df["Phase"].unique():
        pdf.set_font("DejaVu","B",12)
        pdf.set_text_color(0,51,102)
        pdf.cell(0,9,f"• Phase : {phase}", ln=True)
        for _, row in df[df["Phase"]==phase].iterrows():
            ligne = f"{row['Élément']} : {row['Dose kg']} kg → {row['Engrais']} ({row['Dose engrais (kg)']} kg)"
            pdf.set_font("DejaVu","",11)
            pdf.set_text_color(0,0,0)
            pdf.cell(0,8,ligne,ln=True)

    # ----- QR Code -----
    url = f"https://sama-agrolink.com/fertiplan/{culture}"
    qr_img = qrcode.make(url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    pdf.ln(10)
    pdf.set_font("DejaVu","B",12)
    pdf.cell(0,10,"🔗 Accès en ligne :", ln=True)
    pdf.image(qr_buffer, w=30)
    pdf.set_font("DejaVu","",9)
    pdf.cell(0,10,url,ln=True)

    # ----- EXPORT PDF -----
    pdf_file = f"{culture}_fertilisation_plan.pdf"
    pdf.output(pdf_file)
    with open(pdf_file,"rb") as f_pdf:
        st.download_button("📄 Télécharger PDF", f_pdf, file_name=pdf_file, mime="application/pdf")

    # ----- EXPORT EXCEL -----
    excel_file = f"{culture}_fertilisation_plan.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file,"rb") as f_excel:
        st.download_button(
            "📥 Télécharger Excel",
            f_excel,
            file_name=excel_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
