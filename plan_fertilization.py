import streamlit as st
import json
import math

# ----------- 🔹 Fonctions utilitaires ----------
def get_engrais_equivalents():
    return {
        "Urée": {"N": 0.46},
        "DAP (18-46-0)": {"N": 0.18, "P2O5": 0.46},
        "NPK 15-15-15": {"N": 0.15, "P2O5": 0.15, "K2O": 0.15},
        "Sulfate de potassium": {"K2O": 0.50},
        "MAP": {"P2O5": 0.52, "N": 0.11},
        "Sulphate de zinc": {"Zn": 0.22},
        "Cuivre sulfate": {"Cu": 0.25},
        "Bore (Borax)": {"B": 0.11},
        "Chélate Fer (EDDHA)": {"Fe": 0.06},
        "Chélate Mn (EDTA)": {"Mn": 0.13}
    }

def get_efficiences():
    return {
        "N": 0.70,
        "P2O5": 0.50,
        "K2O": 0.60,
        "CaO": 0.50,
        "MgO": 0.50,
        "SO3": 0.60,
        "Fe": 0.30,
        "Mn": 0.30,
        "Zn": 0.30,
        "Cu": 0.30,
        "B": 0.30
    }

# ----------- 📂 Charger les données ----------
with open("C:\\plateforme-agricole-complete-v2\\pheno_phases.json", "r", encoding="utf-8") as f:
    phenology = json.load(f)

with open("C:\\plateforme-agricole-complete-v2\\besoins des plantes en nutriments.json", "r", encoding="utf-8") as f:
    culture_data = json.load(f)

with open("knowledge/fertilization_phased_db.json", "r", encoding="utf-8") as f:
    fertibase = json.load(f)

engrais_db = get_engrais_equivalents()
eff_db = get_efficiences()

# ----------- 🎛️ Interface Streamlit ----------
st.title("📊 Calcul des Besoins en Engrais par Culture")
st.markdown("Entrez les paramètres pour générer un plan de fertilisation personnalisé.")

cultures = list(culture_data["cultures"].keys())
culture_code = st.selectbox("🌱 Choisir une culture", cultures)
surface = st.number_input("📐 Superficie cultivée (en hectares)", 0.1, step=0.1)
rendement = st.number_input("🎯 Rendement visé (en tonnes par hectare)", 0.1, step=0.1)
mode_app = st.selectbox("🧴 Méthode d’application", ["volée", "localisée", "fertirrigation"])
zone = st.text_input("📍 Zone géographique (pays ou région)").strip().lower()

# ----------- 🧠 Calculs ----------
if st.button("🔍 Calculer les besoins en engrais"):
    culture = culture_data["cultures"][culture_code]
    st.subheader(f"🧾 Résumé pour {culture['nom_commun']} — {surface} ha — {rendement} t/ha")

    besoins_totaux = {}
    st.markdown("### 💡 Exportation totale en nutriments")

    for element, info in culture["export_par_tonne"].items():
        unite = info["unite"]
        valeur = info["valeur"] * rendement * surface / 1000 if unite.endswith("g/t") else info["valeur"] * rendement * surface
        if unite.endswith("g/t"):
            unite_affiche = "kg"
        else:
            unite_affiche = unite
        besoins_totaux[element] = round(valeur / eff_db.get(element, 1), 2)
        st.write(f"- {element} : {round(valeur,2)} {unite_affiche} → ⚠️ corrigé avec efficacité : {besoins_totaux[element]} kg")

    st.markdown("---")
    st.markdown("### 🧪 Conversion en engrais commerciaux")
    for engrais, composants in engrais_db.items():
        total_apport = 0
        composants_utiles = []
        for nutr, ratio in composants.items():
            if nutr in besoins_totaux:
                dose_engrais = besoins_totaux[nutr] / ratio
                composants_utiles.append((nutr, dose_engrais))
                total_apport = max(total_apport, dose_engrais)

        if composants_utiles:
            total_zone = total_apport
            st.write(f"**{engrais}** → 💼 {round(total_apport,2)} kg nécessaires pour couvrir les besoins (tous nutriments confondus)")
            for nutr, d in composants_utiles:
                st.caption(f" - {nutr} : {round(d, 2)} kg pour {besoins_totaux[nutr]} kg nécessaires")

    # ----------- 🔎 Plan par phase (si disponible) ----------
    st.markdown("---")
    st.markdown("### 📋 Plan de fertilisation par phases (si disponible)")
    culture_key = culture_code.lower()
    try:
        phases = phenology[culture_key]
        plan = fertibase[culture_key][f"{rendement} t/ha"][mode_app][zone]

        for phase in phases:
            st.subheader(f"📌 Phase : {phase}")
            if phase in plan:
                for dose in plan[phase]:
                    engrais = dose["fertilizer"]
                    par_ha = dose["dose_kg_ha"]
                    total = round(par_ha * surface, 2)
                    st.write(f"- {engrais} : {par_ha} kg/ha → **{total} kg au total**")
            else:
                st.warning(f"Pas de plan d’engrais pour la phase : {phase}")
    except KeyError:
        st.error("❌ Aucune donnée disponible pour ce plan de phases dans la base de données actuelle.")

    st.success("✅ Calcul terminé. Les résultats sont donnés à titre indicatif.")
