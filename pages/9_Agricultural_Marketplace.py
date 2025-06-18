﻿
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Agricultural Marketplace", page_icon="ðŸ›’", layout="wide")

st.title("ðŸ›’ Marketplace Agricole IntÃ©grÃ©e")
st.markdown("### Plateforme d'achat/vente d'intrants et prÃ©visions de rentabilitÃ©")

# Sidebar controls
st.sidebar.title("Navigation Marketplace")

user_type = st.sidebar.selectbox(
    "Type d'utilisateur",
    ["ðŸŒ¾ Acheteur (Agriculteur)", "ðŸ­ Vendeur (Fournisseur)", "ðŸ“Š Analyste MarchÃ©"]
)

region = st.sidebar.selectbox(
    "RÃ©gion",
    ["ÃŽle-de-France", "Nouvelle-Aquitaine", "Occitanie", "Grand Est", "Hauts-de-France", "Toutes rÃ©gions"]
)

currency = st.sidebar.selectbox(
    "Devise",
    ["EUR (â‚¬)", "USD ($)", "GBP (Â£)"]
)

# Main content tabs
if user_type == "ðŸŒ¾ Acheteur (Agriculteur)":
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Catalogue Intrants",
        "Comparateur Prix",
        "Mes Commandes",
        "PrÃ©visions CoÃ»ts",
        "Recommandations IA"
    ])
    
    with tab1:
        st.subheader("Catalogue des Intrants Agricoles")
        
        # Filtres de recherche
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox(
                "CatÃ©gorie",
                ["Toutes", "Semences", "Engrais", "Pesticides", "MatÃ©riel", "Ã‰quipements"]
            )
        
        with col2:
            crop_type = st.selectbox(
                "Type de culture",
                ["Toutes", "CÃ©rÃ©ales", "LÃ©gumineuses", "OlÃ©agineux", "MaraÃ®chage", "Arboriculture"]
            )
        
        with col3:
            price_range = st.selectbox(
                "Gamme de prix",
                ["Toutes", "< 50â‚¬", "50-200â‚¬", "200-500â‚¬", "500-1000â‚¬", "> 1000â‚¬"]
            )
        
        # GÃ©nÃ©ration de donnÃ©es produits simulÃ©es
        products_data = []
        categories = ["Semences", "Engrais", "Pesticides", "MatÃ©riel"]
        
        for i in range(20):
            product = {
                "id": f"PROD_{i+1:03d}",
                "nom": f"Produit {i+1}",
                "categorie": np.random.choice(categories),
                "prix": np.random.uniform(25, 800),
                "unite": np.random.choice(["kg", "L", "unitÃ©", "sac"]),
                "stock": np.random.randint(0, 500),
                "fournisseur": f"Fournisseur {np.random.randint(1, 10)}",
                "rating": np.random.uniform(3.5, 5.0),
                "livraison": np.random.randint(1, 7),
                "bio": np.random.choice([True, False], p=[0.3, 0.7]),
                "promotion": np.random.choice([True, False], p=[0.2, 0.8])
            }
            products_data.append(product)
        
        products_df = pd.DataFrame(products_data)
        
        # Affichage des produits
        for i, product in products_df.iterrows():
            with st.container():
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    promotion_tag = "ðŸ·ï¸ PROMO" if product['promotion'] else ""
                    bio_tag = "ðŸŒ± BIO" if product['bio'] else ""
                    st.markdown(f"**{product['nom']}** {promotion_tag} {bio_tag}")
                    st.write(f"CatÃ©gorie: {product['categorie']}")
                    st.write(f"Fournisseur: {product['fournisseur']}")
                    st.write(f"â­ {product['rating']:.1f}/5")
                
                with col2:
                    if product['promotion']:
                        original_price = product['prix'] * 1.2
                        st.markdown(f"~~{original_price:.2f}â‚¬~~ **{product['prix']:.2f}â‚¬**/{product['unite']}")
                    else:
                        st.markdown(f"**{product['prix']:.2f}â‚¬**/{product['unite']}")
                    
                    stock_color = "green" if product['stock'] > 100 else "orange" if product['stock'] > 0 else "red"
                    st.markdown(f"Stock: :{stock_color}[{product['stock']}]")
                
                with col3:
                    st.write(f"ðŸšš {product['livraison']} jours")
                    
                    quantity = st.number_input(
                        "QuantitÃ©",
                        min_value=1,
                        max_value=min(100, product['stock']),
                        value=1,
                        key=f"qty_{product['id']}"
                    )
                
                with col4:
                    if st.button("ðŸ›’ Ajouter", key=f"add_{product['id']}"):
                        if 'cart' not in st.session_state:
                            st.session_state.cart = []
                        
                        st.session_state.cart.append({
                            'product': product['nom'],
                            'price': product['prix'],
                            'quantity': quantity,
                            'total': product['prix'] * quantity
                        })
                        st.success(f"AjoutÃ© au panier!")
                    
                    if st.button("ðŸ‘ï¸ DÃ©tails", key=f"details_{product['id']}"):
                        st.info(f"DÃ©tails de {product['nom']}")
                
                st.markdown("---")
    
    with tab2:
        st.subheader("Comparateur de Prix en Temps RÃ©el")
        
        # SÃ©lection du produit Ã  comparer
        product_to_compare = st.selectbox(
            "Produit Ã  comparer",
            ["Engrais NPK 15-15-15", "Semences BlÃ© Tendre", "Pesticide Glyphosate", "Fuel Agricole"]
        )
        
        # DonnÃ©es de comparaison simulÃ©es
        suppliers_data = []
        for i in range(8):
            supplier = {
                "fournisseur": f"Fournisseur {chr(65+i)}",
                "prix": np.random.uniform(45, 85),
                "livraison": np.random.randint(1, 10),
                "frais_port": np.random.uniform(5, 25),
                "rating": np.random.uniform(3.0, 5.0),
                "stock": np.random.randint(50, 500),
                "certification": np.random.choice(["Bio", "Standard", "Premium"])
            }
            supplier["prix_total"] = supplier["prix"] + supplier["frais_port"]
            suppliers_data.append(supplier)
        
        suppliers_df = pd.DataFrame(suppliers_data).sort_values('prix_total')
        
        # Graphique de comparaison
        fig_comparison = px.bar(
            suppliers_df,
            x='fournisseur',
            y=['prix', 'frais_port'],
            title=f"Comparaison Prix - {product_to_compare}",
            labels={'value': 'Prix (â‚¬)', 'variable': 'Composante'},
            color_discrete_map={'prix': 'lightblue', 'frais_port': 'orange'}
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Tableau de comparaison dÃ©taillÃ©
        st.markdown("**Comparaison DÃ©taillÃ©e**")
        
        for i, supplier in suppliers_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                certification_icon = {"Bio": "ðŸŒ±", "Standard": "ðŸ“¦", "Premium": "â­"}.get(supplier['certification'], "")
                st.write(f"**{supplier['fournisseur']}** {certification_icon}")
                st.write(f"â­ {supplier['rating']:.1f}/5")
            
            with col2:
                st.metric("Prix Unitaire", f"{supplier['prix']:.2f}â‚¬")
            
            with col3:
                st.metric("Livraison", f"{supplier['livraison']} jours")
                st.write(f"Port: {supplier['frais_port']:.2f}â‚¬")
            
            with col4:
                st.metric("Total", f"{supplier['prix_total']:.2f}â‚¬")
                
                if i == 0:
                    st.success("ðŸ† Meilleur prix")
            
            with col5:
                if st.button("SÃ©lectionner", key=f"select_{i}"):
                    st.success(f"SÃ©lectionnÃ©: {supplier['fournisseur']}")
        
        # Ã‰volution des prix
        st.markdown("**ðŸ“ˆ Ã‰volution des Prix (30 jours)**")
        
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_price = 65
        price_evolution = base_price + np.cumsum(np.random.normal(0, 2, 30))
        
        fig_price_evolution = px.line(
            x=dates,
            y=price_evolution,
            title=f"Ã‰volution Prix - {product_to_compare}",
            labels={'x': 'Date', 'y': 'Prix (â‚¬)'}
        )
        
        fig_price_evolution.add_hline(
            y=np.mean(price_evolution),
            line_dash="dash",
            line_color="red",
            annotation_text="Prix moyen"
        )
        
        st.plotly_chart(fig_price_evolution, use_container_width=True)
    
    with tab3:
        st.subheader("Mes Commandes et Historique")
        
        # Statut des commandes
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Commandes en cours", "3", delta="1")
        with col2:
            st.metric("Total ce mois", "2,458â‚¬", delta="15.2%")
        with col3:
            st.metric("Ã‰conomies rÃ©alisÃ©es", "347â‚¬", delta="12.8%")
        
        # Commandes rÃ©centes
        st.markdown("**Commandes RÃ©centes**")
        
        orders_data = [
            {
                "id": "CMD_001",
                "date": "2024-06-10",
                "produits": "Engrais NPK, Semences BlÃ©",
                "montant": 456.78,
                "statut": "En livraison",
                "livraison_prevue": "2024-06-14"
            },
            {
                "id": "CMD_002", 
                "date": "2024-06-08",
                "produits": "Pesticide Bio, MatÃ©riel",
                "montant": 234.50,
                "statut": "LivrÃ©",
                "livraison_prevue": "2024-06-12"
            },
            {
                "id": "CMD_003",
                "date": "2024-06-05",
                "produits": "Fuel Agricole",
                "montant": 189.32,
                "statut": "En prÃ©paration",
                "livraison_prevue": "2024-06-15"
            }
        ]
        
        for order in orders_data:
            with st.container():
                col1, col2, col3, col4 = st.columns([1, 2, 1, 1])
                
                with col1:
                    st.write(f"**{order['id']}**")
                    st.write(order['date'])
                
                with col2:
                    st.write(order['produits'])
                
                with col3:
                    st.write(f"**{order['montant']:.2f}â‚¬**")
                    
                    status_color = {
                        "LivrÃ©": "green",
                        "En livraison": "orange", 
                        "En prÃ©paration": "blue"
                    }.get(order['statut'], "gray")
                    
                    st.markdown(f":{status_color}[{order['statut']}]")
                
                with col4:
                    st.write(f"ðŸ“… {order['livraison_prevue']}")
                    
                    if order['statut'] != "LivrÃ©":
                        if st.button("ðŸ“ Suivre", key=f"track_{order['id']}"):
                            st.info("Suivi de commande activÃ©")
                
                st.markdown("---")
        
        # Panier actuel
        if 'cart' in st.session_state and st.session_state.cart:
            st.markdown("**ðŸ›’ Panier Actuel**")
            
            total_cart = sum(item['total'] for item in st.session_state.cart)
            
            for item in st.session_state.cart:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"{item['product']} x{item['quantity']}")
                with col2:
                    st.write(f"{item['price']:.2f}â‚¬ / unitÃ©")
                with col3:
                    st.write(f"**{item['total']:.2f}â‚¬**")
            
            st.markdown(f"**Total: {total_cart:.2f}â‚¬**")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("ðŸ—‘ï¸ Vider Panier"):
                    st.session_state.cart = []
                    st.rerun()
            
            with col2:
                if st.button("âœ… Confirmer Commande"):
                    st.success("Commande confirmÃ©e!")
                    st.session_state.cart = []
    
    with tab4:
        st.subheader("PrÃ©visions de CoÃ»ts et RentabilitÃ©")
        
        # Configuration de la simulation
        col1, col2 = st.columns(2)
        
        with col1:
            simulation_crop = st.selectbox(
                "Culture Ã  analyser",
                ["BlÃ© Tendre", "MaÃ¯s Grain", "Colza", "Tournesol", "Orge"]
            )
            
            surface_hectares = st.number_input(
                "Surface (hectares)",
                min_value=1,
                max_value=1000,
                value=50
            )
            
            yield_target = st.number_input(
                "Rendement objectif (t/ha)",
                min_value=1.0,
                max_value=15.0,
                value=7.2,
                step=0.1
            )
        
        with col2:
            market_price = st.number_input(
                "Prix de vente prÃ©vu (â‚¬/t)",
                min_value=100,
                max_value=500,
                value=220
            )
            
            scenario = st.selectbox(
                "ScÃ©nario Ã©conomique",
                ["Optimiste", "RÃ©aliste", "Pessimiste"]
            )
            
            # Facteurs de risque
            risk_factors = st.multiselect(
                "Facteurs de risque",
                ["SÃ©cheresse", "Maladies", "Prix volatils", "Retard livraison"],
                default=["Prix volatils"]
            )
        
        # Calcul des coÃ»ts prÃ©visionnels
        base_costs = {
            "Semences": 120 * surface_hectares,
            "Engrais": 180 * surface_hectares,
            "Phytosanitaires": 95 * surface_hectares,
            "Fuel": 85 * surface_hectares,
            "Main d'Å“uvre": 150 * surface_hectares,
            "MatÃ©riel": 200 * surface_hectares
        }
        
        # Ajustements selon le scÃ©nario
        scenario_multipliers = {
            "Optimiste": 0.9,
            "RÃ©aliste": 1.0,
            "Pessimiste": 1.15
        }
        
        multiplier = scenario_multipliers[scenario]
        adjusted_costs = {k: v * multiplier for k, v in base_costs.items()}
        
        # Graphique des coÃ»ts
        fig_costs = px.pie(
            values=list(adjusted_costs.values()),
            names=list(adjusted_costs.keys()),
            title=f"RÃ©partition des CoÃ»ts - {simulation_crop} ({scenario})"
        )
        
        st.plotly_chart(fig_costs, use_container_width=True)
        
        # Calcul de rentabilitÃ©
        total_costs = sum(adjusted_costs.values())
        total_revenue = surface_hectares * yield_target * market_price
        gross_margin = total_revenue - total_costs
        margin_percentage = (gross_margin / total_revenue) * 100 if total_revenue > 0 else 0
        
        # MÃ©triques financiÃ¨res
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CoÃ»ts Totaux", f"{total_costs:,.0f}â‚¬", help="Tous coÃ»ts inclus")
        
        with col2:
            st.metric("Revenus PrÃ©vus", f"{total_revenue:,.0f}â‚¬", help="Surface Ã— Rendement Ã— Prix")
        
        with col3:
            margin_color = "normal" if gross_margin > 0 else "inverse"
            st.metric(
                "Marge Brute", 
                f"{gross_margin:,.0f}â‚¬", 
                delta=f"{margin_percentage:.1f}%"
            )
        
        with col4:
            cost_per_ha = total_costs / surface_hectares
            st.metric("CoÃ»t/ha", f"{cost_per_ha:.0f}â‚¬", help="CoÃ»t moyen par hectare")
        
        # Analyse de sensibilitÃ©
        st.markdown("**ðŸ“Š Analyse de SensibilitÃ©**")
        
        # Variation des prix
        price_variations = np.arange(0.8, 1.3, 0.05)
        margin_variations = []
        
        for variation in price_variations:
            varied_revenue = total_revenue * variation
            varied_margin = varied_revenue - total_costs
            margin_variations.append(varied_margin)
        
        fig_sensitivity = go.Figure()
        
        fig_sensitivity.add_trace(go.Scatter(
            x=price_variations * 100,
            y=margin_variations,
            mode='lines+markers',
            name='Marge Brute',
            line=dict(color='blue', width=3)
        ))
        
        fig_sensitivity.add_hline(
            y=0,
            line_dash="dash",
            line_color="red",
            annotation_text="Seuil de rentabilitÃ©"
        )
        
        fig_sensitivity.update_layout(
            title="SensibilitÃ© de la Marge aux Variations de Prix",
            xaxis_title="Variation Prix (%)",
            yaxis_title="Marge Brute (â‚¬)",
            height=400
        )
        
        st.plotly_chart(fig_sensitivity, use_container_width=True)
    
    with tab5:
        st.subheader("Recommandations IA PersonnalisÃ©es")
        
        # Profil de l'exploitation
        st.markdown("**ðŸŽ¯ Profil de votre Exploitation**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            farm_type = st.selectbox(
                "Type d'exploitation",
                ["Grandes Cultures", "Ã‰levage + Cultures", "MaraÃ®chage", "Arboriculture", "Bio DiversifiÃ©e"]
            )
            
            farm_size = st.selectbox(
                "Taille exploitation",
                ["< 50 ha", "50-150 ha", "150-300 ha", "> 300 ha"]
            )
        
        with col2:
            budget_annual = st.selectbox(
                "Budget annuel intrants",
                ["< 25kâ‚¬", "25-75kâ‚¬", "75-150kâ‚¬", "150-300kâ‚¬", "> 300kâ‚¬"]
            )
            
            sustainability_focus = st.selectbox(
                "Orientation durabilitÃ©",
                ["Conventionnel", "RaisonnÃ©e", "Bio en conversion", "Bio certifiÃ©", "RÃ©gÃ©nÃ©ratrice"]
            )
        
        # Recommandations IA basÃ©es sur le profil
        st.markdown("**ðŸ¤– Recommandations PersonnalisÃ©es**")
        
        if farm_type == "Grandes Cultures" and "150-300" in farm_size:
            recommendations = [
                {
                    "type": "ðŸ’° Optimisation Achats",
                    "title": "Groupement d'Achat Engrais",
                    "description": "Ã‰conomies estimÃ©es: 12-18% sur achats engrais via coopÃ©rative rÃ©gionale",
                    "priority": "Haute",
                    "savings": "8,500â‚¬/an"
                },
                {
                    "type": "ðŸ“… Timing Optimal",
                    "title": "Achat Carburant - FenÃªtre Favorable",
                    "description": "Prix fuel agricole en baisse prÃ©vue dans 2-3 semaines",
                    "priority": "Moyenne",
                    "savings": "2,100â‚¬"
                },
                {
                    "type": "ðŸŒ± Alternative Bio",
                    "title": "Engrais Organiques SubventionnÃ©s",
                    "description": "Aide rÃ©gion disponible pour transition vers engrais organiques",
                    "priority": "Moyenne",
                    "savings": "3,200â‚¬"
                }
            ]
        else:
            recommendations = [
                {
                    "type": "ðŸ’¡ Innovation",
                    "title": "Capteurs Sol IoT",
                    "description": "Optimisation fertilisation avec capteurs connectÃ©s",
                    "priority": "Haute",
                    "savings": "15-25%"
                },
                {
                    "type": "ðŸ¤ Partenariat",
                    "title": "Ã‰change Local",
                    "description": "Plateforme d'Ã©change avec exploitations voisines",
                    "priority": "Moyenne",
                    "savings": "Variable"
                }
            ]
        
        for rec in recommendations:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    priority_color = {"Haute": "red", "Moyenne": "orange", "Basse": "green"}.get(rec['priority'], "blue")
                    st.markdown(f"**{rec['type']}** :{priority_color}[{rec['priority']}]")
                    st.markdown(f"**{rec['title']}**")
                    st.write(rec['description'])
                
                with col2:
                    st.metric("Ã‰conomies", rec['savings'])
                
                with col3:
                    if st.button("âœ… IntÃ©ressÃ©", key=f"rec_{rec['title']}"):
                        st.success("Recommandation sauvegardÃ©e!")
                    
                    if st.button("â„¹ï¸ DÃ©tails", key=f"details_rec_{rec['title']}"):
                        st.info(f"Plus d'infos sur: {rec['title']}")
                
                st.markdown("---")
        
        # Alertes de marchÃ©
        st.markdown("**ðŸ“ˆ Alertes MarchÃ©**")
        
        market_alerts = [
            "ðŸš¨ Prix blÃ© +8% cette semaine - OpportunitÃ© de vente",
            "ðŸ“‰ Engrais azotÃ©s -5% attendu mois prochain",
            "âš ï¸ PÃ©nurie phytos prÃ©vue - Anticiper commandes",
            "ðŸ’¡ Nouveau produit bio: -20% prix lancement"
        ]
        
        for alert in market_alerts:
            st.warning(alert)

