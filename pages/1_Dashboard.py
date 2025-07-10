import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.visualization import create_overview_charts, create_trend_analysis
from utils.data_processing import get_sample_agricultural_data
from config.translator import translate_text


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Agricultural Dashboard")
st.markdown("### Comprehensive overview of your agricultural operations")

# Check if data exists in session state
if 'agricultural_data' not in st.session_state:
    st.warning("No data available. Please upload data first or use sample data for demonstration.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Upload Data", use_container_width=True):
            st.switch_page("pages/5_Data_Upload.py")

    with col2:
        if st.button("Use Sample Data", use_container_width=True):
            # This would normally load real data, but for demo we'll create structure
            st.session_state.agricultural_data = get_sample_agricultural_data()
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
        st.metric(
            label="Average Yield (tons/ha)",
            value=f"{avg_yield:.2f}",
            delta=f"{(avg_yield - data['yield'].median()):.2f}"
        )
    else:
        st.metric("Average Yield", "--", help="Yield data not available")

with col2:
    if 'area' in data.columns:
        total_area = data['area'].sum()
        st.metric(
            label="Total Area (hectares)",
            value=f"{total_area:.1f}",
            help="Total cultivated area"
        )
    else:
        st.metric("Total Area", "--", help="Area data not available")

with col3:
    if 'crop_type' in data.columns:
        crop_diversity = data['crop_type'].nunique()
        st.metric(
            label="Crop Varieties",
            value=crop_diversity,
            help="Number of different crops grown"
        )
    else:
        st.metric("Crop Varieties", "--", help="Crop data not available")

with col4:
    if 'profit' in data.columns:
        total_profit = data['profit'].sum()
        st.metric(
            label="Total Profit ($)",
            value=f"${total_profit:,.0f}",
            delta=f"{(total_profit/len(data)):.0f} per record"
        )
    else:
        st.metric("Total Profit", "--", help="Profit data not available")

# Charts section
st.markdown("---")
st.subheader("Data Visualization")

# Create tabs for different chart types
tab1, tab2, tab3, tab4 = st.tabs(["Yield Analysis", "Crop Distribution", "Seasonal Trends", "Performance Metrics"])

with tab1:
    col1, col2 = st.columns(2)

    with col1:
        if 'yield' in data.columns and 'crop_type' in data.columns:
            fig_yield = px.box(
                data,
                x='crop_type',
                y='yield',
                title="Yield Distribution by Crop Type",
                labels={'yield': 'Yield (tons/ha)', 'crop_type': 'Crop Type'}
            )
            fig_yield.update_layout(height=400)
            st.plotly_chart(fig_yield, use_container_width=True)
        else:
            st.error("Yield or crop type data not available for visualization")

    with col2:
        if 'yield' in data.columns:
            fig_hist = px.histogram(
                data,
                x='yield',
                nbins=20,
                title="Yield Distribution Histogram",
                labels={'yield': 'Yield (tons/ha)', 'count': 'Frequency'}
            )
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.error("Yield data not available for histogram")

with tab2:
    if 'crop_type' in data.columns:
        crop_counts = data['crop_type'].value_counts()

        col1, col2 = st.columns(2)

        with col1:
            fig_pie = px.pie(
                values=crop_counts.values,
                names=crop_counts.index,
                title="Crop Distribution"
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            fig_bar = px.bar(
                x=crop_counts.index,
                y=crop_counts.values,
                title="Crop Count by Type",
                labels={'x': 'Crop Type', 'y': 'Count'}
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.error("Crop type data not available for distribution analysis")

with tab3:
    if 'date' in data.columns or 'season' in data.columns:
        st.info("Seasonal trend analysis requires date/season data in your dataset")

        # If we have date data, create time series
        if 'date' in data.columns and 'yield' in data.columns:
            try:
                data['date'] = pd.to_datetime(data['date'])
                monthly_yield = data.groupby(data['date'].dt.to_period('M'))['yield'].mean().reset_index()
                monthly_yield['date'] = monthly_yield['date'].dt.to_timestamp()

                fig_trend = px.line(
                    monthly_yield,
                    x='date',
                    y='yield',
                    title="Monthly Yield Trends",
                    labels={'date': 'Date', 'yield': 'Average Yield (tons/ha)'}
                )
                fig_trend.update_layout(height=400)
                st.plotly_chart(fig_trend, use_container_width=True)
            except Exception as e:
                st.error(f"Error processing date data: {str(e)}")
        else:
            st.warning("Date column not found or not properly formatted for trend analysis")
    else:
        st.warning("No date or season data available for trend analysis")

with tab4:
    if 'yield' in data.columns and 'area' in data.columns:
        col1, col2 = st.columns(2)

        with col1:
            # Scatter plot of yield vs area
            fig_scatter = px.scatter(
                data,
                x='area',
                y='yield',
                color='crop_type' if 'crop_type' in data.columns else None,
                title="Yield vs Area Relationship",
                labels={'area': 'Area (hectares)', 'yield': 'Yield (tons/ha)'}
            )
            fig_scatter.update_layout(height=400)
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col2:
            # Correlation analysis
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 1:
                corr_matrix = data[numeric_cols].corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    title="Correlation Matrix",
                    color_continuous_scale='RdBu_r'
                )
                fig_corr.update_layout(height=400)
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("Insufficient numeric columns for correlation analysis")
    else:
        st.error("Yield and area data required for performance metrics")

# Data summary section
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

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Export Dashboard Report", use_container_width=True):
        st.info("Report export functionality would be implemented here")

with col2:
    if st.button("📈 Export Charts", use_container_width=True):
        st.info("Chart export functionality would be implemented here")

with col3:
    if st.button("📋 Export Data Summary", use_container_width=True):
        st.info("Data summary export functionality would be implemented here")
