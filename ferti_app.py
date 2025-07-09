import streamlit as st # type: ignore
import json
import os
import pandas as pd # type: ignore
from fpdf import FPDF # type: ignore
from datetime import datetime
import qrcode # type: ignore
from io import BytesIO
import sqlite3
from sqlite3 import Error
import leafmap.foliumap as leafmap # type: ignore
from config.lang import t
# ----- CONFIGURATION INITIALE -----
# DRAPEAUX PAR LANGUE
lang_labels = {
    "fr": "🇫🇷 Français",
    "en": "🇬🇧 English",
    "ar": "🇸🇦 العربية",
    "tr": "🇹🇷 Türkçe",
    "zh": "🇨🇳 中文",
    "wo": "🌍 Wolof",
    "bm": "🌍 Bambara",
    "ha": "🌍 Hausa",
    "ff": "🌍 Fulfulde",
    "mo": "🌍 Mooré"
}

with st.sidebar:
    st.markdown("### 🌐 Langue / Language")
    lang_options = list(lang_labels.values())
    selected_label = st.selectbox("🌐", lang_options, index=lang_options.index("🇫🇷 Français"))
    selected_lang = [code for code, label in lang_labels.items() if label == selected_label][0]

# ----- CONFIG POLICES -----
BASE_PATH = "C:/plateforme-agricole-complete-v2/fonts/dejavu-fonts-ttf-2.37/ttf/"
dejavu_regular = os.path.join(BASE_PATH, "DejaVuSans.ttf")
dejavu_bold = os.path.join(BASE_PATH, "DejaVuSans-Bold.ttf")

# ----- CONFIG AGRONOMIE -----
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

# ----- SYSTÈME EXPERT SOL/CLIMAT -----
SOIL_RULES = {
    "Sableux": {
        "adjustments": {"N": 1.2, "P2O5": 1.1, "K2O": 0.9},
        "notes": "Sol drainant, besoins accrus en azote"
    },
    "Argileux": {
        "adjustments": {"N": 0.8, "P2O5": 0.9, "K2O": 1.2},
        "notes": "Rétention d'eau élevée, réduire azote"
    },
    "Limon": {
        "adjustments": {"N": 1.0, "P2O5": 1.0, "K2O": 1.0},
        "notes": "Sol équilibré"
    },
    "Volcanique": {
        "adjustments": {"P2O5": 0.7, "K2O": 1.3},
        "notes": "Riche en minéraux, moins de phosphore"
    },
    "Tourbe": {
        "adjustments": {"N": 1.3, "K2O": 1.4},
        "notes": "Sol acide, besoins accrus"
    }
}

CLIMATE_RULES = {
    "Sec": {"water_soluble": True, "split_applications": 3},
    "Humide": {"slow_release": True, "split_applications": 2},
    "Tropical": {"split_applications": 4},
    "Désertique": {"water_soluble": True, "split_applications": 5},
    "Tempéré": {"split_applications": 3}
}

# ----- BASE DE DONNÉES HISTORIQUE -----
def create_connection():
    """Crée une connexion à la DB SQLite"""
    conn = None
    try:
        conn = sqlite3.connect('fertilization_history.db')
        return conn
    except Error as e:
        st.error(f"Erreur DB: {e}")
    return conn

def init_db(conn):
    """Initialise la table si elle n'existe pas"""
    try:
        sql = '''CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    culture TEXT,
                    surface REAL,
                    rendement REAL,
                    soil_type TEXT,
                    climate TEXT,
                    date TEXT,
                    recommendations TEXT
                )'''
        conn.execute(sql)
    except Error as e:
        st.error(f"Erreur d'initialisation: {e}")

# Initialisation au démarrage
conn = create_connection()
if conn:
    init_db(conn)

# ----- FONCTIONS UTILITAIRES -----
def adjust_recommendations(df, soil_type, climate):
    """Ajuste les recommandations basées sur le sol et climat"""
    if soil_type in SOIL_RULES:
        adj = SOIL_RULES[soil_type]["adjustments"]
        for elmt in adj:
            df.loc[df["Élément"] == elmt, "Dose kg"] *= adj[elmt]

    if climate in CLIMATE_RULES:
        df["Forme"] = "Standard"
        if CLIMATE_RULES[climate].get("water_soluble"):
            df.loc[df["Engrais"] == "Urée", "Forme"] = "Soluble"
        if CLIMATE_RULES[climate].get("slow_release"):
            df.loc[df["Engrais"] == "MAP", "Forme"] = "Libération lente"

    return df

@st.cache_data
def get_fertilizer_info(engrais_name):
    """Retourne des infos pédagogiques sur les engrais"""
    tooltips = {
        "Urée": t.get("urea_tooltip", "Fournit de l'azote pour la croissance végétative"),
        "MAP": t.get("map_tooltip", "Fournit du phosphore pour le développement racinaire"),
        "KCl": t.get("kcl_tooltip", "Fournit du potassium pour la fructification"),
        "Sulfate de magnésium": t.get("mg_tooltip", "Corrige les carences en magnésium"),
        "Soufre (Sulfate)": t.get("s_tooltip", "Essentiel pour la synthèse des protéines"),
        "Sulfate de zinc": t.get("zn_tooltip", "Important pour la croissance et le développement"),
        "Borax": t.get("b_tooltip", "Favorise la floraison et la fructification")
    }
    return tooltips.get(engrais_name, t.get("default_tooltip", "Engrais minéral"))

