
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageEnhance
import cv2
from datetime import datetime, timedelta
import json
from config.lang import t

st.set_page_config(page_title="Drone & Imagery", page_icon="🛰", layout="wide")

st.title("🛰 Drone & Imagerie Aérienne")
st.markdown("### Analyse avancée des parcelles par drones et satellites")

# Sidebar controls
st.sidebar.title("Paramètres d'Analyse")

analysis_type = st.sidebar.selectbox(
    "Type d'analyse",
    ["Stress Hydrique", "Détection Maladies", "Croissance Végétale", "Cartographie NDVI", "Analyse Multispectrale"]
)

image_source = st.sidebar.radio(
    "Source d'image",
    ["Upload Local", "Simulation Drone", "Données Satellite"]
)

resolution = st.sidebar.select_slider(
    "Résolution d'analyse",
    options=["Basse (5m/pixel)", "Moyenne (2m/pixel)", "Haute (0.5m/pixel)", "Ultra (0.1m/pixel)"],
    value="Haute (0.5m/pixel)"
)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Analyse d'Image",
    "Cartographie Parcelles",
    "Évolution Temporelle",
    "Rapport Automatisé",
    "Planification Missions"
])

with tab1:
    st.subheader("Analyse d'Image Spectrale")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Upload d'Image**")

        if image_source == "Upload Local":
            uploaded_file = st.file_uploader(
                "Sélectionnez une image drone/satellite",
                type=['png', 'jpg', 'jpeg', 'tiff'],
                help="Formats supportés: RGB, NIR, Multi-spectral"
            )

            if uploaded_file:
                image = Image.open(uploaded_file)
                st.image(image, caption="Image originale", width=300)

        elif image_source == "Simulation Drone":
            st.info("🚁 Mode simulation - Données drone synthétiques")
            # Générer une image simulée
            sim_data = np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8)
            sim_image = Image.fromarray(sim_data)
            st.image(sim_image, caption="Image drone simulée", width=300)
            image = sim_image

        else:  # Données Satellite
            st.info("🛰 Mode satellite - Données Sentinel-2 simulées")
            sat_data = np.random.randint(50, 200, (400, 400, 3), dtype=np.uint8)
            sat_image = Image.fromarray(sat_data)
            st.image(sat_image, caption="Image satellite simulée", width=300)
            image = sat_image

        # Paramètres d'analyse
        st.markdown("**Paramètres Spectraux**")

        bands_to_analyze = st.multiselect(
            "Bandes spectrales",
            ["RGB", "NIR (Proche Infrarouge)", "RED EDGE", "SWIR"],
            default=["RGB", "NIR (Proche Infrarouge)"]
        )

        ndvi_threshold = st.slider(
            "Seuil NDVI santé",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05
        )

    with col2:
        st.markdown("**Résultats d'Analyse**")

        if 'image' in locals():
            with st.spinner("Analyse spectrale en cours..."):
                # Simulation d'analyse NDVI
                ndvi_data = np.random.uniform(0.1, 0.8, (100, 100))

                # Création de la carte NDVI
                fig_ndvi = px.imshow(
                    ndvi_data,
                    color_continuous_scale="RdYlGn",
                    title="Carte NDVI - Index de Végétation",
                    labels={'color': 'NDVI'}
                )
                fig_ndvi.update_layout(height=300)
                st.plotly_chart(fig_ndvi, use_container_width=True)

                # Métriques d'analyse
                healthy_percentage = np.mean(ndvi_data > ndvi_threshold) * 100
                avg_ndvi = np.mean(ndvi_data)
                stress_areas = np.sum(ndvi_data < 0.3)

                col_met1, col_met2, col_met3 = st.columns(3)

                with col_met1:
                    st.metric(
                        "Végétation Saine",
                        f"{healthy_percentage:.1f}%",
                        delta=f"{healthy_percentage - 75:.1f}%" if healthy_percentage > 75 else None
                    )

                with col_met2:
                    st.metric(
                        "NDVI Moyen",
                        f"{avg_ndvi:.3f}",
                        delta="0.05" if avg_ndvi > 0.5 else "-0.02"
                    )

                with col_met3:
                    st.metric(
                        "Zones de Stress",
                        f"{stress_areas}",
                        delta=f"-{stress_areas//10}" if stress_areas < 500 else f"+{stress_areas//20}"
                    )

                # Détection d'anomalies
                st.markdown("**🚨 Alertes Détectées**")

                alerts = []
                if avg_ndvi < 0.4:
                    alerts.append("⚠️ NDVI faible détecté - Possible stress hydrique")
                if stress_areas > 800:
                    alerts.append("🔴 Zones de stress étendues - Inspection recommandée")
                if healthy_percentage < 60:
                    alerts.append("📉 Santé végétale dégradée - Action immédiate requise")

                if alerts:
                    for alert in alerts:
                        st.warning(alert)
                else:
                    st.success("✅ Aucune anomalie majeure détectée")

