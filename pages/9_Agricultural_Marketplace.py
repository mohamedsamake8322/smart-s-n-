import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

# 🔐 Initialisation sûre du panier
if 'cart' not in st.session_state:
    st.session_state.cart = []

st.set_page_config(page_title="Agricultural Marketplace", page_icon="🛒", layout="wide")
# 🛒 Affichage dynamique du contenu du panier
st.sidebar.markdown(f"🛒 Panier : {len(st.session_state.cart)} article(s)")
st.title("🛒 Marketplace Agricole Intégrée")
st.markdown("### Plateforme d'achat/vente d'intrants et prévisions de rentabilité")

# Sidebar controls
st.sidebar.title("Navigation Marketplace")

user_type = st.sidebar.selectbox(
    "Type d'utilisateur",
    ["🌾 Acheteur (Agriculteur)", "🏭 Vendeur (Fournisseur)", "📊 Analyste Marché"]
)

region = st.sidebar.selectbox(
    "Région",
    ["Île-de-France", "Nouvelle-Aquitaine", "Occitanie", "Grand Est", "Hauts-de-France", "Toutes régions"]
)

currency = st.sidebar.selectbox(
    "Devise",
    ["EUR (€)", "USD ($)", "GBP (£)"]
)

# Main content tabs
if user_type == "🌾 Acheteur (Agriculteur)":
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Catalogue Intrants",
        "Comparateur Prix",
        "Mes Commandes",
        "Prévisions Coûts",
        "Recommandations IA"
    ])

    with tab1:
        st.subheader("Catalogue des Intrants Agricoles")

        # Filtres de recherche
        col1, col2, col3 = st.columns(3)

        with col1:
            category = st.selectbox(
                "Catégorie",
                ["Toutes", "Semences", "Engrais", "Pesticides", "Matériel", "Équipements"]
            )

        with col2:
            crop_type = st.selectbox(
                "Type de culture",
                ["Toutes", "Céréales", "Légumineuses", "Oléagineux", "Maraîchage", "Arboriculture"]
            )

        with col3:
            price_range = st.selectbox(
                "Gamme de prix",
                ["Toutes", "< 50€", "50-200€", "200-500€", "500-1000€", "> 1000€"]
            )

        # Génération de données produits simulées
        products_data = []
        categories = ["Semences", "Engrais", "Pesticides", "Matériel"]

        for i in range(20):
            product = {
                "id": f"PROD_{i+1:03d}",
                "nom": f"Produit {i+1}",
                "categorie": np.random.choice(categories),
                "prix": np.random.uniform(25, 800),
                "unite": np.random.choice(["kg", "L", "unité", "sac"]),
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
                    promotion_tag = "🏷️ PROMO" if product['promotion'] else ""
                    bio_tag = "🌱 BIO" if product['bio'] else ""
                    st.markdown(f"**{product['nom']}** {promotion_tag} {bio_tag}")
                    st.write(f"Catégorie: {product['categorie']}")
                    st.write(f"Fournisseur: {product['fournisseur']}")
                    st.write(f"⭐ {product['rating']:.1f}/5")

                with col2:
                    if product['promotion']:
                        original_price = product['prix'] * 1.2
                        st.markdown(f"~~{original_price:.2f}€~~ **{product['prix']:.2f}€**/{product['unite']}")
                    else:
                        st.markdown(f"**{product['prix']:.2f}€**/{product['unite']}")

                    stock_color = "green" if product['stock'] > 100 else "orange" if product['stock'] > 0 else "red"
                    st.markdown(f"Stock: :{stock_color}[{product['stock']}]")

                with col3:
                    st.write(f"🚚 {product['livraison']} jours")
                    if product['stock'] > 0:
                        quantity = st.number_input(
                            "Quantité",
                            min_value=1,
                            max_value=min(100, product['stock']),
                            value=1,
                            key=f"qty_{product['id']}"
                    )
                    else:
                        st.error("Produit actuellement en rupture de stock ❌")
                with col4:
                    if product['stock'] > 0:
                        if st.button("🛒 Ajouter", key=f"add_{product['id']}"):
                            st.session_state.cart.append({
                            'product': product['nom'],
                            'price': product['prix'],
                            'quantity': quantity,
                            'total': product['prix'] * quantity
                        })
                        st.success(f"Ajouté au panier!")
                    else:
                        st.button("🚫 Indisponible", key=f"out_{product['id']}", disabled=True)
                    if st.button("👁️ Détails", key=f"details_{product['id']}"):
                        st.info(f"Détails de {product['nom']}")

                st.markdown("---")

    with tab2:
        st.subheader("Comparateur de Prix en Temps Réel")

        # Sélection du produit à comparer
        product_to_compare = st.selectbox(
            "Produit à comparer",
            ["Engrais NPK 15-15-15", "Semences Blé Tendre", "Pesticide Glyphosate", "Fuel Agricole"]
        )

        # Données de comparaison simulées
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
            labels={'value': 'Prix (€)', 'variable': 'Composante'},
            color_discrete_map={'prix': 'lightblue', 'frais_port': 'orange'}
        )

        st.plotly_chart(fig_comparison, use_container_width=True)

        # Tableau de comparaison détaillé
        st.markdown("**Comparaison Détaillée**")

        for i, supplier in suppliers_df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

            with col1:
                certification_icon = {"Bio": "🌱", "Standard": "📦", "Premium": "⭐"}.get(supplier['certification'], "")
                st.write(f"**{supplier['fournisseur']}** {certification_icon}")
                st.write(f"⭐ {supplier['rating']:.1f}/5")

            with col2:
                st.metric("Prix Unitaire", f"{supplier['prix']:.2f}€")

            with col3:
                st.metric("Livraison", f"{supplier['livraison']} jours")
                st.write(f"Port: {supplier['frais_port']:.2f}€")

            with col4:
                st.metric("Total", f"{supplier['prix_total']:.2f}€")

                if i == 0:
                    st.success("🏆 Meilleur prix")

            with col5:
                if st.button("Sélectionner", key=f"select_{i}"):
                    st.success(f"Sélectionné: {supplier['fournisseur']}")

        # Évolution des prix
        st.markdown("**📈 Évolution des Prix (30 jours)**")

        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        base_price = 65
        price_evolution = base_price + np.cumsum(np.random.normal(0, 2, 30))

        fig_price_evolution = px.line(
            x=dates,
            y=price_evolution,
            title=f"Évolution Prix - {product_to_compare}",
            labels={'x': 'Date', 'y': 'Prix (€)'}
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
            st.metric("Total ce mois", "2,458€", delta="15.2%")
        with col3:
            st.metric("Économies réalisées", "347€", delta="12.8%")

        # Commandes récentes
        st.markdown("**Commandes Récentes**")

        orders_data = [
            {
                "id": "CMD_001",
                "date": "2024-06-10",
                "produits": "Engrais NPK, Semences Blé",
                "montant": 456.78,
                "statut": "En livraison",
                "livraison_prevue": "2024-06-14"
            },
            {
                "id": "CMD_002",
                "date": "2024-06-08",
                "produits": "Pesticide Bio, Matériel",
                "montant": 234.50,
                "statut": "Livré",
                "livraison_prevue": "2024-06-12"
            },
            {
                "id": "CMD_003",
                "date": "2024-06-05",
                "produits": "Fuel Agricole",
                "montant": 189.32,
                "statut": "En préparation",
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
                    st.write(f"**{order['montant']:.2f}€**")

                    status_color = {
                        "Livré": "green",
                        "En livraison": "orange",
                        "En préparation": "blue"
                    }.get(order['statut'], "gray")

                    st.markdown(f":{status_color}[{order['statut']}]")

                with col4:
                    st.write(f"📅 {order['livraison_prevue']}")

                    if order['statut'] != "Livré":
                        if st.button("📍 Suivre", key=f"track_{order['id']}"):
                            st.info("Suivi de commande activé")

                st.markdown("---")

        # Panier actuel
        if 'cart' in st.session_state and st.session_state.cart:
            st.markdown("**🛒 Panier Actuel**")

            total_cart = sum(item['total'] for item in st.session_state.cart)

            for item in st.session_state.cart:
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.write(f"{item['product']} x{item['quantity']}")
                with col2:
                    st.write(f"{item['price']:.2f}€ / unité")
                with col3:
                    st.write(f"**{item['total']:.2f}€**")

            st.markdown(f"**Total: {total_cart:.2f}€**")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Vider Panier"):
                    st.session_state.cart = []
                    st.rerun()

            with col2:
                if st.button("✅ Confirmer Commande"):
                    st.success("Commande confirmée!")
                    st.session_state.cart = []

    with tab4:
        st.subheader("Prévisions de Coûts et Rentabilité")

        # Configuration de la simulation
        col1, col2 = st.columns(2)

        with col1:
            simulation_crop = st.selectbox(
                "Culture à analyser",
                ["Blé Tendre", "Maïs Grain", "Colza", "Tournesol", "Orge"]
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
                "Prix de vente prévu (€/t)",
                min_value=100,
                max_value=500,
                value=220
            )

            scenario = st.selectbox(
                "Scénario économique",
                ["Optimiste", "Réaliste", "Pessimiste"]
            )

            # Facteurs de risque
            risk_factors = st.multiselect(
                "Facteurs de risque",
                ["Sécheresse", "Maladies", "Prix volatils", "Retard livraison"],
                default=["Prix volatils"]
            )

        # Calcul des coûts prévisionnels
        base_costs = {
            "Semences": 120 * surface_hectares,
            "Engrais": 180 * surface_hectares,
            "Phytosanitaires": 95 * surface_hectares,
            "Fuel": 85 * surface_hectares,
            "Main d'œuvre": 150 * surface_hectares,
            "Matériel": 200 * surface_hectares
        }

        # Ajustements selon le scénario
        scenario_multipliers = {
            "Optimiste": 0.9,
            "Réaliste": 1.0,
            "Pessimiste": 1.15
        }

        multiplier = scenario_multipliers[scenario]
        adjusted_costs = {k: v * multiplier for k, v in base_costs.items()}

        # Graphique des coûts
        fig_costs = px.pie(
            values=list(adjusted_costs.values()),
            names=list(adjusted_costs.keys()),
            title=f"Répartition des Coûts - {simulation_crop} ({scenario})"
        )

        st.plotly_chart(fig_costs, use_container_width=True)

        # Calcul de rentabilité
        total_costs = sum(adjusted_costs.values())
        total_revenue = surface_hectares * yield_target * market_price
        gross_margin = total_revenue - total_costs
        margin_percentage = (gross_margin / total_revenue) * 100 if total_revenue > 0 else 0

        # Métriques financières
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Coûts Totaux", f"{total_costs:,.0f}€", help="Tous coûts inclus")

        with col2:
            st.metric("Revenus Prévus", f"{total_revenue:,.0f}€", help="Surface × Rendement × Prix")

        with col3:
            margin_color = "normal" if gross_margin > 0 else "inverse"
            st.metric(
                "Marge Brute",
                f"{gross_margin:,.0f}€",
                delta=f"{margin_percentage:.1f}%"
            )

        with col4:
            cost_per_ha = total_costs / surface_hectares
            st.metric("Coût/ha", f"{cost_per_ha:.0f}€", help="Coût moyen par hectare")

        # Analyse de sensibilité
        st.markdown("**📊 Analyse de Sensibilité**")

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
            annotation_text="Seuil de rentabilité"
        )

        fig_sensitivity.update_layout(
            title="Sensibilité de la Marge aux Variations de Prix",
            xaxis_title="Variation Prix (%)",
            yaxis_title="Marge Brute (€)",
            height=400
        )

        st.plotly_chart(fig_sensitivity, use_container_width=True)

    with tab5:
        st.subheader("Recommandations IA Personnalisées")

        # Profil de l'exploitation
        st.markdown("**🎯 Profil de votre Exploitation**")

        col1, col2 = st.columns(2)

        with col1:
            farm_type = st.selectbox(
                "Type d'exploitation",
                ["Grandes Cultures", "Élevage + Cultures", "Maraîchage", "Arboriculture", "Bio Diversifiée"]
            )

            farm_size = st.selectbox(
                "Taille exploitation",
                ["< 50 ha", "50-150 ha", "150-300 ha", "> 300 ha"]
            )

        with col2:
            budget_annual = st.selectbox(
                "Budget annuel intrants",
                ["< 25k€", "25-75k€", "75-150k€", "150-300k€", "> 300k€"]
            )

            sustainability_focus = st.selectbox(
                "Orientation durabilité",
                ["Conventionnel", "Raisonnée", "Bio en conversion", "Bio certifié", "Régénératrice"]
            )

        # Recommandations IA basées sur le profil
        st.markdown("**🤖 Recommandations Personnalisées**")

        if farm_type == "Grandes Cultures" and "150-300" in farm_size:
            recommendations = [
                {
                    "type": "💰 Optimisation Achats",
                    "title": "Groupement d'Achat Engrais",
                    "description": "Économies estimées: 12-18% sur achats engrais via coopérative régionale",
                    "priority": "Haute",
                    "savings": "8,500€/an"
                },
                {
                    "type": "📅 Timing Optimal",
                    "title": "Achat Carburant - Fenêtre Favorable",
                    "description": "Prix fuel agricole en baisse prévue dans 2-3 semaines",
                    "priority": "Moyenne",
                    "savings": "2,100€"
                },
                {
                    "type": "🌱 Alternative Bio",
                    "title": "Engrais Organiques Subventionnés",
                    "description": "Aide région disponible pour transition vers engrais organiques",
                    "priority": "Moyenne",
                    "savings": "3,200€"
                }
            ]
        else:
            recommendations = [
                {
                    "type": "💡 Innovation",
                    "title": "Capteurs Sol IoT",
                    "description": "Optimisation fertilisation avec capteurs connectés",
                    "priority": "Haute",
                    "savings": "15-25%"
                },
                {
                    "type": "🤝 Partenariat",
                    "title": "Échange Local",
                    "description": "Plateforme d'échange avec exploitations voisines",
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
                    st.metric("Économies", rec['savings'])

                with col3:
                    if st.button("✅ Intéressé", key=f"rec_{rec['title']}"):
                        st.success("Recommandation sauvegardée!")

                    if st.button("ℹ️ Détails", key=f"details_rec_{rec['title']}"):
                        st.info(f"Plus d'infos sur: {rec['title']}")

                st.markdown("---")

        # Alertes de marché
        st.markdown("**📈 Alertes Marché**")

        market_alerts = [
            "🚨 Prix blé +8% cette semaine - Opportunité de vente",
            "📉 Engrais azotés -5% attendu mois prochain",
            "⚠️ Pénurie phytos prévue - Anticiper commandes",
            "💡 Nouveau produit bio: -20% prix lancement"
        ]

        for alert in market_alerts:
            st.warning(alert)

elif user_type == "🏭 Vendeur (Fournisseur)":
    tab1, tab2, tab3, tab4 = st.tabs([
        "Mon Catalogue",
        "Commandes Reçues",
        "Analytics Ventes",
        "Gestion Stocks"
    ])

    with tab1:
        st.subheader("Gestion de Mon Catalogue")
        st.info("Interface vendeur en développement - Fonctionnalités complètes disponibles prochainement")

    with tab2:
        st.subheader("Commandes Reçues")
        st.info("Tableau de bord des commandes en développement")

    with tab3:
        st.subheader("Analytics des Ventes")
        st.info("Analyses de performance des ventes en développement")

    with tab4:
        st.subheader("Gestion des Stocks")
        st.info("Système de gestion des stocks en développement")

else:  # Analyste Marché
    st.subheader("Analyses de Marché Avancées")
    st.info("Module d'analyse de marché en développement - Données économiques et tendances")

# Sidebar market info
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Info Marché**")

# Prix du jour simulés
daily_prices = {
    "Blé": 218.50,
    "Maïs": 195.20,
    "Colza": 425.80,
    "Fuel": 0.67
}

for commodity, price in daily_prices.items():
    change = np.random.uniform(-5, 5)
    delta_color = "normal" if change >= 0 else "inverse"
    st.sidebar.metric(
        commodity,
        f"{price:.2f}€",
        delta=f"{change:+.1f}€"
    )

st.sidebar.metric("Transactions/jour", "1,247")
st.sidebar.metric("Utilisateurs actifs", "8,932")

# Footer
st.markdown("---")
st.markdown("**🛒 Marketplace Agricole** - Plateforme intégrée d'achat/vente avec IA prédictive")
