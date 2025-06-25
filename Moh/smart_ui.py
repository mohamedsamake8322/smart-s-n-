import streamlit as st
from smart_fertilizer_engine import generate_fertilization_plan, SoilData
from regional_context import get_region_by_country
from pdf_generator import generate_pdf_report  # à créer

# Langues disponibles
LANGUAGES = {
    "fr": "Français",
    "sw": "Swahili",
    "ha": "Haoussa"
}

lang = st.sidebar.selectbox("🌐 Langue", options=list(LANGUAGES.keys()), format_func=lambda x: LANGUAGES[x])

# Formulaire utilisateur
st.title("🌱 Plan de Fertilisation Intelligent")
country = st.selectbox("🌍 Pays", ["Mali", "Rwanda", "Côte d'Ivoire", "Kenya"])
region = get_region_by_country(country)

crop = st.selectbox("🌾 Culture", region.crops)
area = st.number_input("📐 Superficie (ha)", min_value=0.1, value=1.0)
yield_target = st.number_input("🎯 Rendement cible (t/ha)", min_value=1.0, value=6.0)
planting_date = st.date_input("📅 Date de plantation")

# Données sol
st.subheader("🧪 Analyse du sol")
soil = SoilData(
    ph=st.slider("pH", 4.0, 9.0, 6.5),
    organic_matter=st.slider("Matière organique (%)", 0.0, 10.0, 2.5),
    nitrogen_ppm=st.slider("Azote (ppm)", 0, 200, 40),
    phosphorus_ppm=st.slider("Phosphore (ppm)", 0, 100, 20),
    potassium_ppm=st.slider("Potassium (ppm)", 0, 300, 150)
)

if st.button("🚀 Générer le plan"):
    plan = generate_fertilization_plan(crop, soil, area, planting_date, yield_target)
    st.success("✅ Plan généré avec succès !")

    for phase in plan["phases"]:
        st.markdown(f"**{phase['stage'].capitalize()}** – {phase['date'].strftime('%d/%m/%Y')}")
        st.write(f"N: {phase['N']} kg/ha | P: {phase['P']} kg/ha | K: {phase['K']} kg/ha")
        st.write(f"Micro-éléments : {', '.join(phase['micro_elements'])}")

    if st.button("📄 Télécharger PDF"):
        pdf_bytes = generate_pdf_report(plan, region, country)
        st.download_button("💾 Télécharger le rapport", data=pdf_bytes, file_name="plan_fertilisation.pdf", mime="application/pdf")