def show_climate_map():
    """Affiche une carte des zones climatiques"""
    m = leafmap.Map(center=[8, 10], zoom=5)
    m.add_basemap("HYBRID")

    # Couche climatique (exemple simplifié)
    climate_zones = {
        "Sec": [[15, -5], [20, 15], [5, 10]],
        "Humide": [[5, -10], [0, 10], [-5, 20]],
        "Tropical": [[-10, -20], [-5, 30], [10, 25]],
        "Désertique": [[15, 0], [30, 40], [20, 20]],
        "Tempéré": [[35, -10], [50, 20], [40, 30]]
    }

    for zone, coords in climate_zones.items():
        m.add_polygon(coords, layer_name=zone, info_mode="on_click")

    return m

# ----- CHARGEMENT DONNÉES -----
with open(FERTI_PATH, encoding='utf-8') as f:
    fertibase = json.load(f)
with open(BESOINS_PATH, encoding='utf-8') as f:
    raw_data = json.load(f)

besoins_db = {}
for bloc in raw_data:
    besoins_db.update(bloc.get("cultures", bloc))

# ----- INTERFACE UTILISATEUR -----
st.title(t("🌾 Plan de Fertilisation par Phase", selected_lang))
# Onglets principaux
tab1, tab2 = st.tabs(["Recommandations", "Carte Climatique"])

