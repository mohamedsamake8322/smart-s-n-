# pages/7_Smart_Fertilizer.py
import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime
import qrcode
from io import BytesIO
import xgboost as xgb
import json

# -----------------------------
# Paths (relative)
# -----------------------------
BASE = os.path.dirname(__file__)
MODEL_BIN = os.path.join(BASE, "../models/xgb_mali_model.bin")
COLUMNS_JSON = os.path.join(BASE, "../models/model_columns.json")
FONTS_DIR = os.path.join(BASE, "../fonts/dejavu-fonts-ttf-2.37/ttf/")
DEJAVU_REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
DEJAVU_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

# -----------------------------
# Sanity checks
# -----------------------------
if not os.path.exists(MODEL_BIN) or not os.path.exists(COLUMNS_JSON):
    st.error("Le modèle ou model_columns.json est introuvable dans le dossier 'models/'. "
             "Assure-toi d'avoir poussé 'models/xgb_mali_model.bin' et 'models/model_columns.json' dans le repo.")
    st.stop()

if not os.path.exists(DEJAVU_REGULAR) or not os.path.exists(DEJAVU_BOLD):
    st.warning("Les polices DejaVu n'ont pas été trouvées dans ../fonts. Les PDFs utiliseront une police par défaut.")

# -----------------------------
# Charger colonnes attendues
# -----------------------------
with open(COLUMNS_JSON, "r", encoding="utf-8") as f:
    model_cols = json.load(f)

# -----------------------------
# Charger booster natif XGBoost
# -----------------------------
booster = xgb.Booster()
booster.load_model(MODEL_BIN)

# -----------------------------
# Config engrais / fractionnements (hardcodés)
# -----------------------------
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

# -----------------------------
# Utilitaires
# -----------------------------
def predict_yield_from_user_inputs(user_inputs: dict) -> float:
    """Construit X_input complet selon model_cols, convertit en DMatrix et prédit."""
    X_input_dict = {c: 0 for c in model_cols}
    for k, v in user_inputs.items():
        if k in X_input_dict:
            X_input_dict[k] = v
    X_input = pd.DataFrame([X_input_dict], columns=model_cols)
    # for safety convert numeric columns
    for col in X_input.columns:
        X_input[col] = pd.to_numeric(X_input[col], errors="coerce").fillna(0)
    dmat = xgb.DMatrix(X_input.values, feature_names=model_cols)
    preds = booster.predict(dmat)
    if len(preds) == 0:
        raise RuntimeError("Aucune prédiction retournée par le booster.")
    return float(preds[0])

def build_pdf_and_bytes(culture: str, surface: float, pred_rendement: float, df_plan: pd.DataFrame) -> BytesIO:
    """Génère le PDF en mémoire et renvoie un BytesIO."""
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
            self.cell(0,10,"Généré par SmartFactLaser | " + datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0, "C")

    pdf = StyledPDF()
    if os.path.exists(DEJAVU_REGULAR):
        pdf.add_font("DejaVu","",DEJAVU_REGULAR, uni=True)
        pdf.add_font("DejaVu","B",DEJAVU_BOLD, uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial", "", 12)
    pdf.cell(0,10,f"🌿 Culture : {culture}", ln=True)
    pdf.cell(0,10,f"📐 Surface : {surface} ha    🎯 Rendement prédit : {round(pred_rendement,2)} t/ha", ln=True)
    pdf.ln(5)
    for phase in df_plan["Phase"].unique():
        pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial", "B", 12)
        pdf.set_text_color(0,51,102)
        pdf.cell(0,9,f"• Phase : {phase}", ln=True)
        for _, row in df_plan[df_plan["Phase"]==phase].iterrows():
            ligne = f"{row['Élément']} : {row['Dose kg']} kg → {row['Engrais']} ({row['Dose engrais (kg)']} kg)"
            pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial", "", 11)
            pdf.set_text_color(0,0,0)
            pdf.multi_cell(0,8, ligne)
        pdf.ln(2)

    # QR code
    url = f"https://sama-agrolink.com/fertiplan/{culture}"
    qr_img = qrcode.make(url)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format='PNG')
    qr_buffer.seek(0)
    pdf.ln(5)
    if os.path.exists(DEJAVU_REGULAR):
        pdf.set_font("DejaVu","B",12)
    else:
        pdf.set_font("Arial","B",12)
    pdf.cell(0,10,"🔗 Accès en ligne :", ln=True)
    # insert image from bytes
    pdf.image(qr_buffer, w=30)
    pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial","",9)
    pdf.cell(0,10,url, ln=True)

    # write to BytesIO
    out = BytesIO()
    out_bytes = pdf.output(dest='S').encode('latin-1')  # fpdf returns latin-1 bytes
    out.write(out_bytes)
    out.seek(0)
    return out

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌾 SmartFactLaser – Prédiction de Rendement & Plan de Fertilisation")

