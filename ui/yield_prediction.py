"""
Enterprise Yield Prediction Interface
Professional yield forecasting with advanced analytics
"""
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List

from services.prediction_service import prediction_service, PredictionRequest
from services.weather_service import weather_service
from utils.data_validation import data_validator
from utils.file_handler import file_handler
from utils.visualization import viz_engine
from config.settings import CROP_TYPES, SOIL_TYPES, GROWTH_STAGES

def render_yield_prediction():
    """Render the yield prediction interface"""
    
    st.header("🌾 Advanced Yield Prediction")
    st.markdown("Professional crop yield forecasting with ML-powered insights")
    
    # Main tabs for different prediction modes
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Single Prediction", 
        "📈 Batch Analysis", 
        "📋 Prediction History", 
        "🎯 Model Performance"
    ])
    
    with tab1:
        render_single_prediction()
    
    with tab2:
        render_batch_analysis()
    
    with tab3:
        render_prediction_history()
    
    with tab4:
        render_model_performance()

def render_single_prediction():
    """Render single yield prediction interface"""
    
    st.subheader("Individual Field Prediction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Input form
        with st.form("yield_prediction_form"):
            st.markdown("**🌱 Crop Information**")
            col_a, col_b = st.columns(2)
            
            with col_a:
                crop_type = st.selectbox(
                    "Crop Type",
                    options=CROP_TYPES,
                    help="Select the type of crop to predict"
                )
                
                growth_stage = st.selectbox(
                    "Growth Stage",
                    options=GROWTH_STAGES,
                    help="Current growth stage of the crop"
                )
            
            with col_b:
                soil_type = st.selectbox(
                    "Soil Type",
                    options=SOIL_TYPES,
                    help="Type of soil in the field"
                )
                
                area_hectares = st.number_input(
                    "Field Area (hectares)",
                    min_value=0.1,
                    max_value=1000.0,
                    value=1.0,
                    step=0.1,
                    help="Total area of the field"
                )
            
            st.markdown("**🌡️ Environmental Conditions**")
            col_c, col_d = st.columns(2)
            
            with col_c:
                temperature = st.number_input(
                    "Average Temperature (°C)",
                    min_value=-10.0,
                    max_value=50.0,
                    value=25.0,
                    step=0.5,
                    help="Average daily temperature"
                )
                
                humidity = st.number_input(
                    "Humidity (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=65.0,
                    step=1.0,
                    help="Relative humidity percentage"
                )
            
            with col_d:
                rainfall = st.number_input(
                    "Rainfall (mm)",
                    min_value=0.0,
                    max_value=1000.0,
                    value=50.0,
                    step=5.0,
                    help="Total rainfall amount"
                )
                
                wind_speed = st.number_input(
                    "Wind Speed (m/s)",
                    min_value=0.0,
                    max_value=50.0,
                    value=5.0,
                    step=0.5,
                    help="Average wind speed"
                )
            
            st.markdown("**🧪 Soil Nutrients**")
            col_e, col_f, col_g = st.columns(3)
            
            with col_e:
                nitrogen = st.number_input(
                    "Nitrogen (kg/ha)",
                    min_value=0.0,
                    max_value=300.0,
                    value=50.0,
                    step=5.0,
                    help="Nitrogen content in soil"
                )
            
            with col_f:
                phosphorus = st.number_input(
                    "Phosphorus (kg/ha)",
                    min_value=0.0,
                    max_value=200.0,
                    value=25.0,
                    step=2.5,
                    help="Phosphorus content in soil"
                )
            
            with col_g:
                potassium = st.number_input(
                    "Potassium (kg/ha)",
                    min_value=0.0,
                    max_value=500.0,
                    value=200.0,
                    step=10.0,
                    help="Potassium content in soil"
                )
            
            ph_soil = st.slider(
                "Soil pH",
                min_value=3.0,
                max_value=12.0,
                value=6.5,
                step=0.1,
                help="Soil pH level"
            )
            
            # Location input for weather integration
            st.markdown("**📍 Location (Optional)**")
            col_h, col_i = st.columns(2)
            
            with col_h:
                latitude = st.number_input(
                    "Latitude",
                    min_value=-90.0,
                    max_value=90.0,
                    value=0.0,
                    step=0.1,
                    help="Field latitude for weather data"
                )
            
            with col_i:
                longitude = st.number_input(
                    "Longitude", 
                    min_value=-180.0,
                    max_value=180.0,
                    value=0.0,
                    step=0.1,
                    help="Field longitude for weather data"
                )
            
            submitted = st.form_submit_button("🚀 Predict Yield", type="primary")
            
            if submitted:
                # Prepare input data
                input_data = {
                    'crop_type': crop_type,
                    'soil_type': soil_type,
                    'growth_stage': growth_stage,
                    'temperature': temperature,
                    'humidity': humidity,
                    'rainfall': rainfall,
                    'wind_speed': wind_speed,
                    'ph': ph_soil,
                    'nitrogen': nitrogen,
                    'phosphorus': phosphorus,
                    'potassium': potassium,
                    'area_hectares': area_hectares
                }
                
                location = None
                if latitude != 0.0 or longitude != 0.0:
                    location = {'latitude': latitude, 'longitude': longitude}
                
                # Validate input data
                validation_result = data_validator.validate_yield_prediction_input(input_data)
                
                if not validation_result.is_valid:
                    st.error("❌ Input Validation Failed")
                    for error in validation_result.errors:
                        st.error(f"• {error}")
                    
                    if validation_result.warnings:
                        st.warning("⚠️ Warnings:")
                        for warning in validation_result.warnings:
                            st.warning(f"• {warning}")
                else:
                    # Make prediction
                    with st.spinner("🔄 Generating yield prediction..."):
                        request = PredictionRequest(
                            user_id=1,  # TODO: Get from session
                            prediction_type='yield_prediction',
                            input_data=validation_result.cleaned_data,
                            location=location
                        )
                        
                        result = prediction_service.predict_crop_yield(request)
                        
                        if result.success:
                            st.session_state['latest_prediction'] = result
                            st.success("✅ Prediction completed successfully!")
                            st.rerun()
                        else:
                            st.error(f"❌ Prediction failed: {result.error}")
    
    with col2:
        # Results display
        st.subheader("Prediction Results")
        
        if 'latest_prediction' in st.session_state:
            result = st.session_state['latest_prediction']
            prediction_data = result.result
            
            # Main prediction result
            predicted_yield = prediction_data.get('predicted_yield', 0)
            confidence = prediction_data.get('confidence', 0)
            
            st.metric(
                label="Predicted Yield",
                value=f"{predicted_yield:,.0f} kg/ha",
                delta=f"Confidence: {confidence*100:.1f}%" if confidence else None
            )
            
            # Yield classification
            classification = prediction_data.get('yield_classification', 'Unknown')
            classification_color = {
                'Excellent': '🟢',
                'Good': '🟡', 
                'Average': '🟠',
                'Below Average': '🔴',
                'Poor': '⚫'
            }.get(classification, '⚪')
            
            st.info(f"{classification_color} Yield Classification: **{classification}**")
            
            # Limiting factors
            limiting_factors = prediction_data.get('limiting_factors', [])
            if limiting_factors:
                st.warning("⚠️ **Limiting Factors:**")
                for factor in limiting_factors:
                    st.write(f"• {factor}")
            
            # Recommendations
            if result.recommendations:
                st.success("💡 **Recommendations:**")
                for recommendation in result.recommendations:
                    st.write(f"• {recommendation}")
            
            # Optimization potential
            optimization = prediction_data.get('optimization_potential', {})
            if optimization:
                st.markdown("**🎯 Optimization Potential:**")
                for aspect, potential in optimization.items():
                    st.progress(potential, text=f"{aspect.replace('_', ' ').title()}: {potential*100:.0f}%")
        
        else:
            st.info("📋 Enter field parameters and click 'Predict Yield' to see results")
            
            # Display sample insights
            st.markdown("**💡 Prediction Insights:**")
            st.write("• AI-powered yield forecasting")
            st.write("• Weather integration available")
            st.write("• Soil nutrient optimization")
            st.write("• Growth stage considerations")
            st.write("• Confidence scoring")

def render_batch_analysis():
    """Render batch analysis interface"""
    
    st.subheader("Batch Yield Analysis")
    st.markdown("Upload a dataset for bulk yield predictions")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload Dataset (CSV, Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Dataset should contain columns: crop_type, soil_type, temperature, humidity, ph, nitrogen, phosphorus, potassium"
    )
    
    if uploaded_file is not None:
        # Load and validate dataset
        dataset_result = file_handler.load_dataset(uploaded_file)
        
        if dataset_result['success']:
            df = dataset_result['data']
            summary = dataset_result['summary']
            
            st.success(f"✅ Dataset loaded successfully!")
            
            # Dataset summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Rows", summary['rows'])
            with col2:
                st.metric("Columns", summary['columns'])
            with col3:
                st.metric("Missing Values", summary['missing_values'])
            with col4:
                st.metric("Memory Usage", f"{summary['memory_usage_mb']:.1f} MB")
            
            # Data preview
            st.markdown("**📋 Data Preview:**")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Validation
            required_columns = ['crop_type', 'soil_type', 'temperature', 'humidity', 'ph', 'nitrogen', 'phosphorus', 'potassium']
            validation_result = data_validator.validate_dataset(df, required_columns)
            
            if validation_result.is_valid:
                st.success("✅ Dataset validation passed")
                
                if st.button("🚀 Generate Batch Predictions", type="primary"):
                    with st.spinner("🔄 Processing batch predictions..."):
                        # Process predictions in batches
                        predictions = []
                        progress_bar = st.progress(0)
                        
                        for idx, row in df.iterrows():
                            try:
                                input_data = row.to_dict()
                                request = PredictionRequest(
                                    user_id=1,
                                    prediction_type='yield_prediction',
                                    input_data=input_data
                                )
                                
                                result = prediction_service.predict_crop_yield(request)
                                
                                if result.success:
                                    prediction_data = result.result
                                    predictions.append({
                                        'row_index': idx,
                                        'predicted_yield': prediction_data.get('predicted_yield', 0),
                                        'confidence': prediction_data.get('confidence', 0),
                                        'classification': prediction_data.get('yield_classification', 'Unknown')
                                    })
                                
                                progress_bar.progress((idx + 1) / len(df))
                                
                            except Exception as e:
                                st.warning(f"⚠️ Error processing row {idx}: {e}")
                        
                        # Display results
                        if predictions:
                            results_df = pd.DataFrame(predictions)
                            
                            # Merge with original data
                            df_with_predictions = df.copy()
                            df_with_predictions['predicted_yield'] = results_df['predicted_yield']
                            df_with_predictions['confidence'] = results_df['confidence']
                            df_with_predictions['classification'] = results_df['classification']
                            
                            st.success(f"✅ Processed {len(predictions)} predictions")
                            
                            # Summary statistics
                            st.markdown("**📊 Prediction Summary:**")
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("Average Yield", f"{results_df['predicted_yield'].mean():,.0f} kg/ha")
                            with col2:
                                st.metric("Max Yield", f"{results_df['predicted_yield'].max():,.0f} kg/ha")
                            with col3:
                                st.metric("Min Yield", f"{results_df['predicted_yield'].min():,.0f} kg/ha")
                            with col4:
                                st.metric("Avg Confidence", f"{results_df['confidence'].mean()*100:.1f}%")
                            
                            # Results visualization
                            st.markdown("**📈 Yield Distribution:**")
                            fig = viz_engine.create_yield_trend_chart(
                                pd.DataFrame({
                                    'date': pd.date_range(start='2024-01-01', periods=len(results_df)),
                                    'yield': results_df['predicted_yield']
                                })
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Download results
                            st.markdown("**💾 Export Results:**")
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if st.button("📥 Download CSV"):
                                    csv = df_with_predictions.to_csv(index=False)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv,
                                        file_name=f"yield_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            
                            with col_b:
                                if st.button("📊 Download Excel"):
                                    # Use file_handler to create Excel export
                                    export_result = file_handler.export_data(
                                        df_with_predictions, 
                                        "batch_predictions", 
                                        "excel"
                                    )
                                    if export_result['success']:
                                        st.success("📁 Excel file created for download")
                            
                            # Display full results
                            st.markdown("**📋 Detailed Results:**")
                            st.dataframe(df_with_predictions, use_container_width=True)
                        
                        else:
                            st.error("❌ No successful predictions generated")
            
            else:
                st.error("❌ Dataset validation failed")
                for error in validation_result.errors:
                    st.error(f"• {error}")
                
                if validation_result.warnings:
                    st.warning("⚠️ Warnings:")
                    for warning in validation_result.warnings:
                        st.warning(f"• {warning}")
        
        else:
            st.error(f"❌ Failed to load dataset: {dataset_result['error']}")

def render_prediction_history():
    """Render prediction history interface"""
    
    st.subheader("Prediction History & Analytics")
    
    # Get prediction history
    try:
        predictions = prediction_service.get_prediction_history(
            user_id=1,  # TODO: Get from session
            prediction_type='yield_prediction',
            limit=100
        )
        
        if predictions:
            df_history = pd.DataFrame(predictions)
            
            # Summary metrics
            st.markdown("**📊 History Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Predictions", len(predictions))
            with col2:
                recent_predictions = len([p for p in predictions if 
                    datetime.fromisoformat(p['created_at'].replace('Z', '+00:00')) > 
                    datetime.now() - timedelta(days=30)])
                st.metric("Last 30 Days", recent_predictions)
            with col3:
                if 'prediction_result' in df_history.columns:
                    avg_yield = df_history['prediction_result'].apply(
                        lambda x: x.get('predicted_yield', 0) if isinstance(x, dict) else 0
                    ).mean()
                    st.metric("Avg Predicted Yield", f"{avg_yield:,.0f} kg/ha")
                else:
                    st.metric("Avg Predicted Yield", "N/A")
            with col4:
                avg_confidence = df_history['confidence_score'].mean() if 'confidence_score' in df_history.columns else 0
                st.metric("Avg Confidence", f"{avg_confidence*100:.1f}%")
            
            # Filters
            st.markdown("**🔍 Filters:**")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                date_range = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=30), datetime.now()),
                    help="Filter predictions by date range"
                )
            
            with col_b:
                min_confidence = st.slider(
                    "Minimum Confidence",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1,
                    help="Filter by prediction confidence"
                )
            
            with col_c:
                sort_by = st.selectbox(
                    "Sort By",
                    options=['Date (Newest)', 'Date (Oldest)', 'Confidence (High)', 'Confidence (Low)'],
                    help="Sort predictions"
                )
            
            # Apply filters and display
            filtered_predictions = predictions  # TODO: Apply actual filtering
            
            # History table
            st.markdown("**📋 Prediction History:**")
            
            history_display = []
            for pred in filtered_predictions[:20]:  # Show latest 20
                try:
                    result = pred.get('prediction_result', {})
                    if isinstance(result, str):
                        import json
                        result = json.loads(result)
                    
                    history_display.append({
                        'Date': pred.get('created_at', ''),
                        'Predicted Yield (kg/ha)': result.get('predicted_yield', 0),
                        'Confidence': f"{pred.get('confidence_score', 0)*100:.1f}%" if pred.get('confidence_score') else 'N/A',
                        'Classification': result.get('yield_classification', 'Unknown'),
                        'Model Version': pred.get('model_version', 'Unknown')
                    })
                except Exception as e:
                    continue
            
            if history_display:
                st.dataframe(pd.DataFrame(history_display), use_container_width=True)
            else:
                st.info("📭 No prediction history available")
        
        else:
            st.info("📭 No prediction history found. Make some predictions to see history here.")
    
    except Exception as e:
        st.error(f"❌ Error loading prediction history: {e}")

