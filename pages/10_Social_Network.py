
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

st.set_page_config(page_title="Social Network", page_icon="🤝", layout="wide")

st.title("🤝 Réseau Social Agricole")
st.markdown("### Communauté d'échange entre agriculteurs et experts")

# Sidebar controls
st.sidebar.title("Mon Profil")

if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {
        'name': 'Jean Dupont',
        'type': 'Agriculteur',
        'specialite': 'Grandes Cultures',
        'region': 'Nouvelle-Aquitaine',
        'experience': '15 ans',
        'followers': 234,
        'following': 189,
        'posts': 67
    }

profile = st.session_state.user_profile

st.sidebar.markdown(f"**{profile['name']}**")
st.sidebar.markdown(f"{profile['type']} - {profile['specialite']}")
st.sidebar.markdown(f"📍 {profile['region']}")
st.sidebar.markdown(f"🎯 {profile['experience']} d'expérience")

col1, col2, col3 = st.sidebar.columns(3)
with col1:
    st.metric("Posts", profile['posts'])
with col2:
    st.metric("Abonnés", profile['followers'])
with col3:
    st.metric("Suivi", profile['following'])

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Fil d'Actualité",
    "Groupes & Forums", 
    "Questions/Réponses",
    "Événements",
    "Marketplace Social"
])

