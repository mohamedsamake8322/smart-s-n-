
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Climate Forecasting", page_icon="ðŸ“¡", layout="wide")

st.title("ðŸ“¡ PrÃ©vision Climatique AvancÃ©e")
st.markdown("### IA combinÃ©e avec donnÃ©es satellites & IoT pour anticiper les Ã©vÃ©nements climatiques")

# Sidebar controls
st.sidebar.title("Configuration PrÃ©visions")

location = st.sidebar.text_input(
    "Localisation",
    value="Paris, France",
    help="Ville, rÃ©gion ou coordonnÃ©es GPS"
)

forecast_range = st.sidebar.selectbox(
    "Horizon de prÃ©vision",
    ["7 jours", "15 jours", "1 mois", "3 mois", "Saisonnier"]
)

alert_sensitivity = st.sidebar.select_slider(
    "SensibilitÃ© des alertes",
    options=["Faible", "Normale", "Ã‰levÃ©e"],
    value="Normale"
)

# Data sources
data_sources = st.sidebar.multiselect(
    "Sources de donnÃ©es",
    [
        "Satellites mÃ©tÃ©o (GOES, MSG)",
        "Capteurs IoT locaux",
        "ModÃ¨les numÃ©riques (GFS, ECMWF)",
        "Stations mÃ©tÃ©orologiques",
        "Radars prÃ©cipitations",
        "BouÃ©es ocÃ©aniques"
    ],
    default=["Satellites mÃ©tÃ©o (GOES, MSG)", "Capteurs IoT locaux", "ModÃ¨les numÃ©riques (GFS, ECMWF)"]
)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "PrÃ©visions Temps RÃ©el",
    "Alertes Climatiques", 
    "Analyse SaisonniÃ¨re",
    "Impact Agricole",
    "ModÃ¨les PrÃ©dictifs"
])