with tab1:
    # Section paramètres avancés
    with st.expander(t.get("advanced_settings", "🔧 Paramètres avancés")):
        col1, col2 = st.columns(2)
        with col1:
            soil_type = st.selectbox(
                t.get("soil_type_label", "Type de sol"),
                ["Tous", "Sableux", "Argileux", "Limon", "Volcanique", "Tourbe"],
                index=0
            )
            climate = st.selectbox(
                t.get("climate_label", "Climat"),
                ["Tous", "Sec", "Humide", "Tropical", "Désertique", "Tempéré"],
                index=0
            )

        with col2:
            growth_stage = st.selectbox(
                t.get("growth_stage_label", "Stade de croissance"),
                ["Pré-plantation", "Germination", "Croissance", "Floraison", "Fructification"],
                index=0
            )

            if st.checkbox(t.get("show_history", "Afficher l'historique")):
                if conn:
                    history = pd.read_sql(
                        "SELECT culture, date, soil_type FROM history ORDER BY date DESC LIMIT 5",
                        conn
                    )
                    st.dataframe(history)
                else:
                    st.warning("Connexion à la base de données indisponible")

    # Sélection principale
    culture_code = st.selectbox(t["select_culture"], list(besoins_db.keys()))
    surface = st.number_input(t["surface_label"], min_value=0.1, value=1.0, step=0.1)
    rendement = st.number_input(t["yield_label"], min_value=0.1, value=5.0, step=0.1)

    if st.button(t["generate_button"], key="generate_plan"):
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

        # Ajustements basés sur le sol et climat
        if soil_type != "Tous" or climate != "Tous":
            df = adjust_recommendations(df, soil_type, climate)

        # Ajout des colonnes pédagogiques
        df["Méthode recommandée"] = df["Engrais"].apply(lambda x: {
            "Urée": t.get("broadcast_method", "Épandre en surface"),
            "MAP": t.get("incorporate_method", "Incorporer au sol"),
            "KCl": t.get("broadcast_method", "Épandre en surface"),
            "Sulfate de magnésium": t.get("foliar_method", "Pulvérisation foliaire"),
            "Soufre (Sulfate)": t.get("incorporate_method", "Incorporer au sol"),
            "Sulfate de zinc": t.get("foliar_method", "Pulvérisation foliaire"),
            "Borax": t.get("broadcast_method", "Épandre en surface")
        }.get(x, t.get("default_method", "Voir instructions")))

        df["Rôle"] = df["Engrais"].apply(lambda x: {
            "Urée": t.get("nitrogen_role", "Croissance végétative"),
            "MAP": t.get("phosphorus_role", "Développement racinaire"),
            "KCl": t.get("potassium_role", "Fructification/Qualité"),
            "Sulfate de magnésium": t.get("magnesium_role", "Photosynthèse"),
            "Soufre (Sulfate)": t.get("sulfur_role", "Synthèse protéique"),
            "Sulfate de zinc": t.get("zinc_role", "Croissance et développement"),
            "Borax": t.get("boron_role", "Floraison/Fructification")
        }.get(x, t.get("default_role", "Nutriment essentiel")))

        # Affichage des résultats
        st.markdown(f"### {t['phase_plan']}")

        edited_df = st.data_editor(
            df.style.applymap(lambda x: "background-color: #e6f3ff" if x in ["N", "P2O5"] else "", subset=["Élément"]),
            column_config={
                "Phase": st.column_config.TextColumn(width="medium"),
                "Élément": st.column_config.TextColumn(
                    width="small",
                    help=t.get("element_help", "Élément nutritif")
                ),
                "Engrais": st.column_config.TextColumn(
                    help=get_fertilizer_info(df["Engrais"].iloc[0])
                ),
                "Méthode recommandée": st.column_config.TextColumn(
                    width="large",
                    help=t.get("method_help", "Méthode d'application recommandée")
                )
            },
            hide_index=True,
            use_container_width=True
        )

        # Sauvegarde historique
        if conn:
            try:
                conn.execute(
                    '''INSERT INTO history
                    (user_id, culture, surface, rendement, soil_type, climate, date, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    ("user123", culture_code, surface, rendement, soil_type, climate,
                     datetime.now().isoformat(), df.to_json())
                )
                conn.commit()
                st.success("Recommandation sauvegardée dans l'historique")
            except Error as e:
                st.warning(f"Historique non sauvegardé: {e}")

        # Génération PDF
        class StyledPDF(FPDF):
            def header(self):
                self.set_fill_color(0, 102, 204)
                self.rect(0, 0, self.w, 20, 'F')
                self.set_font("DejaVu", "B", 14)
                self.set_text_color(255, 255, 255)
                self.set_y(6)
                self.cell(0, 8, t["phase_plan"], align="C")
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font("DejaVu", "", 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, t["generated_by"] + datetime.now().strftime("%d/%m/%Y %H:%M"), 0, 0, "C")

        pdf = StyledPDF()
        pdf.add_font("DejaVu", "", dejavu_regular)
        pdf.add_font("DejaVu", "B", dejavu_bold)
        pdf.add_page()
        pdf.set_font("DejaVu", "", 12)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(5)
        pdf.cell(0, 10, f"{t['select_culture']} : {culture['nom_commun']}", ln=True)
        pdf.cell(0, 10, f"{t['surface_label']} : {surface} ha    {t['yield_label']} : {rendement} t/ha", ln=True)
        pdf.ln(5)

        for phase in df["Phase"].unique():
            pdf.set_font("DejaVu", "B", 12)
            pdf.set_text_color(0, 51, 102)
            pdf.cell(0, 9, f"{t['phase_label']} {phase}", ln=True)
            for _, row in df[df["Phase"] == phase].iterrows():
                ligne = f"{row['Élément']} : {row['Dose kg']} kg → {row['Engrais']} ({row['Dose engrais (kg)']} kg)"
                pdf.set_font("DejaVu", "", 11)
                pdf.set_text_color(0, 0, 0)
                pdf.cell(0, 8, ligne, ln=True)

        # LÉGENDE
        pdf.ln(5)
        pdf.set_font("DejaVu", "B", 12)
        pdf.set_text_color(0, 51, 102)
        pdf.cell(0, 10, t["legend_title"], ln=True)
        pdf.set_font("DejaVu", "", 10)
        pdf.set_text_color(0, 0, 0)
        for engrais in sorted({row["Engrais"] for row in phase_data if row["Engrais"]}):
            nutriments = ENGRAIS_DB.get(engrais, {})
            contenu = ", ".join([f"{k} – {int(v * 100)}%" for k, v in nutriments.items()])
            pdf.cell(0, 8, f"- {engrais} : {contenu}", ln=True)

        # QR CODE
        url = f"https://sama-agrolink.com/fertiplan/{culture_code}"
        qr_img = qrcode.make(url)
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)

        pdf.ln(10)
        pdf.set_font("DejaVu", "B", 12)
        pdf.cell(0, 10, t["online_access"], ln=True)
        pdf.image(qr_buffer, w=30)
        pdf.set_font("DejaVu", "", 9)
        pdf.cell(0, 10, url, ln=True)

        # EXPORT PDF
        file_path = f"{culture_code}_fertilisation_plan.pdf"
        pdf.output(file_path)
        with open(file_path, "rb") as f:
            st.download_button(t["download_pdf"], f, file_name=file_path, mime="application/pdf")

        # EXPORT EXCEL
        excel_path = f"{culture_code}_fertilisation_plan.xlsx"
        df.to_excel(excel_path, index=False)
        with open(excel_path, "rb") as f_excel:
            st.download_button(t["download_excel"], f_excel, file_name=excel_path, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

with tab2:
    st.markdown("### 🌍 Carte des Zones Climatiques")
    st.write("Sélectionnez votre zone pour adapter les recommandations:")

    m = show_climate_map()
    m.to_streamlit(height=500)

    st.info("""
    **Légende:**
    - Zones **bleues**: Climats humides
    - Zones **rouges**: Climats secs/désertiques
    - Zones **vertes**: Climats tropicaux
    """)

# Fermeture connexion DB
if conn:
    conn.close()
