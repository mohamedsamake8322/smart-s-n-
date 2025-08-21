import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.visualization import create_overview_charts, create_trend_analysis
from utils.data_processing import load_and_merge_indicators, get_sample_agricultural_data

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Agricultural Dashboard")
st.markdown("### Comprehensive overview of your agricultural operations")

# Load data if not already in session
if 'agricultural_data' not in st.session_state:
    st.warning("No data available. Please upload data, use sample data, or load Mali indicators.")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Upload Data", use_container_width=True):
            st.switch_page("pages/5_Data_Upload.py")

    with col2:
        if st.button("Use Sample Data", use_container_width=True):
            st.session_state.agricultural_data = get_sample_agricultural_data()
            st.rerun()

    with col3:
        if st.button("Load Mali Indicators", use_container_width=True):
            st.session_state.agricultural_data = load_and_merge_indicators(
                base_path=r"C:\plateforme-agricole-complete-v2\data"
            )
            st.rerun()

    st.stop()

# Main dashboard content
data = st.session_state.agricultural_data

# Key metrics row
st.subheader("Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if 'yield' in data.columns:
        avg_yield = data['yield'].mean()
        st.metric("Average Yield (tons/ha)", f"{avg_yield:.2f}", delta=f"{(avg_yield - data['yield'].median()):.2f}")
    else:
        st.metric("Average Yield", "--", help="Yield data not available")

with col2:
    if 'area' in data.columns:
        total_area = data['area'].sum()
        st.metric("Total Area (hectares)", f"{total_area:.1f}", help="Total cultivated area")
    else:
        st.metric("Total Area", "--", help="Area data not available")

with col3:
    if 'crop_type' in data.columns:
        crop_diversity = data['crop_type'].nunique()
        st.metric("Crop Varieties", crop_diversity, help="Number of different crops grown")
    else:
        st.metric("Crop Varieties", "--", help="Crop data not available")

with col4:
    if 'profit' in data.columns:
        total_profit = data['profit'].sum()
        st.metric("Total Profit ($)", f"${total_profit:,.0f}", delta=f"{(total_profit/len(data)):.0f} per record")
    else:
        st.metric("Total Profit", "--", help="Profit data not available")

# Charts section
st.markdown("---")
st.subheader("Data Visualization")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Yield Analysis", "Crop Distribution", "Seasonal Trends", "Performance Metrics",
    "NDVI/EVI Trends", "SPEI Drought Index", "Soil Properties"
])

with tab1:
    if 'yield' in data.columns and 'crop_type' in data.columns:
        fig_yield = px.box(data, x='crop_type', y='yield', title="Yield Distribution by Crop Type")
        st.plotly_chart(fig_yield, use_container_width=True)

with tab2:
    if 'crop_type' in data.columns:
        crop_counts = data['crop_type'].value_counts()
        fig_pie = px.pie(values=crop_counts.values, names=crop_counts.index, title="Crop Distribution")
        fig_bar = px.bar(x=crop_counts.index, y=crop_counts.values, title="Crop Count by Type")
        st.plotly_chart(fig_pie, use_container_width=True)
        st.plotly_chart(fig_bar, use_container_width=True)

with tab3:
    if 'date' in data.columns and 'yield' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        monthly_yield = data.groupby(data['date'].dt.to_period('M'))['yield'].mean().reset_index()
        monthly_yield['date'] = monthly_yield['date'].dt.to_timestamp()
        fig_trend = px.line(monthly_yield, x='date', y='yield', title="Monthly Yield Trends")
        st.plotly_chart(fig_trend, use_container_width=True)

with tab4:
    if 'yield' in data.columns and 'area' in data.columns:
        fig_scatter = px.scatter(data, x='area', y='yield', color='crop_type', title="Yield vs Area")
        st.plotly_chart(fig_scatter, use_container_width=True)

        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr_matrix = data[numeric_cols].corr()
            fig_corr = px.imshow(corr_matrix, title="Correlation Matrix", color_continuous_scale='RdBu_r')
            st.plotly_chart(fig_corr, use_container_width=True)

with tab5:
    if 'ndvi' in data.columns and 'ADM2_NAME' in data.columns:
        fig_ndvi = px.line(data, x='date', y='ndvi', color='ADM2_NAME', title="NDVI Trends by Region")
        st.plotly_chart(fig_ndvi, use_container_width=True)

with tab6:
    if 'spei_03' in data.columns and 'ADM2_NAME' in data.columns:
        fig_spei = px.line(data, x='date', y='spei_03', color='ADM2_NAME', title="SPEI-03 Drought Index")
        st.plotly_chart(fig_spei, use_container_width=True)

with tab7:
    if 'soil_sand' in data.columns and 'soil_clay' in data.columns:
        fig_soil = px.scatter(
            data,
            x='soil_sand',
            y='soil_clay',
            color='ADM2_NAME',
            size='smap_moisture',
            title="Soil Texture vs Moisture",
            labels={'soil_sand': 'Sand (%)', 'soil_clay': 'Clay (%)', 'smap_moisture': 'Moisture'}
        )
        st.plotly_chart(fig_soil, use_container_width=True)

# Data summary
st.markdown("---")
st.subheader("Data Summary")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Dataset Overview:**")
    st.write(f"- Total records: {len(data)}")
    st.write(f"- Columns: {len(data.columns)}")
    st.write(f"- Data types: {data.dtypes.value_counts().to_dict()}")

with col2:
    st.markdown("**Data Quality:**")
    missing_data = data.isnull().sum()
    if missing_data.sum() > 0:
        st.warning("Missing data detected:")
        for col, missing in missing_data[missing_data > 0].items():
            st.write(f"- {col}: {missing} missing values")
    else:
        st.success("No missing data detected")

# Export options
st.markdown("---")
st.subheader("Export Options")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📊 Export Dashboard Report", use_container_width=True):
        st.info("Report export functionality would be implemented here")

with col2:
    if st.button("📈 Export Charts", use_container_width=True):
        st.info("Chart export functionality would be implemented here")

with col3:
    if st.button("📋 Export Data Summary", use_container_width=True):
        st.info("Data summary export functionality would be implemented here")

with col4:
    if st.button("📁 Export Excel File", use_container_width=True):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, index=False, sheet_name='Agricultural Data')
        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="agricultural_dashboard_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