with tab2:
    st.subheader("Cartographie Intelligente des Parcelles")

    # Sélection de la parcelle
    parcelle_id = st.selectbox(
        "Sélectionner une parcelle",
        ["Parcelle_A1", "Parcelle_B2", "Parcelle_C3", "Parcelle_D4", "Nouveau..."]
    )

    if parcelle_id == "Nouveau...":
        new_parcelle = st.text_input("Nom de la nouvelle parcelle")
        if new_parcelle:
            parcelle_id = new_parcelle

    col1, col2 = st.columns([2, 1])

    with col1:
        # Carte 3D simulée
        x = np.linspace(0, 100, 50)
        y = np.linspace(0, 100, 50)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(X/10) * np.cos(Y/10) * 10 + np.random.normal(0, 1, X.shape)

        fig_3d = go.Figure(data=[go.Surface(
            x=X, y=Y, z=Z,
            colorscale='Earth',
            name='Topographie'
        )])

        fig_3d.update_layout(
            title="Cartographie 3D de la Parcelle",
            scene=dict(
                xaxis_title="Longitude (m)",
                yaxis_title="Latitude (m)",
                zaxis_title="Élévation (m)"
            ),
            height=400
        )

        st.plotly_chart(fig_3d, use_container_width=True)

    with col2:
        st.markdown("**Caractéristiques Parcelle**")

        # Informations de la parcelle
        parcelle_info = {
            "Surface": "12.5 hectares",
            "Pente moyenne": "2.3°",
            "Exposition": "Sud-Est",
            "Type de sol": "Argilo-limoneux",
            "Drainage": "Bon",
            "pH moyen": "6.8"
        }

        for key, value in parcelle_info.items():
            st.write(f"**{key}:** {value}")

        st.markdown("**Recommandations IA**")

        recommendations = [
            "🌾 Culture recommandée: Blé d'hiver",
            "💧 Irrigation: Zone sud nécessite + d'eau",
            "🧪 Fertilisation: Azote modéré",
            "📅 Période optimale: Mars-Avril"
        ]

        for rec in recommendations:
            st.write(rec)

with tab3:
    st.subheader("Évolution Temporelle des Cultures")

    # Sélection de période
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Date de début",
            value=datetime.now() - timedelta(days=90)
        )

    with col2:
        end_date = st.date_input(
            "Date de fin",
            value=datetime.now()
        )

    # Génération de données temporelles
    dates = pd.date_range(start=start_date, end=end_date, freq='W')
    ndvi_evolution = np.random.normal(0.5, 0.1, len(dates))
    ndvi_evolution = np.cumsum(np.random.normal(0, 0.02, len(dates))) + 0.3
    ndvi_evolution = np.clip(ndvi_evolution, 0, 1)

    lai_evolution = ndvi_evolution * 6 + np.random.normal(0, 0.2, len(dates))
    lai_evolution = np.clip(lai_evolution, 0, 8)

    # Graphiques d'évolution
    fig_evolution = go.Figure()

    fig_evolution.add_trace(go.Scatter(
        x=dates,
        y=ndvi_evolution,
        mode='lines+markers',
        name='NDVI',
        line=dict(color='green', width=3),
        yaxis='y'
    ))

    fig_evolution.add_trace(go.Scatter(
        x=dates,
        y=lai_evolution,
        mode='lines+markers',
        name='LAI (Leaf Area Index)',
        line=dict(color='blue', width=3),
        yaxis='y2'
    ))

    fig_evolution.update_layout(
        title="Évolution des Indices de Végétation",
        xaxis_title="Date",
        yaxis=dict(title="NDVI", side="left"),
        yaxis2=dict(title="LAI", side="right", overlaying="y"),
        height=400
    )

    st.plotly_chart(fig_evolution, use_container_width=True)

    # Analyse des tendances
    st.markdown("**Analyse des Tendances**")

    col1, col2, col3 = st.columns(3)

    with col1:
        ndvi_trend = np.polyfit(range(len(ndvi_evolution)), ndvi_evolution, 1)[0]
        trend_direction = "📈 Croissance" if ndvi_trend > 0 else "📉 Déclin"
        st.metric("Tendance NDVI", trend_direction, f"{ndvi_trend:.4f}/semaine")

    with col2:
        current_stage = "Développement végétatif" if np.mean(ndvi_evolution[-4:]) > 0.6 else "Début de cycle"
        st.metric("Stade Cultural", current_stage)

    with col3:
        stress_periods = np.sum(np.diff(ndvi_evolution) < -0.1)
        st.metric("Périodes de Stress", stress_periods, delta=f"{stress_periods-2} vs moy.")