cols = st.columns(2)
with cols[0]:
    culture = st.selectbox("🌿 Type de culture", list(FRACTIONNEMENTS.keys()))
    surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)
with cols[1]:
    year = st.number_input("Année", min_value=2021, max_value=2025, value=2023)
    month = st.selectbox("Mois", list(range(1,13)), index=5)

st.markdown("### 🌤 Paramètres environnementaux (si inconnus laisser par défaut)")
ndvi = st.number_input("NDVI moyen", min_value=0.0, max_value=1.0, value=0.5)
ndmi = st.number_input("NDMI moyen", min_value=-1.0, max_value=1.0, value=0.1)
sm = st.number_input("Humidité du sol (SMAP)", min_value=0.0, value=0.2)
prec = st.number_input("Précipitations (mm)", min_value=0.0, value=50.0)
tavg = st.number_input("Température moyenne (°C)", min_value=-10.0, max_value=50.0, value=28.0)

if st.button("🔍 Prédire rendement & Générer plan"):
    user_inputs = {
        "Year": int(year),
        "Month": int(month),
        "NDVI_mean": float(ndvi),
        "NDMI_mean": float(ndmi),
        "SMAP_SoilMoisture": float(sm),
        "prec": float(prec),
        "tavg": float(tavg)
    }

    try:
        pred_rendement = predict_yield_from_user_inputs(user_inputs)
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        st.stop()

    st.success(f"🎯 Rendement prédit : {round(pred_rendement, 2)} t/ha")

    # build fertilization plan
    fractionnement = FRACTIONNEMENTS[culture]
    phase_list = []
    for phase, nutriments in fractionnement.items():
        for elmt, ratio in nutriments.items():
            dose = pred_rendement * surface * ratio / EFFICIENCES.get(elmt, 1)
            engrais = next((n for n, comp in ENGRAIS_DB.items() if elmt in comp), None)
            dose_engrais = round(dose / ENGRAIS_DB[engrais][elmt], 2) if engrais else None
            phase_list.append({
                "Phase": phase,
                "Élément": elmt,
                "Dose kg": round(dose, 2),
                "Engrais": engrais,
                "Dose engrais (kg)": dose_engrais
            })
    df_plan = pd.DataFrame(phase_list)

    st.markdown("### 📋 Plan de fertilisation par phase")
    st.dataframe(df_plan)

    # generate PDF bytes and provide download
    pdf_bytes = build_pdf_and_bytes(culture, surface, pred_rendement, df_plan)
    st.download_button("📄 Télécharger le plan PDF", pdf_bytes, file_name=f"{culture}_fertilisation_plan.pdf", mime="application/pdf")

    # also provide excel download
    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
        df_plan.to_excel(writer, index=False, sheet_name="Fertilisation")
    excel_bytes.seek(0)
    st.download_button("📥 Télécharger Excel", excel_bytes, file_name=f"{culture}_fertilisation_plan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # show short explanation
    st.markdown("### ℹ️ Explication rapide")
    st.write(f"- Le rendement estimé ({round(pred_rendement,2)} t/ha) a été obtenu par un modèle XGBoost entraîné sur des données historiques.")
    st.write("- Le plan de fertilisation répartit les besoins en N, P2O5 et K2O selon les phases définies pour la culture.")
    st.write("- Les doses d'engrais sont calculées en tenant compte des efficacités (pertes estimées).")
    st.write("")

    st.success("Plan généré — téléchargez le PDF ou Excel ci-dessous.")

# fin du script