with tab1:
    st.subheader("PrÃ©visions MÃ©tÃ©orologiques en Temps RÃ©el")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # GÃ©nÃ©ration de donnÃ©es de prÃ©vision simulÃ©es
        days = 15 if "15 jours" in forecast_range else 7
        dates = [datetime.now() + timedelta(days=i) for i in range(days)]
        
        # DonnÃ©es simulÃ©es
        temperatures = np.random.normal(22, 8, days)
        humidity = np.random.normal(65, 15, days)
        precipitation = np.random.exponential(2, days)
        wind_speed = np.random.gamma(2, 3, days)
        pressure = np.random.normal(1015, 10, days)
        
        # CrÃ©ation du graphique multi-variables
        fig = go.Figure()
        
        # TempÃ©rature
        fig.add_trace(go.Scatter(
            x=dates,
            y=temperatures,
            mode='lines+markers',
            name='TempÃ©rature (Â°C)',
            line=dict(color='red', width=3),
            yaxis='y'
        ))
        
        # PrÃ©cipitations (barres)
        fig.add_trace(go.Bar(
            x=dates,
            y=precipitation,
            name='PrÃ©cipitations (mm)',
            marker_color='blue',
            opacity=0.6,
            yaxis='y2'
        ))
        
        # HumiditÃ©
        fig.add_trace(go.Scatter(
            x=dates,
            y=humidity,
            mode='lines',
            name='HumiditÃ© (%)',
            line=dict(color='green', dash='dash'),
            yaxis='y3'
        ))
        
        fig.update_layout(
            title="PrÃ©visions MÃ©tÃ©orologiques Multi-Variables",
            xaxis_title="Date",
            yaxis=dict(title="TempÃ©rature (Â°C)", side="left", color="red"),
            yaxis2=dict(title="PrÃ©cipitations (mm)", side="right", overlaying="y", color="blue"),
            yaxis3=dict(title="HumiditÃ© (%)", side="right", overlaying="y", position=0.9, color="green"),
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

# Carte mÃ©tÃ©orologique
        st.markdown("**Carte MÃ©tÃ©orologique RÃ©gionale**")

# Simulation d'une carte de tempÃ©ratures
        lat = np.random.uniform(45, 50, 100)
        lon = np.random.uniform(1, 6, 100)
        temp_map = np.random.normal(20, 5, 100)

        fig_map = px.scatter_map(
            lat=lat,
            lon=lon,
            color=temp_map,
            size=abs(temp_map - 20) + 5,
            hover_name=[f"Station {i}" for i in range(100)],
            hover_data={"TempÃ©rature": temp_map},
            color_continuous_scale="Viridis",
            size_max=15,
            zoom=6,
            height=400,
            title="TempÃ©rature RÃ©gionale en Temps RÃ©el"
        )

        fig_map.update_layout(map_style="open-street-map")
        st.plotly_chart(fig_map, use_container_width=True)

    
    with col2:
        st.markdown("**Conditions Actuelles**")
        
        # MÃ©tÃ©o actuelle simulÃ©e
        current_temp = np.random.normal(22, 5)
        current_humidity = np.random.uniform(40, 80)
        current_wind = np.random.uniform(5, 25)
        current_pressure = np.random.normal(1015, 8)
        
        # MÃ©triques mÃ©tÃ©o
        st.metric("ðŸŒ¡ï¸ TempÃ©rature", f"{current_temp:.1f}Â°C", delta="2.3Â°C")
        st.metric("ðŸ’§ HumiditÃ©", f"{current_humidity:.0f}%", delta="5%")
        st.metric("ðŸ’¨ Vent", f"{current_wind:.1f} km/h", delta="-3.2 km/h")
        st.metric("ðŸ§­ Pression", f"{current_pressure:.0f} hPa", delta="2 hPa")
        
        st.markdown("**ðŸŽ¯ Indices Agricoles**")
        
        # Calcul d'indices agricoles
        gdd = max(0, current_temp - 10)  # Growing Degree Days
        et_rate = max(0, (current_temp - 5) * (1 - current_humidity/100) * 0.1)
        
        st.metric("ðŸŒ± GDD (Base 10Â°C)", f"{gdd:.1f}")
        st.metric("ðŸ’¦ Ã‰vapotranspiration", f"{et_rate:.2f} mm/jour")
        
        # QualitÃ© de l'air simulÃ©e
        air_quality_index = np.random.randint(25, 150)
        air_quality_status = "Bon" if air_quality_index < 50 else "ModÃ©rÃ©" if air_quality_index < 100 else "Mauvais"
        
        st.metric("ðŸŒ¬ï¸ QualitÃ© de l'Air", air_quality_status, f"AQI: {air_quality_index}")
        
        st.markdown("**ðŸ“Š Tendance 24h**")
        
        # Mini graphique de tendance
        hours = list(range(24))
        hourly_temp = current_temp + np.sin(np.array(hours) * np.pi / 12) * 5 + np.random.normal(0, 1, 24)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=hours,
            y=hourly_temp,
            mode='lines',
            name='TempÃ©rature 24h',
            line=dict(color='orange', width=2)
        ))
        
        fig_trend.update_layout(
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
            xaxis_title="Heure",
            yaxis_title="Â°C"
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)