with tab4:
    st.subheader("Rapport Automatisé d'Analyse")

    # Paramètres du rapport
    col1, col2 = st.columns(2)

    with col1:
        report_type = st.selectbox(
            "Type de rapport",
            ["Rapport Hebdomadaire", "Rapport Mensuel", "Rapport de Saison", "Rapport d'Incident"]
        )

        include_sections = st.multiselect(
            "Sections à inclure",
            [
                "Résumé Exécutif",
                "Analyse NDVI",
                "Détection d'Anomalies",
                "Recommandations",
                "Données Météorologiques",
                "Comparaison Historique",
                "Prévisions"
            ],
            default=["Résumé Exécutif", "Analyse NDVI", "Recommandations"]
        )

    with col2:
        export_format = st.selectbox(
            "Format d'export",
            ["PDF", "Word", "Excel", "PowerPoint"]
        )

        language = st.selectbox(
            "Langue du rapport",
            ["Français", "English", "Español"]
        )

    if st.button("🔄 Générer Rapport", use_container_width=True):
        with st.spinner("Génération du rapport en cours..."):
            # Simulation de génération
            import time
            time.sleep(2)

            st.success("✅ Rapport généré avec succès!")

            # Aperçu du rapport
            st.markdown("**Aperçu du Rapport**")

            with st.expander("Résumé Exécutif", expanded=True):
                st.markdown("""
                **Période d'analyse:** {start_date} - {end_date}

                **État général de la parcelle:** ✅ Satisfaisant

                **Points clés:**
                - NDVI moyen: 0.67 (+12% vs période précédente)
                - Zones de stress détectées: 3% de la surface
                - Croissance végétative: Normale pour la saison
                - Recommandation prioritaire: Surveillance irrigation zone Nord-Est

                **Prochaines actions:**
                1. Mission drone dans 7 jours
                2. Analyse sol complémentaire recommandée
                3. Ajustement irrigation si pas de pluie
                """)

            if "Analyse NDVI" in include_sections:
                with st.expander("Analyse NDVI"):
                    st.markdown("""
                    **Évolution NDVI:**
                    - Valeur actuelle: 0.67
                    - Tendance: +0.05 par semaine
                    - Comparaison historique: Dans la normale
                    - Zones problématiques: Secteur D4 (NDVI < 0.4)
                    """)

            # Bouton de téléchargement simulé
            st.download_button(
                label=f"📥 Télécharger Rapport ({export_format})",
                data="Rapport simulé - contenu du fichier",
                file_name=f"rapport_drone_{datetime.now().strftime('%Y%m%d')}.{export_format.lower()}",
                mime="application/octet-stream"
            )

with tab5:
    st.subheader("Planification des Missions Drone")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("**Calendrier des Missions**")

        # Mission scheduler
        mission_type = st.selectbox(
            "Type de mission",
            ["Surveillance Routine", "Inspection Détaillée", "Cartographie", "Urgence"]
        )

        mission_date = st.date_input(
            "Date de mission",
            value=datetime.now() + timedelta(days=1)
        )

        mission_time = st.time_input(
            "Heure de mission",
            value=datetime.now().replace(hour=10, minute=0).time()
        )

        weather_condition = st.select_slider(
            "Conditions météo prévues",
            options=["Défavorable", "Acceptable", "Idéale"],
            value="Idéale"
        )

        drone_model = st.selectbox(
            "Modèle de drone",
            ["DJI Phantom 4 Pro", "DJI Mavic 3", "Parrot Sequoia", "SenseFly eBee"]
        )

        if st.button("📅 Planifier Mission"):
            st.success(f"✅ Mission planifiée pour le {mission_date} à {mission_time}")

            # Ajout à la session state
            if 'planned_missions' not in st.session_state:
                st.session_state.planned_missions = []

            st.session_state.planned_missions.append({
                'type': mission_type,
                'date': mission_date,
                'time': mission_time,
                'weather': weather_condition,
                'drone': drone_model,
                'status': 'Planifiée'
            })

    with col2:
        st.markdown("**Missions Planifiées**")

        if 'planned_missions' in st.session_state and st.session_state.planned_missions:
            for i, mission in enumerate(st.session_state.planned_missions):
                with st.container():
                    st.markdown(f"**Mission #{i+1}**")
                    st.write(f"Type: {mission['type']}")
                    st.write(f"Date: {mission['date']}")
                    st.write(f"Statut: {mission['status']}")

                    if st.button(f"Annuler", key=f"cancel_{i}"):
                        st.session_state.planned_missions.pop(i)
                        st.rerun()

                    st.markdown("---")
        else:
            st.info("Aucune mission planifiée")

        # Recommandations IA
        st.markdown("**🤖 Recommandations IA**")

        ai_recommendations = [
            "☀️ Meilleures heures: 10h-14h",
            "🌤️ Éviter les jours venteux >20km/h",
            "📸 Vol à 100m pour résolution optimale",
            "🔋 Prévoir 2 batteries par mission",
            "📡 Vérifier signal GPS avant décollage"
        ]

        for rec in ai_recommendations:
            st.write(rec)

# Sidebar - Mission status
st.sidebar.markdown("---")
st.sidebar.markdown("**État des Missions**")

if 'planned_missions' in st.session_state:
    missions_count = len(st.session_state.planned_missions)
    st.sidebar.metric("Missions planifiées", missions_count)
else:
    st.sidebar.metric("Missions planifiées", 0)

st.sidebar.metric("Dernière mission", "Il y a 3 jours")
st.sidebar.metric("Heures de vol", "24.5h ce mois")

# Footer
st.markdown("---")
st.markdown("**🛰 Module Drone & Imagerie** - Analyse spectrale avancée pour agriculture de précision")
