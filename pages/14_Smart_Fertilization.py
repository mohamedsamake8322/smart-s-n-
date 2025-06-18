
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import io
from utils.smart_fertilization import smart_fertilization, CropDatabase
from utils.pdf_generator import pdf_generator
from utils.translations import TranslationManager
from utils.data_processing import generate_soil_sample_data

st.set_page_config(page_title="Smart Fertilization", page_icon="🌱", layout="wide")
# Instancier le gestionnaire de traduction
translator = TranslationManager()
# Language selection
lang = st.sidebar.selectbox("Language / Langue", ["en", "fr"], index=1)
# Utilisation correcte de get_text()
st.title(f"🌱 {translator.get_text('smart_fertilization', lang)}")
st.markdown(f"### {translator.get_text('ai_fertilization_subtitle', lang)}")
# Instancier le gestionnaire de traduction
translator = TranslationManager()

# Utiliser la méthode get_text depuis l'instance
text = translator.get_text("smart_fertilization", lang="fr")
# Initialize session state
if 'fertilization_plans' not in st.session_state:
    st.session_state.fertilization_plans = []

if 'soil_data' not in st.session_state:
    st.session_state.soil_data = generate_soil_sample_data()

# Sidebar for quick actions
st.sidebar.title(translator.get_text('quick_actions', lang))

if st.sidebar.button(f"🔄 {translator.get_text('refresh_data', lang)}"):
    st.session_state.soil_data = generate_soil_sample_data()
    st.rerun()

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    translator.get_text('create_plan', lang),
    translator.get_text('crop_database', lang), 
    translator.get_text('ai_optimization', lang),
    translator.get_text('cost_analysis', lang),
    translator.get_text('iot_integration', lang),
    translator.get_text('plan_history', lang)
])

with tab1:
    st.subheader(f"📋 {translator.get_text('create_fertilization_plan', lang)}")
    
    col1, col2 = st.columns(2)  # Corrigé

with col1:
    st.markdown(f"**{translator.get_text('farm_information', lang)}**")

with st.form("fertilization_plan"):
    # Informations agriculteur
    farmer_name = st.text_input(
        translator.get_text('farmer_name', lang),
        value="Jean Dupont",
        help=translator.get_text('farmer_name_help', lang)
    )

    farm_name = st.text_input(
        translator.get_text('farm_name', lang),
        value="Ferme du Soleil Levant",
        help=translator.get_text('farm_name_help', lang)
    )

    # Informations culture ✅ Suppression de la duplication et correction de l'indentation
    crop_type = st.selectbox(
        translator.get_text('crop_type', lang),
        ["wheat", "corn", "rice", "soybeans"],
        format_func=lambda x: {
            "wheat": "Blé", "corn": "Maïs",
            "rice": "Riz", "soybeans": "Soja"
        }[x]
    )

    area = st.number_input(
        translator.get_text('area_hectares', lang),
        min_value=0.1,
        max_value=1000.0,
        value=25.0,
        step=0.1
    )

    planting_date = st.date_input(
        translator.get_text('planting_date', lang),
        value=datetime.now() - timedelta(days=30)
    )

    target_yield = st.number_input(
        translator.get_text('target_yield', lang),
        min_value=1.0,
        max_value=20.0,
        value=6.0,
        step=0.1,
        help=translator.get_text('target_yield_help', lang)
    )

    # Données sol ✅ Correction de `get_text()`
    st.markdown(f"**{translator.get_text('soil_conditions', lang)}**")

    soil_ph = st.slider(
        translator.get_text('soil_ph', lang),
        min_value=4.0,
        max_value=9.0,
        value=6.8,
        step=0.1
    )

    col_a, col_b = st.columns(2)
    with col_a:
        soil_nitrogen = st.number_input(
            translator.get_text('nitrogen_ppm', lang),
            min_value=0,
            max_value=200,
            value=45
        )

        soil_phosphorus = st.number_input(
            translator.get_text('phosphorus_ppm', lang),
            min_value=0,
            max_value=100,
            value=28
        )

    with col_b:
        soil_potassium = st.number_input(
            translator.get_text('potassium_ppm', lang),
            min_value=0,
            max_value=500,
            value=180
        )

        organic_matter = st.number_input(
            translator.get_text('organic_matter', lang),
            min_value=0.0,
            max_value=10.0,
            value=3.2,
            step=0.1
        )

    moisture = st.slider(
        translator.get_text('soil_moisture', lang),
        min_value=0,
        max_value=100,
        value=55,
        help=translator.get_text('moisture_help', lang)
    )

    # Bouton de soumission ✅ Indentation correcte
    submitted = st.form_submit_button(f"🚀 {translator.get_text('generate_plan', lang)}")

