import streamlit as st
import pandas as pd
import os
from fpdf import FPDF # type: ignore
from datetime import datetime
import qrcode # type: ignore
from io import BytesIO
import xgboost as xgb # type: ignore
import json

# -----------------------------
# Paths
# -----------------------------
BASE = os.path.dirname(__file__)
DATA_FOLDER = r"C:\Downloads\Crop-Fertilizer-Analysis"
MODEL_BIN = os.path.join(BASE, "../models/xgb_mali_model.bin")
COLUMNS_JSON = os.path.join(BASE, "../models/model_columns.json")
FONTS_DIR = os.path.join(BASE, "../fonts/dejavu-fonts-ttf-2.37/ttf/")
DEJAVU_REGULAR = os.path.join(FONTS_DIR, "DejaVuSans.ttf")
DEJAVU_BOLD = os.path.join(FONTS_DIR, "DejaVuSans-Bold.ttf")

# -----------------------------
# Sanity checks
# -----------------------------
if not os.path.exists(MODEL_BIN) or not os.path.exists(COLUMNS_JSON):
    st.error("Modèle ou colonnes manquants dans 'models/'.")
    st.stop()

# -----------------------------
# Charger modèle et colonnes
# -----------------------------
with open(COLUMNS_JSON, "r", encoding="utf-8") as f:
    model_cols = json.load(f)

booster = xgb.Booster()
booster.load_model(MODEL_BIN)

# -----------------------------
# Extraire cultures depuis CSV
# -----------------------------
def get_available_cultures(folder_path: str) -> list:
    cultures = set()
    for file in os.listdir(folder_path):
        if file.endswith(".csv"):
            df = pd.read_csv(os.path.join(folder_path, file))
            for col in df.columns:
                if col.lower().strip() in ["label", "crop type", "culture"]:
                    cultures.update(df[col].dropna().unique())
    return sorted(list(cultures))

available_cultures = get_available_cultures(DATA_FOLDER)

# -----------------------------
# Fractionnements génériques
# -----------------------------
def generate_fractionnement(culture: str) -> dict:
    return {
        "Phase 1": {"N": 0.4, "P2O5": 0.3, "K2O": 0.3},
        "Phase 2": {"N": 0.3, "P2O5": 0.4, "K2O": 0.3},
        "Phase 3": {"N": 0.3, "P2O5": 0.3, "K2O": 0.4}
    }

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

# -----------------------------
# Prédiction
# -----------------------------
def predict_yield(user_inputs: dict) -> float:
    X_input_dict = {c: 0 for c in model_cols}
    for k, v in user_inputs.items():
        if k in X_input_dict:
            X_input_dict[k] = v
    X_input = pd.DataFrame([X_input_dict], columns=model_cols)
    for col in X_input.columns:
        X_input[col] = pd.to_numeric(X_input[col], errors="coerce").fillna(0)
    dmat = xgb.DMatrix(X_input.values, feature_names=model_cols)
    preds = booster.predict(dmat)
    if len(preds) == 0:
        raise RuntimeError("Aucune prédiction retournée.")
    return float(preds[0])

# -----------------------------
# PDF Generator
# -----------------------------
def build_pdf(culture, surface, pred_rendement, df_plan):
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
            self.cell(0,10,"Généré le " + datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0, "C")

    pdf = StyledPDF()
    if os.path.exists(DEJAVU_REGULAR):
        pdf.add_font("DejaVu","",DEJAVU_REGULAR, uni=True)
        pdf.add_font("DejaVu","B",DEJAVU_BOLD, uni=True)
    pdf.add_page()
    pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial", "", 12)
    pdf.cell(0,10,f"🌿 Culture : {culture}", ln=True)
    pdf.cell(0,10,f"📐 Surface : {surface} ha    🎯 Rendement prédit : {round(pred_rendement,2)} t/ha", ln=True)
    pdf.ln(5)
    pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial", "B", 12)
    pdf.set_text_color(0,51,102)
    pdf.cell(0,9,"• Détails du plan :", ln=True)
    for _, row in df_plan.iterrows():
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
    pdf.image(qr_buffer, w=30)
    pdf.set_font("DejaVu" if os.path.exists(DEJAVU_REGULAR) else "Arial","",9)
    pdf.cell(0,10,url, ln=True)

    out = BytesIO()
    out_bytes = pdf.output(dest="S").encode("utf-8")
    out.write(out_bytes)
    out.seek(0)
    return out

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("🌾 SmartFactLaser – Fertilisation basée sur données réelles")

cols = st.columns(2)
with cols[0]:
    culture = st.selectbox("🌿 Type de culture", available_cultures)
    surface = st.number_input("Superficie (ha)", min_value=0.1, value=1.0)
with cols[1]:
    year = st.number_input("Année", min_value=2021, max_value=2025, value=2023)
    month = st.selectbox("Mois", list(range(1,13)), index=5)

st.markdown("### 🌤 Paramètres environnementaux")
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
        pred_rendement = predict_yield(user_inputs)
    except Exception as e:
        st.error(f"Erreur lors de la prédiction : {e}")
        st.stop()

    st.success(f"🎯 Rendement prédit : {round(pred_rendement, 2)} t/ha")

    # Générer le plan de fertilisation sans phases
    total_npk = {"N": 0.4, "P2O5": 0.3, "K2O": 0.3}  # ratios arbitraires à ajuster selon culture
    plan_list = []
    for elmt, ratio in total_npk.items():
        dose = pred_rendement * surface * ratio / EFFICIENCES.get(elmt, 1)
        engrais = next((n for n, comp in ENGRAIS_DB.items() if elmt in comp), None)
        dose_engrais = round(dose / ENGRAIS_DB[engrais][elmt], 2) if engrais else None
        plan_list.append({
            "Élément": elmt,
            "Dose kg": round(dose, 2),
            "Engrais": engrais,
            "Dose engrais (kg)": dose_engrais
        })
    df_plan = pd.DataFrame(plan_list)

    st.markdown("### 📋 Plan de fertilisation")
    st.dataframe(df_plan)


    # PDF
    pdf_bytes = build_pdf(culture, surface, pred_rendement, df_plan)
    st.download_button("📄 Télécharger le plan PDF", pdf_bytes, file_name=f"{culture}_fertilisation_plan.pdf", mime="application/pdf")

    # Excel
    excel_bytes = BytesIO()
    with pd.ExcelWriter(excel_bytes, engine="openpyxl") as writer:
        df_plan.to_excel(writer, index=False, sheet_name="Fertilisation")
    excel_bytes.seek(0)
    st.download_button("📥 Télécharger Excel", excel_bytes, file_name=f"{culture}_fertilisation_plan.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Explication
    st.markdown("### ℹ️ Explication rapide")
    st.write(f"- Le rendement estimé ({round(pred_rendement,2)} t/ha) est basé sur les données environnementales et le modèle XGBoost.")
    st.write("- Le plan calcule les besoins totaux en N, P₂O₅ et K₂O selon le rendement estimé.")
    st.write("- Les doses d'engrais sont ajustées selon les efficacités et converties en produits réels.")
    st.success("✅ Plan généré — téléchargez le PDF ou Excel ci-dessous.")
