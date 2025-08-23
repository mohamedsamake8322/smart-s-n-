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
soil_file = os.path.join(data_path, "fusion_SMAP_SoilGrids.csv")

spei_df = pd.read_csv(spei_file, parse_dates=["date"])
modis_df = pd.read_csv(modis_file, parse_dates=["date"])
soil_df = pd.read_csv(soil_file)

# 🔍 Sélection de la région
region = st.selectbox("📍 Sélectionner une région", spei_df["ADM2_NAME"].unique())

# 🧭 Onglets
tab1, tab2, tab3 = st.tabs(["🌦 Climat & Végétation", "🧪 Profil de Sol", "🚨 Alerte Agricole"])

# 🌦 Onglet 1 : Climat & Végétation
with tab1:
    st.subheader("🌦 Tendances climatiques et stress végétatif")

    region_spei = spei_df[spei_df["ADM2_NAME"] == region]
    region_modis = modis_df[modis_df["ADM2_NAME"] == region]
    fusion_df = pd.merge(region_spei, region_modis, on=["ADM2_NAME", "date"], how="inner")

    # Graphique SPEI
    fig_spei = go.Figure()
    for spei_col, color in zip(["SPEI_03", "SPEI_06", "SPEI_12"], ["orange", "green", "blue"]):
        fig_spei.add_trace(go.Scatter(x=region_spei["date"], y=region_spei[spei_col], mode='lines', name=spei_col, line=dict(color=color)))
    fig_spei.update_layout(title=f"SPEI Trends for {region}", xaxis_title="Date", yaxis_title="SPEI Index", yaxis=dict(range=[-3, 3]))
    st.plotly_chart(fig_spei, use_container_width=True)

    # Graphique NDVI vs SPEI_03
    fig_modis = go.Figure()
    fig_modis.add_trace(go.Scatter(x=fusion_df["date"], y=fusion_df["NDVI"], mode="lines", name="NDVI", line=dict(color="green")))
    fig_modis.add_trace(go.Scatter(x=fusion_df["date"], y=fusion_df["SPEI_03"], mode="lines", name="SPEI_03", line=dict(color="orange"), yaxis="y2"))
    fig_modis.update_layout(
        title=f"NDVI vs SPEI_03 for {region}",
        xaxis_title="Date",
        yaxis=dict(title="NDVI", range=[0, 1]),
        yaxis2=dict(title="SPEI_03", overlaying="y", side="right", range=[-3, 3])
    )
    st.plotly_chart(fig_modis, use_container_width=True)

    # Interprétation simplifiée
    latest = fusion_df.sort_values("date").iloc[-1]
    ndvi = latest["NDVI"]
    spei = latest["SPEI_03"]

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
    message = f"🌿 Région : {region}\nNDVI : {ndvi:.2f}\nSPEI_03 : {spei:.2f}\n{conseil}"
    encoded_msg = urllib.parse.quote(message)
    whatsapp_url = f"https://wa.me/?text={encoded_msg}"
    st.markdown(f"[📱 Envoyer sur WhatsApp]({whatsapp_url})", unsafe_allow_html=True)

# 🧪 Onglet 2 : Profil de Sol
with tab2:
    st.subheader("🧪 Propriétés du sol")
    region_soil = soil_df[soil_df["ADM2_NAME"] == region].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Humidité SMAP", f"{region_soil['SMAP_moisture']:.2f} %")
    col2.metric("pH", f"{region_soil['pH']:.1f}")
    col3.metric("Texture dominante", region_soil["texture_class"])
    col4.metric("Densité apparente", f"{region_soil['bulk_density']:.2f} g/cm³")

    st.markdown("### ⚠️ Alertes sol")
    if region_soil["pH"] < 5.5:
        st.warning("🧪 Sol acide - risque pour certaines cultures")
    if region_soil["bulk_density"] > 1.6:
        st.warning("🧱 Sol compact - faible aération racinaire")
    if region_soil["SMAP_moisture"] < 15:
        st.warning("💧 Faible humidité - faible rétention d'eau")
    if (
        region_soil["pH"] >= 5.5 and
        region_soil["bulk_density"] <= 1.6 and
        region_soil["SMAP_moisture"] >= 15
    ):
        st.success("✅ Sol favorable à la culture")

# 🚨 Onglet 3 : Alerte Agricole
with tab3:
    st.subheader("🚨 Synthèse des risques agricoles")

    st.markdown("### 🧠 Diagnostic combiné")
    alertes = []
    if spei < -1 and ndvi < 0.3:
        alertes.append("🌵 Sécheresse + stress végétatif")
    if region_soil["pH"] < 5.5:
        alertes.append("🧪 Sol acide")
    if region_soil["bulk_density"] > 1.6:
        alertes.append("🧱 Sol compact")
    if region_soil["SMAP_moisture"] < 15:
        alertes.append("💧 Faible humidité")

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