if submitted:
    st.success(f"✅ {translator.get_text('plan_generated', lang)}")

# Génération PDF ✅ Suppression de la syntaxe incorrecte `:` à la fin
if st.button(f"📄 {translator.get_text('generate_pdf', lang)}"):
    with st.spinner("Génération du PDF..."):
        try:
            pdf_path = pdf_generator.generate_fertilization_pdf(plan_data, farmer_info)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label=f"💾 {translator.get_text('download_pdf', lang)}",
                    data=pdf_file.read(),
                    file_name=f"plan_fertilisation_{farmer_info['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            st.success("✅ PDF généré avec succès!")
        except Exception as e:
            st.error(f"❌ Erreur génération PDF: {str(e)}")
else: st.info(f"👆 {translator.get_text('create_plan_first', lang)}")

with tab2:
    st.subheader(f"🌾 {translator.get_text('crop_database', lang)}")
    
    crop_db = CropDatabase()
    
    # Sélection de culture pour affichage
    selected_crop = st.selectbox(
        translator.get_text('select_crop_info', lang),
        ["wheat", "corn", "rice", "soybeans"],
        format_func=lambda x: {
            "wheat": "Blé", "corn": "Maïs", 
            "rice": "Riz", "soybeans": "Soja"
        }[x]
    )
    
    crop_info = crop_db.get_crop_info(selected_crop)
    
    if crop_info:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{crop_info['name']} - Stades de Croissance**")
            
            stages_data = []
            for stage_name, stage_info in crop_info['growth_stages'].items():
                stages_data.append({
                    'Stade': stage_name.title(),
                    'Durée (jours)': stage_info['duration_days'],
                    'Description': stage_info['description'],
                    'N (kg/ha)': stage_info['nutrients']['N'],
                    'P (kg/ha)': stage_info['nutrients']['P'],
                    'K (kg/ha)': stage_info['nutrients']['K']
                })
            
            stages_df = pd.DataFrame(stages_data)
            st.dataframe(stages_df, use_container_width=True)
        
        with col2:
            # Graphique des besoins par stade
            stages = list(crop_info['growth_stages'].keys())
            n_values = [crop_info['growth_stages'][s]['nutrients']['N'] for s in stages]
            p_values = [crop_info['growth_stages'][s]['nutrients']['P'] for s in stages]
            k_values = [crop_info['growth_stages'][s]['nutrients']['K'] for s in stages]
            
            fig_stages = go.Figure()
            
            fig_stages.add_trace(go.Scatter(
                x=stages, y=n_values, mode='lines+markers',
                name='Azote (N)', line=dict(color='blue')
            ))
            fig_stages.add_trace(go.Scatter(
                x=stages, y=p_values, mode='lines+markers',
                name='Phosphore (P)', line=dict(color='red')
            ))
            fig_stages.add_trace(go.Scatter(
                x=stages, y=k_values, mode='lines+markers',
                name='Potassium (K)', line=dict(color='green')
            ))
            
            fig_stages.update_layout(
                title="Besoins en Nutriments par Stade",
                xaxis_title="Stades de Croissance",
                yaxis_title="Besoins (kg/ha)",
                height=400
            )
            
            st.plotly_chart(fig_stages, use_container_width=True)
        
        # Besoins totaux et micro-éléments
        st.markdown("**📊 Besoins Nutritionnels Totaux**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_nutrients = crop_info['total_nutrients']
            
            fig_total = px.pie(
                values=list(total_nutrients.values()),
                names=list(total_nutrients.keys()),
                title="Répartition NPK Totale"
            )
            st.plotly_chart(fig_total, use_container_width=True)
        
        with col2:
            st.markdown("**🧪 Micro-éléments Recommandés**")
            
            micro_elements = crop_info['micro_elements']
            for element, amount in micro_elements.items():
                st.write(f"• **{element}**: {amount} kg/ha")

with tab3:
    st.subheader(f"🤖 {translator.get_text('ai_optimization', lang)}")
    
    # Entraînement du modèle IA
    st.markdown("**🎓 Entraînement du Modèle IA**")
    
    if st.button("🚀 Entraîner le Modèle avec Données Historiques"):
        # Génération de données d'exemple pour l'entraînement
        historical_data = []
        
        for i in range(50):
            record = {
                'soil_ph': np.random.normal(6.5, 0.5),
                'soil_nitrogen': np.random.normal(40, 10),
                'soil_phosphorus': np.random.normal(25, 8),
                'soil_potassium': np.random.normal(180, 40),
                'organic_matter': np.random.normal(3.0, 1.0),
                'fertilizer_n_applied': np.random.normal(150, 30),
                'fertilizer_p_applied': np.random.normal(80, 20),
                'fertilizer_k_applied': np.random.normal(120, 25),
                'rainfall_season': np.random.normal(500, 100),
                'temperature_avg': np.random.normal(20, 3),
                'yield_achieved': np.random.normal(5.5, 1.2)
            }
            historical_data.append(record)
        
        with st.spinner("Entraînement en cours..."):
            success = smart_fertilization.train_optimization_model(historical_data)
            
            if success:
                st.success("✅ Modèle IA entraîné avec succès!")
                st.info("Le modèle peut maintenant optimiser automatiquement les plans de fertilisation.")
            else:
                st.error("❌ Erreur lors de l'entraînement du modèle.")
    
    # Simulation d'optimisation
    if smart_fertilization.is_trained:
        st.markdown("**🎯 Simulation d'Optimisation**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("*Conditions de base*")
            base_yield = st.number_input("Rendement prévu (t/ha)", value=5.0, step=0.1)
            base_n = st.number_input("Azote planifié (kg/ha)", value=150)
            base_p = st.number_input("Phosphore planifié (kg/ha)", value=80)
            
        with col2:
            st.markdown("*Conditions optimisées*")
            # Simulation d'optimisation
            optimized_yield = base_yield * np.random.uniform(1.05, 1.15)
            optimized_n = base_n * np.random.uniform(0.95, 1.05)
            optimized_p = base_p * np.random.uniform(0.95, 1.05)
            
            st.metric("Rendement optimisé", f"{optimized_yield:.1f} t/ha", 
                     f"+{optimized_yield - base_yield:.1f}")
            st.metric("Azote optimisé", f"{optimized_n:.0f} kg/ha", 
                     f"{optimized_n - base_n:+.0f}")
            st.metric("Phosphore optimisé", f"{optimized_p:.0f} kg/ha", 
                     f"{optimized_p - base_p:+.0f}")
        
        # Graphique d'amélioration
        improvement_data = {
            'Métrique': ['Rendement', 'Efficacité N', 'Efficacité P', 'Coût'],
            'Base': [100, 100, 100, 100],
            'Optimisé': [110, 105, 103, 98]
        }
        
        fig_improvement = px.bar(
            improvement_data,
            x='Métrique',
            y=['Base', 'Optimisé'],
            title="Amélioration avec IA (%)",
            barmode='group'
        )
        st.plotly_chart(fig_improvement, use_container_width=True)
    
    else:
        st.info("🎓 Entraînez d'abord le modèle IA pour accéder aux fonctionnalités d'optimisation.")

with tab4:
    st.subheader(f"💰 {translator.get_text('cost_analysis', lang)}")
    
    if st.session_state.fertilization_plans:
        # Sélection du plan à analyser
        plan_options = [f"Plan {p['id']} - {p['farmer_info']['name']}" 
                       for p in st.session_state.fertilization_plans]
        
        selected_plan_idx = st.selectbox(
            "Sélectionner un plan pour analyse",
            range(len(plan_options)),
            format_func=lambda x: plan_options[x]
        )
        
        selected_plan = st.session_state.fertilization_plans[selected_plan_idx]
        cost_data = selected_plan['plan_data']['total_cost_estimate']
        
        # Métriques de coût
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Coût Total",
                f"{cost_data['total_cost_euros']:.2f} €"
            )
        
        with col2:
            st.metric(
                "Coût/hectare",
                f"{cost_data['cost_per_hectare']:.2f} €/ha"
            )
        
        with col3:
            area = selected_plan['farmer_info']['area']
            cost_per_ton = cost_data['total_cost_euros'] / (area * 5.5)  # Estimation 5.5 t/ha
            st.metric(
                "Coût/tonne",
                f"{cost_per_ton:.2f} €/t"
            )
        
        with col4:
            # ROI estimé
            revenue_per_ton = 200  # Prix estimé
            estimated_revenue = area * 5.5 * revenue_per_ton
            roi = ((estimated_revenue - cost_data['total_cost_euros']) / cost_data['total_cost_euros']) * 100
            st.metric(
                "ROI Estimé",
                f"{roi:.1f}%"
            )
        
        # Graphiques de coûts
        col1, col2 = st.columns(2)
        
        with col1:
            # Répartition des coûts par nutriment
            fig_cost_pie = px.pie(
                values=list(cost_data['cost_breakdown'].values()),
                names=list(cost_data['cost_breakdown'].keys()),
                title="Répartition des Coûts par Nutriment"
            )
            st.plotly_chart(fig_cost_pie, use_container_width=True)
        
        with col2:
            # Comparaison avec moyennes secteur
            sector_avg = {'N': 120, 'P': 180, 'K': 80}  # Moyennes secteur €/ha
            current_costs = {k: v/area for k, v in cost_data['cost_breakdown'].items()}
            
            comparison_data = {
                'Nutriment': list(sector_avg.keys()),
                'Secteur (€/ha)': list(sector_avg.values()),
                'Votre Plan (€/ha)': [current_costs.get(k, 0) for k in sector_avg.keys()]
            }
            
            fig_comparison = px.bar(
                comparison_data,
                x='Nutriment',
                y=['Secteur (€/ha)', 'Votre Plan (€/ha)'],
                title="Comparaison avec Moyennes Secteur",
                barmode='group'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Analyse de sensibilité
        st.markdown("**📈 Analyse de Sensibilité des Prix**")
        
        price_variation = st.slider(
            "Variation des prix d'engrais (%)",
            min_value=-50,
            max_value=50,
            value=0,
            step=5
        )
        
        adjusted_cost = cost_data['total_cost_euros'] * (1 + price_variation/100)
        cost_difference = adjusted_cost - cost_data['total_cost_euros']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric(
                "Coût Ajusté",
                f"{adjusted_cost:.2f} €",
                f"{cost_difference:+.2f} €"
            )
        
        with col2:
            adjusted_roi = ((estimated_revenue - adjusted_cost) / adjusted_cost) * 100
            roi_difference = adjusted_roi - roi
            st.metric(
                "ROI Ajusté",
                f"{adjusted_roi:.1f}%",
                f"{roi_difference:+.1f}%"
            )
    
    else:
        st.info("📋 Créez d'abord un plan de fertilisation pour accéder à l'analyse des coûts.")

with tab5:
    st.subheader(f"📡 {translator.get_text('iot_integration', lang)}")
    
    # Simulation d'intégration IoT
    st.markdown("**🌐 Intégration Capteurs IoT**")
    
    # Données capteurs simulées
    current_conditions = {
        'soil_moisture': np.random.normal(55, 10),
        'soil_temperature': np.random.normal(18, 3),
        'air_temperature': np.random.normal(22, 5),
        'humidity': np.random.normal(65, 15),
        'rainfall_24h': np.random.exponential(2)
    }
    
    # Affichage des conditions actuelles
    st.markdown("**📊 Conditions Actuelles des Capteurs**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        moisture = current_conditions['soil_moisture']
        moisture_status = "🟢" if 40 <= moisture <= 70 else "🟡" if 30 <= moisture < 40 else "🔴"
        st.metric(
            "Humidité Sol",
            f"{moisture:.1f}%",
            help="Humidité du sol mesurée"
        )
        st.write(f"Statut: {moisture_status}")
    
    with col2:
        soil_temp = current_conditions['soil_temperature']
        st.metric(
            "Temp. Sol",
            f"{soil_temp:.1f}°C"
        )
    
    with col3:
        air_temp = current_conditions['air_temperature']
        st.metric(
            "Temp. Air",
            f"{air_temp:.1f}°C"
        )
    
    with col4:
        humidity = current_conditions['humidity']
        st.metric(
            "Humidité Air",
            f"{humidity:.1f}%"
        )
    
    with col5:
        rainfall = current_conditions['rainfall_24h']
        st.metric(
            "Pluie 24h",
            f"{rainfall:.1f}mm"
        )
    
    # Alertes automatiques
    st.markdown("**🚨 Alertes Automatiques**")
    
    alerts = []
    
    if moisture < 30:
        alerts.append("💧 URGENT: Humidité sol faible - Irrigation recommandée")
    elif moisture > 80:
        alerts.append("⚠️ Humidité sol élevée - Risque de lessivage")
    
    if rainfall > 20:
        alerts.append("🌧️ Pluies importantes - Reporter application d'engrais")
    
    if air_temp > 30:
        alerts.append("🌡️ Températures élevées - Stress thermique possible")
    
    if humidity > 85:
        alerts.append("🍄 Humidité élevée - Surveillance maladies renforcée")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ Conditions normales - Aucune alerte")
    
    # Recommandations automatiques
    st.markdown("**🤖 Recommandations Automatiques**")
    
    recommendations = []
    
    if moisture < 40:
        recommendations.append("Déclencher irrigation zone prioritaire")
    
    if rainfall > 15:
        recommendations.append("Reporter fertilisation prévue de 2-3 jours")
    
    if air_temp > 25 and humidity < 50:
        recommendations.append("Augmenter fréquence irrigation")
    
    if len(recommendations) > 0:
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.info("Aucune action particulière requise")
    
    # Graphique tendances temps réel
    st.markdown("**📈 Tendances Temps Réel (7 derniers jours)**")
    
    # Génération données historiques simulées
    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    moisture_history = [np.random.normal(55, 8) for _ in range(7)]
    temp_history = [np.random.normal(22, 4) for _ in range(7)]
    
    fig_trends = go.Figure()
    
    fig_trends.add_trace(go.Scatter(
        x=dates,
        y=moisture_history,
        mode='lines+markers',
        name='Humidité Sol (%)',
        yaxis='y',
        line=dict(color='blue')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=dates,
        y=temp_history,
        mode='lines+markers',
        name='Température (°C)',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig_trends.update_layout(
        title="Évolution des Conditions",
        xaxis_title="Date",
        yaxis=dict(title="Humidité (%)", side="left"),
        yaxis2=dict(title="Température (°C)", side="right", overlaying="y"),
        height=400
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)

with tab6:
    st.subheader(f"📚 {translator.get_text('plan_history', lang)}")
    
    if st.session_state.fertilization_plans:
        # Tableau des plans
        plans_data = []
        for plan in st.session_state.fertilization_plans:
            farmer_info = plan['farmer_info']
            plan_data = plan['plan_data']
            
            plans_data.append({
                'ID': plan['id'],
                'Agriculteur': farmer_info['name'],
                'Exploitation': farmer_info['farm_name'],
                'Culture': plan_data['crop_info']['name'],
                'Superficie': f"{farmer_info['area']} ha",
                'Coût Total': f"{plan_data['total_cost_estimate']['total_cost_euros']:.2f} €",
                'Date Création': datetime.fromisoformat(plan['created_date']).strftime("%d/%m/%Y"),
                'Stade Actuel': plan_data['crop_info']['current_stage']
            })
        
        plans_df = pd.DataFrame(plans_data)
        st.dataframe(plans_df, use_container_width=True)
        
        # Analyses comparatives
        if len(st.session_state.fertilization_plans) > 1:
            st.markdown("**📊 Analyses Comparatives**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Coûts par exploitation
                costs = [p['plan_data']['total_cost_estimate']['total_cost_euros'] 
                        for p in st.session_state.fertilization_plans]
                farms = [p['farmer_info']['farm_name'] 
                        for p in st.session_state.fertilization_plans]
                
                fig_costs = px.bar(
                    x=farms,
                    y=costs,
                    title="Coûts par Exploitation (€)",
                    labels={'x': 'Exploitation', 'y': 'Coût (€)'}
                )
                st.plotly_chart(fig_costs, use_container_width=True)
            
            with col2:
                # Qualité sol moyenne
                soil_qualities = [p['plan_data']['soil_analysis']['soil_quality_score'] 
                                for p in st.session_state.fertilization_plans]
                
                fig_quality = px.histogram(
                    x=soil_qualities,
                    nbins=10,
                    title="Distribution Qualité Sol",
                    labels={'x': 'Score Qualité', 'y': 'Nombre d\'Exploitations'}
                )
                st.plotly_chart(fig_quality, use_container_width=True)
        
        # Export des données
        if st.button("📥 Exporter Historique (JSON)"):
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_plans': len(st.session_state.fertilization_plans),
                'plans': st.session_state.fertilization_plans
            }
            
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="💾 Télécharger JSON",
                data=json_str,
                file_name=f"historique_fertilisation_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    else:
        st.info("📋 Aucun plan de fertilisation créé pour le moment.")
        st.markdown("👆 Utilisez l'onglet **Créer Plan** pour commencer.")

# Footer avec informations
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    🌱 Système de Fertilisation Intelligente | 
    Optimisé par IA | 
    Intégration IoT | 
    Génération PDF Automatique
</div>
""", unsafe_allow_html=True)