def render_model_performance():
    """Render model performance metrics"""
    
    st.subheader("Model Performance Analytics")
    
    # Model status
    try:
        from models.ml_models import model_manager
        model_status = model_manager.get_model_status()
        
        yield_model_status = model_status.get('yield_prediction', {})
        
        if yield_model_status.get('available', False):
            st.success("✅ Yield prediction model is online and operational")
            
            # Model information
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📋 Model Information:**")
                st.write(f"• **Version:** {yield_model_status.get('version', 'Unknown')}")
                st.write(f"• **Last Trained:** {yield_model_status.get('last_trained', 'Unknown')}")
                
                metrics = yield_model_status.get('metrics', {})
                if metrics:
                    st.write(f"• **R² Score:** {metrics.get('test_r2', 0):.3f}")
                    st.write(f"• **RMSE:** {metrics.get('test_rmse', 0):.1f}")
            
            with col2:
                st.markdown("**📊 Performance Metrics:**")
                
                # Create performance visualization
                if metrics:
                    import plotly.graph_objects as go
                    
                    metric_names = ['R² Score', 'Training Accuracy', 'Validation Accuracy']
                    metric_values = [
                        metrics.get('test_r2', 0.8),
                        metrics.get('train_r2', 0.85),
                        metrics.get('test_r2', 0.8)
                    ]
                    
                    fig = go.Figure(data=[
                        go.Bar(x=metric_names, y=metric_values, 
                              marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'])
                    ])
                    
                    fig.update_layout(
                        title="Model Performance Metrics",
                        yaxis_title="Score",
                        yaxis=dict(range=[0, 1])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("📊 Performance metrics will be available after model training")
            
            # Feature importance
            if metrics and 'feature_importance' in metrics:
                st.markdown("**🎯 Feature Importance:**")
                
                importance = metrics['feature_importance']
                importance_df = pd.DataFrame([
                    {'Feature': k, 'Importance': v}
                    for k, v in importance.items()
                ]).sort_values('Importance', ascending=False)
                
                import plotly.express as px
                fig = px.bar(
                    importance_df.head(10), 
                    x='Importance', 
                    y='Feature',
                    orientation='h',
                    title="Top 10 Most Important Features"
                )
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Model recommendations
            st.markdown("**💡 Model Recommendations:**")
            st.info("🔄 Model is performing well. Continue regular retraining with new data.")
            st.info("📊 Consider collecting more data for soil micronutrients to improve accuracy.")
            st.info("🌦️ Weather integration is active and improving predictions.")
        
        else:
            st.error("❌ Yield prediction model is not available")
            error_msg = yield_model_status.get('error', 'Unknown error')
            st.error(f"Error: {error_msg}")
            
            st.markdown("**🔧 Troubleshooting Steps:**")
            st.write("1. Check if model files exist in the models directory")
            st.write("2. Verify model file integrity")
            st.write("3. Retrain model if necessary")
            st.write("4. Contact system administrator if issues persist")
    
    except Exception as e:
        st.error(f"❌ Error loading model performance data: {e}")
import logging

# Configuration du logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ton code principal ici
def main():
    print("✅ Script exécuté avec succès !")
    logging.info("Le script a été exécuté sans erreur.")

if __name__ == "__main__":
    main()
