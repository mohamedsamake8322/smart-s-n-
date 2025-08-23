import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import urllib.parse

# Configuration de la page
st.set_page_config(page_title="Agro Monitoring", page_icon="🛰️", layout="wide")
st.title("🛰️ Suivi Agro-Climatique Intégré")
st.markdown("### Visualisation du climat, de la végétation et du sol par région")

# 📁 Chargement des fichiers
data_path = "C:/plateforme-agricole-complete-v2/data"
spei_file = os.path.join(data_path, "SPEI_Mali_ADM2_20250821_1546.csv")
modis_file = os.path.join(data_path, "MODIS_VI_Mali_2020_2025_mali_20250821_1503.csv")
soil_file = os.path.join(data_path, "fusion_completesoil.csv")

# Chargement des données
spei_df = pd.read_csv(spei_file)
modis_df = pd.read_csv(modis_file)
soil_df = pd.read_csv(soil_file)

# Création de la colonne 'date' dans SPEI si possible
if {"year", "month"}.issubset(spei_df.columns):
    spei_df["date"] = pd.to_datetime(spei_df["year"].astype(str) + "-" + spei_df["month"].astype(str) + "-01")
else:
    spei_df["date"] = pd.NaT  # fallback

# 🔍 Sélection de la région
region = st.selectbox("📍 Sélectionner une région", spei_df["ADM2_NAME"].dropna().unique())

# 🧭 Onglets
tab1, tab2, tab3 = st.tabs(["🌦 Climat & Végétation", "🧪 Profil de Sol", "🚨 Alerte Agricole"])

# 🌦 Onglet 1 : Climat & Végétation
with tab1:
    st.subheader("🌦 Tendances climatiques et stress végétatif")

    region_spei = spei_df[spei_df["ADM2_NAME"] == region]
    region_modis = modis_df[modis_df["ADM2_NAME"] == region]

    fusion_df = pd.merge(region_spei, region_modis, on=["ADM2_NAME", "year"], how="inner")

    # Graphique SPEI
    fig_spei = go.Figure()
    if "VALUE" in region_spei.columns:
        fig_spei.add_trace(go.Scatter(x=region_spei["date"], y=region_spei["VALUE"], mode='lines', name="SPEI", line=dict(color="orange")))
        fig_spei.update_layout(title=f"SPEI Trend for {region}", xaxis_title="Date", yaxis_title="SPEI Index", yaxis=dict(range=[-3, 3]))
        st.plotly_chart(fig_spei, use_container_width=True)

    # Graphique NDVI vs SPEI
    if "NDVI_mean" in fusion_df.columns and "VALUE" in fusion_df.columns:
        fig_modis = go.Figure()
        fig_modis.add_trace(go.Scatter(x=fusion_df["year"], y=fusion_df["NDVI_mean"], mode="lines", name="NDVI", line=dict(color="green")))
        fig_modis.add_trace(go.Scatter(x=fusion_df["year"], y=fusion_df["VALUE"], mode="lines", name="SPEI", line=dict(color="orange"), yaxis="y2"))
        fig_modis.update_layout(
            title=f"NDVI vs SPEI for {region}",
            xaxis_title="Year",
            yaxis=dict(title="NDVI", range=[0, 1]),
            yaxis2=dict(title="SPEI", overlaying="y", side="right", range=[-3, 3])
        )
        st.plotly_chart(fig_modis, use_container_width=True)

        # Interprétation simplifiée
        latest = fusion_df.sort_values("year").iloc[-1]
        ndvi = latest["NDVI_mean"]
        spei = latest["VALUE"]

        st.markdown("### 🧠 Interprétation")
        if spei < -1 and ndvi < 0.3:
            st.error("🚨 Stress végétatif confirmé : sécheresse + faible NDVI")
            conseil = "🚨 Stress confirmé : sol sec + plantes faibles"
        elif spei < -1:
            st.warning("⚠️ Sécheresse détectée, surveiller la végétation")
            conseil = "⚠️ Sol sec : surveiller les cultures"
        elif ndvi < 0.3:
            st.warning("🌿 NDVI faible - stress végétatif possible")
            conseil = "🌿 Plantes faibles : vérifier l'irrigation"
        else:
            st.success("✅ Conditions normales")
            conseil = "✅ Tout va bien : bonne humidité et végétation"

        # Résumé producteur + WhatsApp
        st.markdown("### 🔊 Résumé simplifié pour producteurs")
        st.markdown(conseil)
        message = f"🌿 Région : {region}\nNDVI : {ndvi:.2f}\nSPEI : {spei:.2f}\n{conseil}"
        encoded_msg = urllib.parse.quote(message)
        whatsapp_url = f"https://wa.me/?text={encoded_msg}"
        st.markdown(f"[📱 Envoyer sur WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

# 🧪 Onglet 2 : Profil de Sol
with tab2:
    st.subheader("🧪 Propriétés du sol")

    soil_region = soil_df[soil_df["ph_adm2_name"] == region]
    if not soil_region.empty:
        row = soil_region.iloc[0]
        ph = row.get("ph_mean_0_20_mean", None)
        clay = row.get("claycontent_mean_0_20_mean", None)
        carbon = row.get("carbonorganic_mean_0_20_mean", None)

        col1, col2, col3 = st.columns(3)
        col1.metric("pH (0–20cm)", f"{ph:.2f}" if ph else "N/A")
        col2.metric("Argile (%)", f"{clay:.1f}" if clay else "N/A")
        col3.metric("Carbone organique", f"{carbon:.2f}" if carbon else "N/A")

        st.markdown("### ⚠️ Alertes sol")
        if ph and ph < 5.5:
            st.warning("🧪 Sol acide - risque pour certaines cultures")
        if clay and clay > 40:
            st.warning("🧱 Sol très argileux - drainage lent")
        if carbon and carbon < 1.0:
            st.warning("🌱 Faible matière organique - fertilité limitée")
        if (
            (ph and ph >= 5.5) and
            (clay and clay <= 40) and
            (carbon and carbon >= 1.0)
        ):
            st.success("✅ Sol favorable à la culture")

# 🚨 Onglet 3 : Alerte Agricole
with tab3:
    st.subheader("🚨 Synthèse des risques agricoles")

    alertes = []
    if spei < -1 and ndvi < 0.3:
        alertes.append("🌵 Sécheresse + stress végétatif")
    if ph and ph < 5.5:
        alertes.append("🧪 Sol acide")
    if clay and clay > 40:
        alertes.append("🧱 Sol très argileux")
    if carbon and carbon < 1.0:
        alertes.append("🌱 Faible fertilité")

    if alertes:
        st.error("🚨 Risques détectés :")
        for a in alertes:
            st.markdown(f"- {a}")
    else:
        st.success("✅ Aucun risque majeur détecté")

    st.markdown("### 📱 Résumé producteur")
    diagnostic = "\n".join(alertes) if alertes else "✅ Conditions favorables"
    message_final = f"📍 Région : {region}\n{diagnostic}"
    st.markdown(message_final)

    encoded_final = urllib.parse.quote(message_final)
    whatsapp_final = f"https://wa.me/?text={encoded_final}"
    st.markdown(f"[📤 Envoyer ce diagnostic sur WhatsApp]({whatsapp_final})", unsafe_allow_html=True)
