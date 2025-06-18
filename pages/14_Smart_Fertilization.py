
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

st.set_page_config(page_title="Smart Fertilization", page_icon="ðŸŒ±", layout="wide")
# Instancier le gestionnaire de traduction
translator = TranslationManager()
# Language selection
lang = st.sidebar.selectbox("Language / Langue", ["en", "fr"], index=1)
# Utilisation correcte de get_text()
st.title(f"ðŸŒ± {translator.get_text('smart_fertilization', lang)}")
st.markdown(f"### {translator.get_text('ai_fertilization_subtitle', lang)}")
# Instancier le gestionnaire de traduction
translator = TranslationManager()

# Utiliser la mÃ©thode get_text depuis l'instance
text = translator.get_text("smart_fertilization", lang="fr")
# Initialize session state
if 'fertilization_plans' not in st.session_state:
    st.session_state.fertilization_plans = []

if 'soil_data' not in st.session_state:
    st.session_state.soil_data = generate_soil_sample_data()

# Sidebar for quick actions
st.sidebar.title(translator.get_text('quick_actions', lang))

if st.sidebar.button(f"ðŸ”„ {translator.get_text('refresh_data', lang)}"):
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
    st.subheader(f"ðŸ“‹ {translator.get_text('create_fertilization_plan', lang)}")
    
    col1, col2 = st.columns(2)  # CorrigÃ©

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

    # Informations culture âœ… Suppression de la duplication et correction de l'indentation
    crop_type = st.selectbox(
        translator.get_text('crop_type', lang),
        ["wheat", "corn", "rice", "soybeans"],
        format_func=lambda x: {
            "wheat": "BlÃ©", "corn": "MaÃ¯s",
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

    # DonnÃ©es sol âœ… Correction de `get_text()`
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

    # Bouton de soumission âœ… Indentation correcte
    submitted = st.form_submit_button(f"ðŸš€ {translator.get_text('generate_plan', lang)}")

if submitted:
    st.success(f"âœ… {translator.get_text('plan_generated', lang)}")

# GÃ©nÃ©ration PDF âœ… Suppression de la syntaxe incorrecte `:` Ã  la fin
if st.button(f"ðŸ“„ {translator.get_text('generate_pdf', lang)}"):
    with st.spinner("GÃ©nÃ©ration du PDF..."):
        try:
            pdf_path = pdf_generator.generate_fertilization_pdf(plan_data, farmer_info)
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label=f"ðŸ’¾ {translator.get_text('download_pdf', lang)}",
                    data=pdf_file.read(),
                    file_name=f"plan_fertilisation_{farmer_info['name'].replace(' ', '_')}.pdf",
                    mime="application/pdf"
                )
            st.success("âœ… PDF gÃ©nÃ©rÃ© avec succÃ¨s!")
        except Exception as e:
            st.error(f"âŒ Erreur gÃ©nÃ©ration PDF: {str(e)}")
else: st.info(f"ðŸ‘† {translator.get_text('create_plan_first', lang)}")

with tab2:
    st.subheader(f"ðŸŒ¾ {translator.get_text('crop_database', lang)}")
    
    crop_db = CropDatabase()
    
    # SÃ©lection de culture pour affichage
    selected_crop = st.selectbox(
        translator.get_text('select_crop_info', lang),
        ["wheat", "corn", "rice", "soybeans"],
        format_func=lambda x: {
            "wheat": "BlÃ©", "corn": "MaÃ¯s", 
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
                    'DurÃ©e (jours)': stage_info['duration_days'],
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
        
        # Besoins totaux et micro-Ã©lÃ©ments
        st.markdown("**ðŸ“Š Besoins Nutritionnels Totaux**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            total_nutrients = crop_info['total_nutrients']
            
            fig_total = px.pie(
                values=list(total_nutrients.values()),
                names=list(total_nutrients.keys()),
                title="RÃ©partition NPK Totale"
            )
            st.plotly_chart(fig_total, use_container_width=True)
        
        with col2:
            st.markdown("**ðŸ§ª Micro-Ã©lÃ©ments RecommandÃ©s**")
            
            micro_elements = crop_info['micro_elements']
            for element, amount in micro_elements.items():
                st.write(f"â€¢ **{element}**: {amount} kg/ha")

with tab3:
    st.subheader(f"ðŸ¤– {translator.get_text('ai_optimization', lang)}")
    
    # EntraÃ®nement du modÃ¨le IA
    st.markdown("**ðŸŽ“ EntraÃ®nement du ModÃ¨le IA**")
    
    if st.button("ðŸš€ EntraÃ®ner le ModÃ¨le avec DonnÃ©es Historiques"):
        # GÃ©nÃ©ration de donnÃ©es d'exemple pour l'entraÃ®nement
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
        
        with st.spinner("EntraÃ®nement en cours..."):
            success = smart_fertilization.train_optimization_model(historical_data)
            
            if success:
                st.success("âœ… ModÃ¨le IA entraÃ®nÃ© avec succÃ¨s!")
                st.info("Le modÃ¨le peut maintenant optimiser automatiquement les plans de fertilisation.")
            else:
                st.error("âŒ Erreur lors de l'entraÃ®nement du modÃ¨le.")
    
    # Simulation d'optimisation
    if smart_fertilization.is_trained:
        st.markdown("**ðŸŽ¯ Simulation d'Optimisation**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("*Conditions de base*")
            base_yield = st.number_input("Rendement prÃ©vu (t/ha)", value=5.0, step=0.1)
            base_n = st.number_input("Azote planifiÃ© (kg/ha)", value=150)
            base_p = st.number_input("Phosphore planifiÃ© (kg/ha)", value=80)
            
        with col2:
            st.markdown("*Conditions optimisÃ©es*")
            # Simulation d'optimisation
            optimized_yield = base_yield * np.random.uniform(1.05, 1.15)
            optimized_n = base_n * np.random.uniform(0.95, 1.05)
            optimized_p = base_p * np.random.uniform(0.95, 1.05)
            
            st.metric("Rendement optimisÃ©", f"{optimized_yield:.1f} t/ha", 
                     f"+{optimized_yield - base_yield:.1f}")
            st.metric("Azote optimisÃ©", f"{optimized_n:.0f} kg/ha", 
                     f"{optimized_n - base_n:+.0f}")
            st.metric("Phosphore optimisÃ©", f"{optimized_p:.0f} kg/ha", 
                     f"{optimized_p - base_p:+.0f}")
        
        # Graphique d'amÃ©lioration
        improvement_data = {
            'MÃ©trique': ['Rendement', 'EfficacitÃ© N', 'EfficacitÃ© P', 'CoÃ»t'],
            'Base': [100, 100, 100, 100],
            'OptimisÃ©': [110, 105, 103, 98]
        }
        
        fig_improvement = px.bar(
            improvement_data,
            x='MÃ©trique',
            y=['Base', 'OptimisÃ©'],
            title="AmÃ©lioration avec IA (%)",
            barmode='group'
        )
        st.plotly_chart(fig_improvement, use_container_width=True)
    
    else:
        st.info("ðŸŽ“ EntraÃ®nez d'abord le modÃ¨le IA pour accÃ©der aux fonctionnalitÃ©s d'optimisation.")

with tab4:
    st.subheader(f"ðŸ’° {translator.get_text('cost_analysis', lang)}")
    
    if st.session_state.fertilization_plans:
        # SÃ©lection du plan Ã  analyser
        plan_options = [f"Plan {p['id']} - {p['farmer_info']['name']}" 
                       for p in st.session_state.fertilization_plans]
        
        selected_plan_idx = st.selectbox(
            "SÃ©lectionner un plan pour analyse",
            range(len(plan_options)),
            format_func=lambda x: plan_options[x]
        )
        
        selected_plan = st.session_state.fertilization_plans[selected_plan_idx]
        cost_data = selected_plan['plan_data']['total_cost_estimate']
        
        # MÃ©triques de coÃ»t
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "CoÃ»t Total",
                f"{cost_data['total_cost_euros']:.2f} â‚¬"
            )
        
        with col2:
            st.metric(
                "CoÃ»t/hectare",
                f"{cost_data['cost_per_hectare']:.2f} â‚¬/ha"
            )
        
        with col3:
            area = selected_plan['farmer_info']['area']
            cost_per_ton = cost_data['total_cost_euros'] / (area * 5.5)  # Estimation 5.5 t/ha
            st.metric(
                "CoÃ»t/tonne",
                f"{cost_per_ton:.2f} â‚¬/t"
            )
        
        with col4:
            # ROI estimÃ©
            revenue_per_ton = 200  # Prix estimÃ©
            estimated_revenue = area * 5.5 * revenue_per_ton
            roi = ((estimated_revenue - cost_data['total_cost_euros']) / cost_data['total_cost_euros']) * 100
            st.metric(
                "ROI EstimÃ©",
                f"{roi:.1f}%"
            )
        
        # Graphiques de coÃ»ts
        col1, col2 = st.columns(2)
        
        with col1:
            # RÃ©partition des coÃ»ts par nutriment
            fig_cost_pie = px.pie(
                values=list(cost_data['cost_breakdown'].values()),
                names=list(cost_data['cost_breakdown'].keys()),
                title="RÃ©partition des CoÃ»ts par Nutriment"
            )
            st.plotly_chart(fig_cost_pie, use_container_width=True)
        
        with col2:
            # Comparaison avec moyennes secteur
            sector_avg = {'N': 120, 'P': 180, 'K': 80}  # Moyennes secteur â‚¬/ha
            current_costs = {k: v/area for k, v in cost_data['cost_breakdown'].items()}
            
            comparison_data = {
                'Nutriment': list(sector_avg.keys()),
                'Secteur (â‚¬/ha)': list(sector_avg.values()),
                'Votre Plan (â‚¬/ha)': [current_costs.get(k, 0) for k in sector_avg.keys()]
            }
            
            fig_comparison = px.bar(
                comparison_data,
                x='Nutriment',
                y=['Secteur (â‚¬/ha)', 'Votre Plan (â‚¬/ha)'],
                title="Comparaison avec Moyennes Secteur",
                barmode='group'
            )
            st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Analyse de sensibilitÃ©
        st.markdown("**ðŸ“ˆ Analyse de SensibilitÃ© des Prix**")
        
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
                "CoÃ»t AjustÃ©",
                f"{adjusted_cost:.2f} â‚¬",
                f"{cost_difference:+.2f} â‚¬"
            )
        
        with col2:
            adjusted_roi = ((estimated_revenue - adjusted_cost) / adjusted_cost) * 100
            roi_difference = adjusted_roi - roi
            st.metric(
                "ROI AjustÃ©",
                f"{adjusted_roi:.1f}%",
                f"{roi_difference:+.1f}%"
            )
    
    else:
        st.info("ðŸ“‹ CrÃ©ez d'abord un plan de fertilisation pour accÃ©der Ã  l'analyse des coÃ»ts.")

with tab5:
    st.subheader(f"ðŸ“¡ {translator.get_text('iot_integration', lang)}")
    
    # Simulation d'intÃ©gration IoT
    st.markdown("**ðŸŒ IntÃ©gration Capteurs IoT**")
    
    # DonnÃ©es capteurs simulÃ©es
    current_conditions = {
        'soil_moisture': np.random.normal(55, 10),
        'soil_temperature': np.random.normal(18, 3),
        'air_temperature': np.random.normal(22, 5),
        'humidity': np.random.normal(65, 15),
        'rainfall_24h': np.random.exponential(2)
    }
    
    # Affichage des conditions actuelles
    st.markdown("**ðŸ“Š Conditions Actuelles des Capteurs**")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        moisture = current_conditions['soil_moisture']
        moisture_status = "ðŸŸ¢" if 40 <= moisture <= 70 else "ðŸŸ¡" if 30 <= moisture < 40 else "ðŸ”´"
        st.metric(
            "HumiditÃ© Sol",
            f"{moisture:.1f}%",
            help="HumiditÃ© du sol mesurÃ©e"
        )
        st.write(f"Statut: {moisture_status}")
    
    with col2:
        soil_temp = current_conditions['soil_temperature']
        st.metric(
            "Temp. Sol",
            f"{soil_temp:.1f}Â°C"
        )
    
    with col3:
        air_temp = current_conditions['air_temperature']
        st.metric(
            "Temp. Air",
            f"{air_temp:.1f}Â°C"
        )
    
    with col4:
        humidity = current_conditions['humidity']
        st.metric(
            "HumiditÃ© Air",
            f"{humidity:.1f}%"
        )
    
    with col5:
        rainfall = current_conditions['rainfall_24h']
        st.metric(
            "Pluie 24h",
            f"{rainfall:.1f}mm"
        )
    
    # Alertes automatiques
    st.markdown("**ðŸš¨ Alertes Automatiques**")
    
    alerts = []
    
    if moisture < 30:
        alerts.append("ðŸ’§ URGENT: HumiditÃ© sol faible - Irrigation recommandÃ©e")
    elif moisture > 80:
        alerts.append("âš ï¸ HumiditÃ© sol Ã©levÃ©e - Risque de lessivage")
    
    if rainfall > 20:
        alerts.append("ðŸŒ§ï¸ Pluies importantes - Reporter application d'engrais")
    
    if air_temp > 30:
        alerts.append("ðŸŒ¡ï¸ TempÃ©ratures Ã©levÃ©es - Stress thermique possible")
    
    if humidity > 85:
        alerts.append("ðŸ„ HumiditÃ© Ã©levÃ©e - Surveillance maladies renforcÃ©e")
    
    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("âœ… Conditions normales - Aucune alerte")
    
    # Recommandations automatiques
    st.markdown("**ðŸ¤– Recommandations Automatiques**")
    
    recommendations = []
    
    if moisture < 40:
        recommendations.append("DÃ©clencher irrigation zone prioritaire")
    
    if rainfall > 15:
        recommendations.append("Reporter fertilisation prÃ©vue de 2-3 jours")
    
    if air_temp > 25 and humidity < 50:
        recommendations.append("Augmenter frÃ©quence irrigation")
    
    if len(recommendations) > 0:
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")
    else:
        st.info("Aucune action particuliÃ¨re requise")
    
    # Graphique tendances temps rÃ©el
    st.markdown("**ðŸ“ˆ Tendances Temps RÃ©el (7 derniers jours)**")
    
    # GÃ©nÃ©ration donnÃ©es historiques simulÃ©es
    dates = [datetime.now() - timedelta(days=i) for i in range(6, -1, -1)]
    moisture_history = [np.random.normal(55, 8) for _ in range(7)]
    temp_history = [np.random.normal(22, 4) for _ in range(7)]
    
    fig_trends = go.Figure()
    
    fig_trends.add_trace(go.Scatter(
        x=dates,
        y=moisture_history,
        mode='lines+markers',
        name='HumiditÃ© Sol (%)',
        yaxis='y',
        line=dict(color='blue')
    ))
    
    fig_trends.add_trace(go.Scatter(
        x=dates,
        y=temp_history,
        mode='lines+markers',
        name='TempÃ©rature (Â°C)',
        yaxis='y2',
        line=dict(color='red')
    ))
    
    fig_trends.update_layout(
        title="Ã‰volution des Conditions",
        xaxis_title="Date",
        yaxis=dict(title="HumiditÃ© (%)", side="left"),
        yaxis2=dict(title="TempÃ©rature (Â°C)", side="right", overlaying="y"),
        height=400
    )
    
    st.plotly_chart(fig_trends, use_container_width=True)

with tab6:
    st.subheader(f"ðŸ“š {translator.get_text('plan_history', lang)}")
    
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
                'CoÃ»t Total': f"{plan_data['total_cost_estimate']['total_cost_euros']:.2f} â‚¬",
                'Date CrÃ©ation': datetime.fromisoformat(plan['created_date']).strftime("%d/%m/%Y"),
                'Stade Actuel': plan_data['crop_info']['current_stage']
            })
        
        plans_df = pd.DataFrame(plans_data)
        st.dataframe(plans_df, use_container_width=True)
        
        # Analyses comparatives
        if len(st.session_state.fertilization_plans) > 1:
            st.markdown("**ðŸ“Š Analyses Comparatives**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # CoÃ»ts par exploitation
                costs = [p['plan_data']['total_cost_estimate']['total_cost_euros'] 
                        for p in st.session_state.fertilization_plans]
                farms = [p['farmer_info']['farm_name'] 
                        for p in st.session_state.fertilization_plans]
                
                fig_costs = px.bar(
                    x=farms,
                    y=costs,
                    title="CoÃ»ts par Exploitation (â‚¬)",
                    labels={'x': 'Exploitation', 'y': 'CoÃ»t (â‚¬)'}
                )
                st.plotly_chart(fig_costs, use_container_width=True)
            
            with col2:
                # QualitÃ© sol moyenne
                soil_qualities = [p['plan_data']['soil_analysis']['soil_quality_score'] 
                                for p in st.session_state.fertilization_plans]
                
                fig_quality = px.histogram(
                    x=soil_qualities,
                    nbins=10,
                    title="Distribution QualitÃ© Sol",
                    labels={'x': 'Score QualitÃ©', 'y': 'Nombre d\'Exploitations'}
                )
                st.plotly_chart(fig_quality, use_container_width=True)
        
        # Export des donnÃ©es
        if st.button("ðŸ“¥ Exporter Historique (JSON)"):
            export_data = {
                'export_date': datetime.now().isoformat(),
                'total_plans': len(st.session_state.fertilization_plans),
                'plans': st.session_state.fertilization_plans
            }
            
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="ðŸ’¾ TÃ©lÃ©charger JSON",
                data=json_str,
                file_name=f"historique_fertilisation_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    else:
        st.info("ðŸ“‹ Aucun plan de fertilisation crÃ©Ã© pour le moment.")
        st.markdown("ðŸ‘† Utilisez l'onglet **CrÃ©er Plan** pour commencer.")

# Footer avec informations
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    ðŸŒ± SystÃ¨me de Fertilisation Intelligente | 
    OptimisÃ© par IA | 
    IntÃ©gration IoT | 
    GÃ©nÃ©ration PDF Automatique
</div>
""", unsafe_allow_html=True)