elif user_type == "ðŸ­ Vendeur (Fournisseur)":
    tab1, tab2, tab3, tab4 = st.tabs([
        "Mon Catalogue", 
        "Commandes ReÃ§ues", 
        "Analytics Ventes", 
        "Gestion Stocks"
    ])
    
    with tab1:
        st.subheader("Gestion de Mon Catalogue")
        st.info("Interface vendeur en dÃ©veloppement - FonctionnalitÃ©s complÃ¨tes disponibles prochainement")
    
    with tab2:
        st.subheader("Commandes ReÃ§ues")
        st.info("Tableau de bord des commandes en dÃ©veloppement")
    
    with tab3:
        st.subheader("Analytics des Ventes")
        st.info("Analyses de performance des ventes en dÃ©veloppement")
    
    with tab4:
        st.subheader("Gestion des Stocks")
        st.info("SystÃ¨me de gestion des stocks en dÃ©veloppement")

else:  # Analyste MarchÃ©
    st.subheader("Analyses de MarchÃ© AvancÃ©es")
    st.info("Module d'analyse de marchÃ© en dÃ©veloppement - DonnÃ©es Ã©conomiques et tendances")

# Sidebar market info
st.sidebar.markdown("---")
st.sidebar.markdown("**ðŸ“Š Info MarchÃ©**")

# Prix du jour simulÃ©s
daily_prices = {
    "BlÃ©": 218.50,
    "MaÃ¯s": 195.20,
    "Colza": 425.80,
    "Fuel": 0.67
}

for commodity, price in daily_prices.items():
    change = np.random.uniform(-5, 5)
    delta_color = "normal" if change >= 0 else "inverse"
    st.sidebar.metric(
        commodity,
        f"{price:.2f}â‚¬",
        delta=f"{change:+.1f}â‚¬"
    )

st.sidebar.metric("Transactions/jour", "1,247")
st.sidebar.metric("Utilisateurs actifs", "8,932")

# Footer
st.markdown("---")
st.markdown("**ðŸ›’ Marketplace Agricole** - Plateforme intÃ©grÃ©e d'achat/vente avec IA prÃ©dictive")