with tab2:
    st.subheader("SystÃ¨me d'Alertes Climatiques Intelligentes")
    
    # Configuration des alertes
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Configuration des Alertes**")
        
        alert_types = st.multiselect(
            "Types d'alertes Ã  surveiller",
            [
                "ðŸŒ¡ï¸ TempÃ©ratures extrÃªmes",
                "ðŸŒ§ï¸ PrÃ©cipitations intenses",
                "â„ï¸ Risque de gel",
                "ðŸŒªï¸ Vents violents",
                "â›ˆï¸ Orages sÃ©vÃ¨res",
                "ðŸŒµ SÃ©cheresse",
                "ðŸŒŠ Inondations",
                "ðŸŒ«ï¸ Brouillard dense"
            ],
            default=["ðŸŒ¡ï¸ TempÃ©ratures extrÃªmes", "â„ï¸ Risque de gel", "ðŸŒ§ï¸ PrÃ©cipitations intenses"]
        )
        
        notification_methods = st.multiselect(
            "MÃ©thodes de notification",
            ["ðŸ“§ Email", "ðŸ“± SMS", "ðŸ”” Push", "ðŸ“º Dashboard", "ðŸ“¡ IoT Actuators"],
            default=["ðŸ“§ Email", "ðŸ“º Dashboard"]
        )
        
        advance_warning = st.selectbox(
            "PrÃ©avis souhaitÃ©",
            ["1 heure", "3 heures", "6 heures", "12 heures", "24 heures", "48 heures"],
            index=4
        )
    
    with col2:
        st.markdown("**Alertes Actives**")
        
        # Simulation d'alertes
        active_alerts = [
            {
                "type": "â„ï¸ Alerte Gel",
                "severity": "ðŸŸ¡ ModÃ©rÃ©",
                "time": "Dans 18h",
                "temp": "-2Â°C attendu",
                "action": "ProtÃ©ger cultures sensibles"
            },
            {
                "type": "ðŸŒ§ï¸ Pluies Intenses",
                "severity": "ðŸŸ  Ã‰levÃ©", 
                "time": "Dans 6h",
                "amount": "25mm en 2h",
                "action": "VÃ©rifier drainage"
            },
            {
                "type": "ðŸ’¨ Vents Forts",
                "severity": "ðŸŸ¡ ModÃ©rÃ©",
                "time": "Dans 12h",
                "speed": "45 km/h rafales",
                "action": "SÃ©curiser Ã©quipements"
            }
        ]
        
        for alert in active_alerts:
            with st.container():
                st.markdown(f"**{alert['type']}** {alert['severity']}")
                st.write(f"â° {alert['time']}")
                st.write(f"ðŸ“Š {alert.get('temp', alert.get('amount', alert.get('speed', 'N/A')))}")
                st.write(f"ðŸŽ¯ Action: {alert['action']}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("âœ… Acquitter", key=f"ack_{alert['type']}"):
                        st.success("Alerte acquittÃ©e")
                with col_btn2:
                    if st.button("ðŸ”• DÃ©sactiver", key=f"disable_{alert['type']}"):
                        st.info("Alerte dÃ©sactivÃ©e")
                
                st.markdown("---")
    
    # Historique des alertes
    st.markdown("**ðŸ“ˆ Historique des Alertes (30 derniers jours)**")
    
    # GÃ©nÃ©ration de donnÃ©es d'historique
    alert_dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    alert_counts = np.random.poisson(1.5, 30)
    alert_severities = np.random.choice(['Faible', 'ModÃ©rÃ©', 'Ã‰levÃ©', 'Critique'], 30, p=[0.4, 0.3, 0.2, 0.1])
    
    alert_df = pd.DataFrame({
        'Date': alert_dates,
        'Nombre_Alertes': alert_counts,
        'SÃ©vÃ©ritÃ©_Max': alert_severities
    })
    
    fig_alerts = px.bar(
        alert_df,
        x='Date',
        y='Nombre_Alertes',
        color='SÃ©vÃ©ritÃ©_Max',
        title="Ã‰volution des Alertes MÃ©tÃ©orologiques",
        color_discrete_map={
            'Faible': 'green',
            'ModÃ©rÃ©': 'yellow', 
            'Ã‰levÃ©': 'orange',
            'Critique': 'red'
        }
    )
    
    fig_alerts.update_layout(height=300)
    st.plotly_chart(fig_alerts, use_container_width=True)

with tab3:
    st.subheader("Analyse Climatique SaisonniÃ¨re")
    
    # SÃ©lection de la pÃ©riode d'analyse
    col1, col2 = st.columns(2)
    
    with col1:
        analysis_year = st.selectbox(
            "AnnÃ©e d'analyse",
            [2024, 2023, 2022, 2021, 2020],
            index=0
        )
    
    with col2:
        comparison_year = st.selectbox(
            "AnnÃ©e de comparaison",
            [2023, 2022, 2021, 2020, 2019],
            index=0
        )
    
    # DonnÃ©es saisonniÃ¨res simulÃ©es
    months = ['Jan', 'FÃ©v', 'Mar', 'Avr', 'Mai', 'Jun', 
              'Jul', 'AoÃ»', 'Sep', 'Oct', 'Nov', 'DÃ©c']
    
    # TempÃ©rature mensuelle
    temp_2024 = [2, 4, 9, 14, 18, 22, 25, 24, 20, 15, 8, 3]
    temp_2023 = [1, 3, 8, 13, 17, 21, 24, 23, 19, 14, 7, 2]
    
    # PrÃ©cipitations mensuelles  
    precip_2024 = [45, 38, 52, 67, 73, 45, 32, 48, 61, 78, 69, 54]
    precip_2023 = [52, 41, 48, 62, 68, 38, 28, 52, 58, 82, 74, 61]
    
    # Graphiques de comparaison
    fig_seasonal = go.Figure()
    
    # TempÃ©ratures
    fig_seasonal.add_trace(go.Scatter(
        x=months,
        y=temp_2024,
        mode='lines+markers',
        name=f'TempÃ©rature {analysis_year}',
        line=dict(color='red', width=3),
        yaxis='y'
    ))
    
    fig_seasonal.add_trace(go.Scatter(
        x=months,
        y=temp_2023,
        mode='lines+markers',
        name=f'TempÃ©rature {comparison_year}',
        line=dict(color='orange', width=2, dash='dash'),
        yaxis='y'
    ))
    
    # PrÃ©cipitations
    fig_seasonal.add_trace(go.Bar(
        x=months,
        y=precip_2024,
        name=f'PrÃ©cipitations {analysis_year}',
        marker_color='blue',
        opacity=0.7,
        yaxis='y2'
    ))
    
    fig_seasonal.add_trace(go.Bar(
        x=months,
        y=precip_2023,
        name=f'PrÃ©cipitations {comparison_year}',
        marker_color='lightblue',
        opacity=0.5,
        yaxis='y2'
    ))
    
    fig_seasonal.update_layout(
        title="Comparaison Climatique SaisonniÃ¨re",
        xaxis_title="Mois",
        yaxis=dict(title="TempÃ©rature (Â°C)", side="left"),
        yaxis2=dict(title="PrÃ©cipitations (mm)", side="right", overlaying="y"),
        height=400
    )
    
    st.plotly_chart(fig_seasonal, use_container_width=True)
    
    # Analyse des anomalies
    st.markdown("**ðŸ” DÃ©tection d'Anomalies Climatiques**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        temp_anomaly = np.mean(temp_2024) - np.mean(temp_2023)
        st.metric(
            "Anomalie TempÃ©rature",
            f"{temp_anomaly:+.1f}Â°C",
            delta=f"vs {comparison_year}"
        )
    
    with col2:
        precip_anomaly = (np.sum(precip_2024) - np.sum(precip_2023)) / np.sum(precip_2023) * 100
        st.metric(
            "Anomalie PrÃ©cipitations", 
            f"{precip_anomaly:+.1f}%",
            delta=f"vs {comparison_year}"
        )
    
    with col3:
        extreme_days = np.random.randint(12, 28)
        st.metric(
            "Jours ExtrÃªmes",
            extreme_days,
            delta=f"+{extreme_days-20} vs normale"
        )
    
    # Projections climatiques
    st.markdown("**ðŸ”® Projections Climatiques (IA)**")
    
    # GÃ©nÃ©ration de projections
    projection_months = ['Jan 2025', 'FÃ©v 2025', 'Mar 2025', 'Avr 2025', 'Mai 2025', 'Jun 2025']
    projected_temp = [3, 5, 10, 15, 19, 23]
    confidence_bands = [1.5, 1.8, 2.1, 2.3, 2.0, 1.7]
    
    fig_projection = go.Figure()
    
    # Projection centrale
    fig_projection.add_trace(go.Scatter(
        x=projection_months,
        y=projected_temp,
        mode='lines+markers',
        name='Projection IA',
        line=dict(color='purple', width=3)
    ))
    
    # Bandes de confiance
    fig_projection.add_trace(go.Scatter(
        x=projection_months + projection_months[::-1],
        y=[t + c for t, c in zip(projected_temp, confidence_bands)] + 
          [t - c for t, c in zip(projected_temp[::-1], confidence_bands[::-1])],
        fill='toself',
        fillcolor='rgba(128,0,128,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Intervalle confiance 90%'
    ))
    
    fig_projection.update_layout(
        title="Projections TempÃ©rature - 6 Prochains Mois",
        xaxis_title="PÃ©riode",
        yaxis_title="TempÃ©rature (Â°C)",
        height=300
    )
    
    st.plotly_chart(fig_projection, use_container_width=True)

with tab4:
    st.subheader("Ã‰valuation d'Impact Agricole")
    
    # SÃ©lection du type de culture
    crop_selection = st.selectbox(
        "Type de culture Ã  analyser",
        ["BlÃ©", "MaÃ¯s", "Tournesol", "Betterave", "Colza", "Orge", "Tomate", "Pomme de terre"]
    )
    
    growth_stage = st.selectbox(
        "Stade de croissance",
        ["Semis/Plantation", "LevÃ©e", "DÃ©veloppement vÃ©gÃ©tatif", "Floraison", "Formation grains/fruits", "Maturation"]
    )
    
    # Matrice d'impact climatique
    st.markdown("**ðŸ“Š Matrice d'Impact Climatique**")
    
    # DonnÃ©es d'impact simulÃ©es
    climate_factors = ['TempÃ©rature', 'PrÃ©cipitations', 'HumiditÃ©', 'Vent', 'Radiation solaire']
    impact_levels = ['TrÃ¨s Favorable', 'Favorable', 'Neutre', 'DÃ©favorable', 'TrÃ¨s DÃ©favorable']
    
    # Matrice d'impact pour le crop sÃ©lectionnÃ©
    impact_matrix = np.random.choice([0, 1, 2, 3, 4], size=(len(climate_factors), len(impact_levels)), 
                                   p=[0.1, 0.3, 0.3, 0.2, 0.1])
    
    # CrÃ©ation d'un heatmap
    fig_impact = px.imshow(
        impact_matrix,
        x=impact_levels,
        y=climate_factors,
        color_continuous_scale='RdYlGn_r',
        title=f"Impact Climatique sur {crop_selection} - {growth_stage}",
        aspect='auto'
    )
    
    fig_impact.update_layout(height=300)
    st.plotly_chart(fig_impact, use_container_width=True)
    
    # PrÃ©dictions de rendement basÃ©es sur le climat
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**ðŸ“ˆ PrÃ©dictions de Rendement Climatique**")
        
        # GÃ©nÃ©ration de scÃ©narios climatiques
        scenarios = ['Optimiste', 'Probable', 'Pessimiste']
        base_yield = {'BlÃ©': 7.2, 'MaÃ¯s': 9.8, 'Tournesol': 2.8}.get(crop_selection, 5.0)
        
        scenario_yields = [
            base_yield * 1.15,  # Optimiste
            base_yield * 1.0,   # Probable
            base_yield * 0.85   # Pessimiste
        ]
        
        fig_yield_scenarios = go.Figure()
        
        fig_yield_scenarios.add_trace(go.Bar(
            x=scenarios,
            y=scenario_yields,
            marker_color=['green', 'blue', 'red'],
            text=[f"{y:.1f} t/ha" for y in scenario_yields],
            textposition='auto'
        ))
        
        fig_yield_scenarios.update_layout(
            title=f"ScÃ©narios de Rendement - {crop_selection}",
            yaxis_title="Rendement (tonnes/ha)",
            height=300
        )
        
        st.plotly_chart(fig_yield_scenarios, use_container_width=True)
    
    with col2:
        st.markdown("**ðŸŽ¯ Recommandations Adaptatives**")
        
        # Recommandations basÃ©es sur les prÃ©visions
        recommendations = {
            'BlÃ©': [
                "ðŸ’§ Surveillance hydrique renforcÃ©e",
                "ðŸŒ¡ï¸ Protection contre gel tardif",
                "ðŸ„ PrÃ©vention maladies fongiques",
                "â° Ajuster dates de semis"
            ],
            'MaÃ¯s': [
                "ðŸŒ± Retarder semis si sol froid",
                "ðŸ’¦ Irrigation prÃ©coce si sec",
                "ðŸŒªï¸ Protection contre verse",
                "ðŸ¦— Surveillance ravageurs"
            ]
        }
        
        crop_recommendations = recommendations.get(crop_selection, [
            "ðŸ“Š Monitoring continu requis",
            "ðŸ”„ Adapter pratiques culturales",
            "âš ï¸ Alertes mÃ©tÃ©o activÃ©es",
            "ðŸ“ˆ Suivi rendement hebdomadaire"
        ])
        
        for rec in crop_recommendations:
            st.write(rec)
        
        # ProbabilitÃ© de stress
        stress_probability = np.random.uniform(15, 45)
        stress_color = "green" if stress_probability < 25 else "orange" if stress_probability < 35 else "red"
        
        st.metric(
            "Risque de Stress",
            f"{stress_probability:.0f}%",
            delta=f"{stress_probability-30:.0f}% vs normale"
        )
        
        # FenÃªtre d'action optimale
        optimal_window = np.random.randint(3, 14)
        st.metric(
            "FenÃªtre d'action",
            f"{optimal_window} jours",
            help="PÃ©riode optimale pour interventions"
        )

with tab5:
    st.subheader("ModÃ¨les PrÃ©dictifs et Validation")
    
    # SÃ©lection du modÃ¨le
    col1, col2 = st.columns(2)
    
    with col1:
        model_type = st.selectbox(
            "Type de modÃ¨le climatique",
            [
                "Ensemble Neural Network",
                "Random Forest Climatique", 
                "LSTM SÃ©ries Temporelles",
                "ModÃ¨le Hybride Satellite-IoT",
                "Transformers MÃ©tÃ©o"
            ]
        )
        
        model_resolution = st.selectbox(
            "RÃ©solution spatiale",
            ["1km x 1km", "5km x 5km", "10km x 10km", "25km x 25km"]
        )
    
    with col2:
        temporal_resolution = st.selectbox(
            "RÃ©solution temporelle",
            ["Horaire", "3 heures", "6 heures", "Quotidien"]
        )
        
        prediction_horizon = st.selectbox(
            "Horizon de prÃ©diction",
            ["24h", "72h", "7 jours", "15 jours", "1 mois"]
        )
    
    # Performance des modÃ¨les
    st.markdown("**ðŸ“Š Performance des ModÃ¨les**")
    
    # MÃ©triques de performance simulÃ©es
    model_performance = {
        'Ensemble Neural Network': {'PrÃ©cision': 94.2, 'Recall': 91.8, 'F1-Score': 93.0, 'RMSE': 1.12},
        'Random Forest Climatique': {'PrÃ©cision': 89.7, 'Recall': 87.3, 'F1-Score': 88.5, 'RMSE': 1.34},
        'LSTM SÃ©ries Temporelles': {'PrÃ©cision': 91.5, 'Recall': 89.2, 'F1-Score': 90.3, 'RMSE': 1.21},
        'ModÃ¨le Hybride Satellite-IoT': {'PrÃ©cision': 96.1, 'Recall': 94.5, 'F1-Score': 95.3, 'RMSE': 0.98},
        'Transformers MÃ©tÃ©o': {'PrÃ©cision': 93.8, 'Recall': 92.1, 'F1-Score': 92.9, 'RMSE': 1.15}
    }
    
    # Affichage des mÃ©triques pour le modÃ¨le sÃ©lectionnÃ©
    current_metrics = model_performance[model_type]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("PrÃ©cision", f"{current_metrics['PrÃ©cision']:.1f}%")
    with col2:
        st.metric("Recall", f"{current_metrics['Recall']:.1f}%")
    with col3:
        st.metric("F1-Score", f"{current_metrics['F1-Score']:.1f}%")
    with col4:
        st.metric("RMSE", f"{current_metrics['RMSE']:.2f}Â°C")
    
    # Graphique de comparaison des modÃ¨les
    models = list(model_performance.keys())
    precisions = [model_performance[m]['PrÃ©cision'] for m in models]
    rmse_values = [model_performance[m]['RMSE'] for m in models]
    
    fig_models = go.Figure()
    
    fig_models.add_trace(go.Bar(
        name='PrÃ©cision (%)',
        x=models,
        y=precisions,
        yaxis='y',
        offsetgroup=1
    ))
    
    fig_models.add_trace(go.Scatter(
        name='RMSE (Â°C)',
        x=models,
        y=rmse_values,
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='red', width=3)
    ))
    
    fig_models.update_layout(
        title="Comparaison Performance ModÃ¨les Climatiques",
        yaxis=dict(title="PrÃ©cision (%)", side="left"),
        yaxis2=dict(title="RMSE (Â°C)", side="right", overlaying="y"),
        height=400,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig_models, use_container_width=True)
    
    # Validation croisÃ©e et tests
    st.markdown("**ðŸ”¬ Validation et Tests du ModÃ¨le**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Tests de Robustesse**")
        
        test_results = {
            "âœ… Test donnÃ©es manquantes": "95.2% prÃ©cision",
            "âœ… Test conditions extrÃªmes": "87.8% prÃ©cision", 
            "âœ… Test gÃ©nÃ©ralisation spatiale": "91.4% prÃ©cision",
            "âš ï¸ Test changement climatique": "83.1% prÃ©cision",
            "âœ… Test temps rÃ©el": "96.7% prÃ©cision"
        }
        
        for test, result in test_results.items():
            st.write(f"{test}: {result}")
    
    with col2:
        st.markdown("**Mise Ã  Jour du ModÃ¨le**")
        
        last_update = datetime.now() - timedelta(days=2)
        st.write(f"DerniÃ¨re mise Ã  jour: {last_update.strftime('%d/%m/%Y %H:%M')}")
        
        data_sources_count = len(data_sources)
        st.write(f"Sources de donnÃ©es actives: {data_sources_count}")
        
        st.write(f"Ã‰chantillons d'entraÃ®nement: 2.3M")
        st.write(f"FrÃ©quence re-entraÃ®nement: Hebdomadaire")
        
        if st.button("ðŸ”„ DÃ©clencher Re-entraÃ®nement"):
            with st.spinner("Re-entraÃ®nement en cours..."):
                import time
                time.sleep(3)
                st.success("âœ… ModÃ¨le mis Ã  jour avec succÃ¨s!")

# Sidebar status
st.sidebar.markdown("---")
st.sidebar.markdown("**Ã‰tat du SystÃ¨me**")

st.sidebar.metric("Sources actives", len(data_sources))
st.sidebar.metric("PrÃ©dictions/jour", "1,247")
st.sidebar.metric("PrÃ©cision moyenne", "94.1%")
st.sidebar.metric("Latence", "< 50ms")

# Footer
st.markdown("---")
st.markdown("**ðŸ“¡ Module PrÃ©vision Climatique** - IA avancÃ©e pour anticipation mÃ©tÃ©orologique et alertes agricoles")