with tab1:
    st.subheader("Fil d'Actualité Agricole")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Nouveau post
        with st.expander("✍️ Publier un nouveau post", expanded=False):
            post_type = st.selectbox(
                "Type de post",
                ["💬 Discussion", "❓ Question", "📸 Photo/Vidéo", "📊 Retour d'expérience", "🚨 Alerte"]
            )
            
            post_content = st.text_area(
                "Contenu",
                placeholder="Partagez votre expérience, posez une question..."
            )
            
            if post_type == "📸 Photo/Vidéo":
                uploaded_file = st.file_uploader(
                    "Ajouter une image",
                    type=['png', 'jpg', 'jpeg']
                )
            
            tags = st.text_input(
                "Tags",
                placeholder="#blé #rendement #bio"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📤 Publier"):
                    if post_content:
                        st.success("Post publié avec succès!")
                    else:
                        st.error("Veuillez ajouter du contenu")
            
            with col_btn2:
                if st.button("💾 Brouillon"):
                    st.info("Sauvegardé en brouillon")
        
        # Posts du fil d'actualité
        posts_data = [
            {
                "author": "Marie Leblanc",
                "type": "Experte Phytopathologie",
                "time": "Il y a 2h",
                "content": "Attention aux conditions humides actuelles favorables au développement de la rouille sur blé. Surveillez vos parcelles et n'hésitez pas si vous avez des questions! 🌾",
                "tags": ["#blé", "#maladies", "#rouille"],
                "likes": 23,
                "comments": 8,
                "shares": 4,
                "image": None
            },
            {
                "author": "Pierre Martin",
                "type": "Agriculteur - Céréales",
                "time": "Il y a 4h", 
                "content": "Premier passage de désherbant sur colza terminé sur mes 45ha. Conditions parfaites cette semaine! Quelqu'un a-t-il testé les nouveaux produits bio?",
                "tags": ["#colza", "#désherbage", "#bio"],
                "likes": 15,
                "comments": 12,
                "shares": 2,
                "image": "colza.jpg"
            },
            {
                "author": "Sophie Rousseau", 
                "type": "Conseillère Technique",
                "time": "Il y a 6h",
                "content": "📊 Résultats prometteurs sur nos essais de semis direct. Économies de carburant de 30% et amélioration de la structure du sol. Retour d'expérience complet en commentaires!",
                "tags": ["#semisdirect", "#durabilité", "#innovation"],
                "likes": 41,
                "comments": 19,
                "shares": 12,
                "image": "semis_direct.jpg"
            }
        ]
        
        for i, post in enumerate(posts_data):
            with st.container():
                # En-tête du post
                col_avatar, col_info = st.columns([1, 4])
                
                with col_avatar:
                    st.markdown("👤")  # Avatar placeholder
                
                with col_info:
                    st.markdown(f"**{post['author']}**")
                    st.markdown(f"*{post['type']}* • {post['time']}")
                
                # Contenu
                st.markdown(post['content'])
                
                # Tags
                if post['tags']:
                    tag_str = " ".join(post['tags'])
                    st.markdown(f"*{tag_str}*")
                
                # Image si présente
                if post['image']:
                    st.image(f"https://via.placeholder.com/400x200/4CAF50/white?text={post['image']}", 
                            width=400, caption=post['image'])
                
                # Actions
                col_like, col_comment, col_share, col_save = st.columns(4)
                
                with col_like:
                    if st.button(f"👍 {post['likes']}", key=f"like_{i}"):
                        st.success("J'aime ajouté!")
                
                with col_comment:
                    if st.button(f"💬 {post['comments']}", key=f"comment_{i}"):
                        st.info("Commentaires affichés")
                
                with col_share:
                    if st.button(f"🔄 {post['shares']}", key=f"share_{i}"):
                        st.info("Post partagé!")
                
                with col_save:
                    if st.button("🔖 Sauver", key=f"save_{i}"):
                        st.info("Post sauvegardé")
                
                st.markdown("---")
    
    with col2:
        # Widget recommandations
        st.markdown("**👥 Suggestions de Suivi**")
        
        suggestions = [
            {"name": "Dr. Alain Petit", "type": "Expert Sol", "mutual": 12},
            {"name": "Ferme Bio du Lot", "type": "Producteur Bio", "mutual": 8},
            {"name": "Coop Agricole 47", "type": "Coopérative", "mutual": 23}
        ]
        
        for sugg in suggestions:
            with st.container():
                st.markdown(f"**{sugg['name']}**")
                st.markdown(f"*{sugg['type']}*")
                st.markdown(f"👥 {sugg['mutual']} amis en commun")
                
                if st.button("➕ Suivre", key=f"follow_{sugg['name']}"):
                    st.success(f"Vous suivez maintenant {sugg['name']}")
                
                st.markdown("---")
        
        # Trending topics
        st.markdown("**🔥 Sujets Tendance**")
        
        trending = [
            {"tag": "#sécheresse2024", "posts": 156},
            {"tag": "#prixcereales", "posts": 89},
            {"tag": "#semisdirect", "posts": 67},
            {"tag": "#agritech", "posts": 45},
            {"tag": "#biocontrole", "posts": 34}
        ]
        
        for trend in trending:
            col_tag, col_count = st.columns([2, 1])
            with col_tag:
                st.markdown(f"**{trend['tag']}**")
            with col_count:
                st.markdown(f"{trend['posts']} posts")

with tab2:
    st.subheader("Groupes & Forums Spécialisés")
    
    # Mes groupes
    st.markdown("**🏠 Mes Groupes**")
    
    my_groups = [
        {
            "name": "Céréaliers Nouvelle-Aquitaine",
            "members": 1247,
            "new_posts": 12,
            "category": "Régional",
            "private": False
        },
        {
            "name": "Innovation AgriTech",
            "members": 3456,
            "new_posts": 8,
            "category": "Innovation",
            "private": False
        },
        {
            "name": "Réseau Bio France",
            "members": 892,
            "new_posts": 15,
            "category": "Bio",
            "private": True
        }
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        for group in my_groups:
            with st.container():
                col_info, col_stats, col_action = st.columns([2, 1, 1])
                
                with col_info:
                    privacy_icon = "🔒" if group['private'] else "🌐"
                    st.markdown(f"**{group['name']}** {privacy_icon}")
                    st.markdown(f"*{group['category']}*")
                
                with col_stats:
                    st.metric("Membres", group['members'])
                    if group['new_posts'] > 0:
                        st.markdown(f"🆕 {group['new_posts']} nouveaux posts")
                
                with col_action:
                    if st.button("📖 Ouvrir", key=f"open_{group['name']}"):
                        st.info(f"Ouverture du groupe {group['name']}")
                
                st.markdown("---")
    
    with col2:
        st.markdown("**🔍 Découvrir des Groupes**")
        
        search_term = st.text_input("Rechercher un groupe")
        
        group_categories = st.multiselect(
            "Catégories",
            ["Grandes Cultures", "Élevage", "Maraîchage", "Bio", "Innovation", "Régional"],
            default=["Grandes Cultures"]
        )
        
        # Groupes suggérés
        suggested_groups = [
            {"name": "Machinisme Agricole", "members": 2134, "category": "Équipement"},
            {"name": "Jeunes Agriculteurs", "members": 5678, "category": "Communauté"},
            {"name": "Agroécologie Pratique", "members": 1567, "category": "Durabilité"}
        ]
        
        for group in suggested_groups:
            st.markdown(f"**{group['name']}**")
            st.markdown(f"{group['members']} membres • {group['category']}")
            if st.button("➕ Rejoindre", key=f"join_{group['name']}"):
                st.success(f"Demande envoyée pour {group['name']}")
            st.markdown("---")

with tab3:
    st.subheader("Questions & Réponses d'Experts")
    
    # Poser une question
    with st.expander("❓ Poser une nouvelle question", expanded=False):
        question_category = st.selectbox(
            "Catégorie",
            ["Cultures", "Sol", "Phytosanitaire", "Matériel", "Économie", "Réglementation"]
        )
        
        question_title = st.text_input("Titre de la question")
        question_detail = st.text_area("Description détaillée")
        
        question_urgency = st.selectbox(
            "Urgence",
            ["🟢 Normale", "🟡 Modérée", "🔴 Urgente"]
        )
        
        if st.button("📤 Publier Question"):
            if question_title and question_detail:
                st.success("Question publiée! Les experts vont répondre.")
            else:
                st.error("Veuillez remplir tous les champs")
    
    # Questions récentes
    st.markdown("**❓ Questions Récentes**")
    
    questions_data = [
        {
            "title": "Dose de semis pour blé tendre en terre argileuse?",
            "author": "Thomas R.",
            "category": "Cultures",
            "time": "Il y a 1h",
            "answers": 3,
            "views": 47,
            "urgency": "🟡 Modérée",
            "preview": "J'ai 25ha de blé à semer sur terre argileuse lourde. Quelle dose recommandez-vous cette année?"
        },
        {
            "title": "Traitement bio contre les pucerons sur colza",
            "author": "Marie L.",
            "category": "Phytosanitaire", 
            "time": "Il y a 3h",
            "answers": 7,
            "views": 123,
            "urgency": "🔴 Urgente",
            "preview": "Invasion de pucerons sur mes parcelles de colza bio. Solutions naturelles efficaces?"
        },
        {
            "title": "Rentabilité du semis direct en grande culture",
            "author": "Pierre M.",
            "category": "Économie",
            "time": "Il y a 5h", 
            "answers": 12,
            "views": 189,
            "urgency": "🟢 Normale",
            "preview": "Quelqu'un a-t-il calculé la rentabilité réelle du passage en semis direct?"
        }
    ]
    
    for i, q in enumerate(questions_data):
        with st.container():
            col_main, col_stats = st.columns([3, 1])
            
            with col_main:
                st.markdown(f"**{q['title']}** {q['urgency']}")
                st.markdown(f"Par *{q['author']}* • {q['category']} • {q['time']}")
                st.markdown(q['preview'])
                
                col_answer, col_view = st.columns(2)
                with col_answer:
                    if st.button(f"💬 Répondre", key=f"answer_{i}"):
                        st.info("Interface de réponse ouverte")
                with col_view:
                    if st.button(f"👁️ Voir détails", key=f"view_{i}"):
                        st.info("Question détaillée affichée")
            
            with col_stats:
                st.metric("Réponses", q['answers'])
                st.metric("Vues", q['views'])
            
            st.markdown("---")

with tab4:
    st.subheader("Événements et Rencontres")
    
    # Filtres d'événements
    col1, col2, col3 = st.columns(3)
    
    with col1:
        event_type = st.selectbox(
            "Type d'événement",
            ["Tous", "Formation", "Conférence", "Visite d'exploitation", "Salon", "Webinaire"]
        )
    
    with col2:
        event_location = st.selectbox(
            "Localisation",
            ["Toutes", "À proximité (50km)", "Ma région", "France", "Europe"]
        )
    
    with col3:
        event_date = st.selectbox(
            "Période",
            ["Cette semaine", "Ce mois", "Prochains 3 mois", "Toutes dates"]
        )
    
    # Événements à venir
    st.markdown("**📅 Événements à Venir**")
    
    events_data = [
        {
            "title": "Journée Technique Semis Direct",
            "date": "15 Juin 2024",
            "time": "9h00 - 17h00",
            "location": "Ferme Pilote, Agen (47)",
            "type": "Visite d'exploitation",
            "attendees": 45,
            "max_attendees": 60,
            "price": "Gratuit",
            "organizer": "Chambre d'Agriculture 47"
        },
        {
            "title": "Webinaire: Gestion de l'Eau en Agriculture",
            "date": "18 Juin 2024", 
            "time": "14h00 - 15h30",
            "location": "En ligne",
            "type": "Webinaire",
            "attendees": 234,
            "max_attendees": 500,
            "price": "Gratuit",
            "organizer": "Institut Agricole"
        },
        {
            "title": "Salon AgriTech Innovation",
            "date": "25-27 Juin 2024",
            "time": "3 jours",
            "location": "Toulouse (31)",
            "type": "Salon",
            "attendees": 1247,
            "max_attendees": 5000,
            "price": "45€",
            "organizer": "AgriExpo France"
        }
    ]
    
    for i, event in enumerate(events_data):
        with st.container():
            col_info, col_details, col_action = st.columns([2, 1, 1])
            
            with col_info:
                st.markdown(f"**{event['title']}**")
                st.markdown(f"📅 {event['date']} • ⏰ {event['time']}")
                st.markdown(f"📍 {event['location']}")
                st.markdown(f"🏢 {event['organizer']}")
            
            with col_details:
                st.markdown(f"**{event['type']}**")
                st.markdown(f"💰 {event['price']}")
                
                attendance_ratio = event['attendees'] / event['max_attendees']
                color = "green" if attendance_ratio < 0.7 else "orange" if attendance_ratio < 0.9 else "red"
                st.markdown(f"👥 {event['attendees']}/{event['max_attendees']}")
                
                progress = st.progress(attendance_ratio)
            
            with col_action:
                if attendance_ratio < 1.0:
                    if st.button("✅ S'inscrire", key=f"register_{i}"):
                        st.success(f"Inscription confirmée pour {event['title']}")
                else:
                    st.error("Complet")
                
                if st.button("🔗 Partager", key=f"share_event_{i}"):
                    st.info("Lien de partage copié")
            
            st.markdown("---")
    
    # Créer un événement
    with st.expander("➕ Créer un événement", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_event_title = st.text_input("Titre de l'événement")
            new_event_type = st.selectbox("Type", ["Formation", "Visite", "Conférence", "Rencontre"])
            new_event_date = st.date_input("Date")
        
        with col2:
            new_event_location = st.text_input("Lieu")
            new_event_price = st.text_input("Prix (0 si gratuit)")
            new_event_capacity = st.number_input("Capacité max", min_value=1, value=50)
        
        new_event_description = st.text_area("Description")
        
        if st.button("📅 Créer Événement"):
            if new_event_title and new_event_location:
                st.success("Événement créé avec succès!")
            else:
                st.error("Veuillez remplir les champs obligatoires")

with tab5:
    st.subheader("Marketplace Social - Échanges entre Agriculteurs")
    
    # Types d'échanges
    exchange_type = st.selectbox(
        "Type d'échange",
        ["🌾 Produits", "🚜 Matériel", "🤝 Services", "🧠 Conseils", "🌱 Semences"]
    )
    
    # Offres/Demandes récentes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📤 Offres Récentes**")
        
        offers_data = [
            {
                "type": "🌾 Produits",
                "title": "Paille de blé - 200 bottes rondes",
                "author": "Ferme Dubois",
                "location": "Lot-et-Garonne (47)",
                "price": "25€/botte",
                "time": "Il y a 2h"
            },
            {
                "type": "🚜 Matériel", 
                "title": "Épandeur à fumier 8T - Location",
                "author": "CUMA du Périgord",
                "location": "Dordogne (24)",
                "price": "80€/jour",
                "time": "Il y a 4h"
            },
            {
                "type": "🤝 Services",
                "title": "Moisson blé/orge - Prestation",
                "author": "ETA Martin",
                "location": "Gers (32)",
                "price": "120€/ha",
                "time": "Il y a 6h"
            }
        ]
        
        for i, offer in enumerate(offers_data):
            with st.container():
                st.markdown(f"**{offer['title']}** {offer['type']}")
                st.markdown(f"Par *{offer['author']}* • {offer['location']}")
                st.markdown(f"💰 {offer['price']} • {offer['time']}")
                
                col_contact, col_save = st.columns(2)
                with col_contact:
                    if st.button("📞 Contacter", key=f"contact_offer_{i}"):
                        st.success("Message envoyé!")
                with col_save:
                    if st.button("⭐ Suivre", key=f"follow_offer_{i}"):
                        st.info("Offre suivie")
                
                st.markdown("---")
    
    with col2:
        st.markdown("**📥 Demandes Récentes**")
        
        requests_data = [
            {
                "type": "🌱 Semences",
                "title": "Recherche semences tournesol bio",
                "author": "Bio Ferme 82",
                "location": "Tarn-et-Garonne (82)",
                "quantity": "50kg",
                "time": "Il y a 1h"
            },
            {
                "type": "🚜 Matériel",
                "title": "Besoin semoir céréales pour 3 jours",
                "author": "GAEC Nouvelle Terre",
                "location": "Gironde (33)",
                "period": "Fin septembre",
                "time": "Il y a 3h"
            },
            {
                "type": "🧠 Conseils",
                "title": "Conseil rotation cultures bio",
                "author": "Néo-Agriculteur",
                "location": "Lot (46)",
                "context": "Installation récente",
                "time": "Il y a 5h"
            }
        ]
        
        for i, request in enumerate(requests_data):
            with st.container():
                st.markdown(f"**{request['title']}** {request['type']}")
                st.markdown(f"Par *{request['author']}* • {request['location']}")
                
                detail_key = 'quantity' if 'quantity' in request else 'period' if 'period' in request else 'context'
                st.markdown(f"📋 {request[detail_key]} • {request['time']}")
                
                col_respond, col_save = st.columns(2)
                with col_respond:
                    if st.button("💬 Répondre", key=f"respond_request_{i}"):
                        st.success("Réponse envoyée!")
                with col_save:
                    if st.button("🔔 Alerter", key=f"alert_request_{i}"):
                        st.info("Alerte créée")
                
                st.markdown("---")
    
    # Publier une offre/demande
    with st.expander("➕ Publier une offre ou demande", expanded=False):
        offer_or_request = st.radio(
            "Type de publication",
            ["📤 Offre", "📥 Demande"],
            horizontal=True
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            pub_type = st.selectbox("Catégorie", ["Produits", "Matériel", "Services", "Conseils", "Semences"])
            pub_title = st.text_input("Titre")
            pub_location = st.text_input("Localisation")
        
        with col2:
            if offer_or_request == "📤 Offre":
                pub_price = st.text_input("Prix proposé")
            else:
                pub_budget = st.text_input("Budget disponible")
            
            pub_period = st.text_input("Période/Échéance")
            pub_quantity = st.text_input("Quantité/Durée")
        
        pub_description = st.text_area("Description détaillée", key="pub_description")
        
        if st.button(f"📤 Publier {offer_or_request}"):
            if pub_title and pub_description:
                st.success(f"{offer_or_request} publiée avec succès!")
            else:
                st.error("Veuillez remplir les champs obligatoires")

# Sidebar network stats
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Statistiques Réseau**")

st.sidebar.metric("Membres connectés", "2,847")
st.sidebar.metric("Posts aujourd'hui", "156")
st.sidebar.metric("Questions résolues", "89%")
st.sidebar.metric("Échanges actifs", "67")

# Footer
st.markdown("---")
st.markdown("**🤝 Réseau Social Agricole** - Communauté collaborative pour l'agriculture moderne")
