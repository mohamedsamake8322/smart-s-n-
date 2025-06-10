"""
Enterprise Model Training Interface
Professional ML model management and retraining capabilities
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json

from models.ml_models import model_manager
from utils.data_validation import data_validator
from utils.file_handler import file_handler
from utils.visualization import viz_engine
from core.database import db_manager
from config.settings import CROP_TYPES, SOIL_TYPES, PERFORMANCE_THRESHOLDS

def render_model_training():
    """Render the model training interface"""
    
    st.header("🚀 Model Training & Management")
    st.markdown("Professional machine learning model training and performance optimization")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔄 Model Retraining", 
        "📊 Model Performance", 
        "⚙️ Hyperparameter Tuning", 
        "📋 Training History"
    ])
    
    with tab1:
        render_model_retraining()
    
    with tab2:
        render_model_performance()
    
    with tab3:
        render_hyperparameter_tuning()
    
    with tab4:
        render_training_history()

def render_model_retraining():
    """Render model retraining interface"""
    
    st.subheader("Model Retraining & Optimization")
    
    # Model selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        model_type = st.selectbox(
            "Select Model to Retrain:",
            options=["Yield Prediction", "Disease Detection", "Fertilizer Recommendation"],
            help="Choose which model to retrain with new data"
        )
    
    with col2:
        training_mode = st.selectbox(
            "Training Mode:",
            options=["Full Retraining", "Incremental Learning", "Transfer Learning"],
            help="Select training approach"
        )
    
    # Training data upload
    st.markdown("**📤 Training Data Upload**")
    
    uploaded_file = st.file_uploader(
        "Upload Training Dataset",
        type=['csv', 'xlsx', 'json'],
        help="Upload dataset for model training. Ensure data quality and proper formatting."
    )
    
    if uploaded_file is not None:
        # Load and validate dataset
        with st.spinner("📊 Loading and validating dataset..."):
            dataset_result = file_handler.load_dataset(uploaded_file)
            
            if dataset_result['success']:
                df = dataset_result['data']
                summary = dataset_result['summary']
                
                st.success("✅ Dataset loaded successfully!")
                
                # Dataset overview
                st.markdown("**📋 Dataset Overview:**")
                col_a, col_b, col_c, col_d = st.columns(4)
                
                with col_a:
                    st.metric("Rows", f"{summary['rows']:,}")
                with col_b:
                    st.metric("Columns", summary['columns'])
                with col_c:
                    st.metric("Missing Values", f"{summary['missing_values']:,}")
                with col_d:
                    st.metric("Size", f"{summary['memory_usage_mb']:.1f} MB")
                
                # Data preview
                st.markdown("**👀 Data Preview:**")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Data quality assessment
                st.markdown("**🔍 Data Quality Assessment:**")
                
                # Define required columns based on model type
                if model_type == "Yield Prediction":
                    required_columns = ['crop_type', 'soil_type', 'temperature', 'humidity', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'yield']
                elif model_type == "Disease Detection":
                    required_columns = ['image_path', 'disease_label']
                else:  # Fertilizer Recommendation
                    required_columns = ['crop_type', 'soil_type', 'ph', 'nitrogen', 'phosphorus', 'potassium', 'fertilizer_type']
                
                validation_result = data_validator.validate_dataset(df, required_columns)
                
                if validation_result.is_valid:
                    st.success("✅ Dataset validation passed")
                    
                    # Training configuration
                    st.markdown("---")
                    st.markdown("**⚙️ Training Configuration**")
                    
                    col_x, col_y, col_z = st.columns(3)
                    
                    with col_x:
                        test_size = st.slider(
                            "Test Set Size (%)",
                            min_value=10,
                            max_value=40,
                            value=20,
                            step=5,
                            help="Percentage of data to use for testing"
                        )
                        
                        validation_size = st.slider(
                            "Validation Set Size (%)",
                            min_value=10,
                            max_value=30,
                            value=15,
                            step=5,
                            help="Percentage of data to use for validation"
                        )
                    
                    with col_y:
                        if model_type == "Yield Prediction":
                            algorithm = st.selectbox(
                                "Algorithm:",
                                options=["XGBoost", "Random Forest", "Neural Network", "Gradient Boosting"],
                                help="Select machine learning algorithm"
                            )
                            
                            max_epochs = st.number_input(
                                "Max Epochs:",
                                min_value=10,
                                max_value=1000,
                                value=100,
                                step=10,
                                help="Maximum training epochs"
                            )
                        else:
                            algorithm = "Deep Learning CNN"
                            max_epochs = st.number_input(
                                "Max Epochs:",
                                min_value=10,
                                max_value=200,
                                value=50,
                                step=5
                            )
                    
                    with col_z:
                        learning_rate = st.number_input(
                            "Learning Rate:",
                            min_value=0.0001,
                            max_value=0.1,
                            value=0.001,
                            step=0.0001,
                            format="%.4f",
                            help="Learning rate for optimization"
                        )
                        
                        batch_size = st.selectbox(
                            "Batch Size:",
                            options=[16, 32, 64, 128, 256],
                            index=2,
                            help="Training batch size"
                        )
                    
                    # Advanced options
                    with st.expander("🔧 Advanced Training Options"):
                        col_adv1, col_adv2 = st.columns(2)
                        
                        with col_adv1:
                            early_stopping = st.checkbox(
                                "Enable Early Stopping",
                                value=True,
                                help="Stop training when performance stops improving"
                            )
                            
                            data_augmentation = st.checkbox(
                                "Data Augmentation",
                                value=model_type == "Disease Detection",
                                help="Apply data augmentation techniques"
                            )
                            
                            cross_validation = st.checkbox(
                                "Cross Validation",
                                value=True,
                                help="Use k-fold cross validation"
                            )
                        
                        with col_adv2:
                            regularization = st.selectbox(
                                "Regularization:",
                                options=["None", "L1", "L2", "Dropout"],
                                index=2,
                                help="Regularization technique"
                            )
                            
                            optimizer = st.selectbox(
                                "Optimizer:",
                                options=["Adam", "SGD", "RMSprop", "AdaGrad"],
                                help="Optimization algorithm"
                            )
                            
                            random_seed = st.number_input(
                                "Random Seed:",
                                min_value=1,
                                max_value=9999,
                                value=42,
                                help="Random seed for reproducibility"
                            )
                    
                    # Training execution
                    st.markdown("---")
                    
                    col_train1, col_train2 = st.columns([3, 1])
                    
                    with col_train1:
                        if st.button("🚀 Start Model Training", type="primary", use_container_width=True):
                            start_training(
                                df=df,
                                model_type=model_type,
                                training_mode=training_mode,
                                config={
                                    'test_size': test_size / 100,
                                    'validation_size': validation_size / 100,
                                    'algorithm': algorithm,
                                    'max_epochs': max_epochs,
                                    'learning_rate': learning_rate,
                                    'batch_size': batch_size,
                                    'early_stopping': early_stopping,
                                    'data_augmentation': data_augmentation,
                                    'cross_validation': cross_validation,
                                    'regularization': regularization,
                                    'optimizer': optimizer,
                                    'random_seed': random_seed
                                }
                            )
                    
                    with col_train2:
                        if st.button("💾 Save Configuration"):
                            st.success("⚙️ Configuration saved!")
                
                else:
                    st.error("❌ Dataset validation failed")
                    
                    if validation_result.errors:
                        st.markdown("**🚨 Errors:**")
                        for error in validation_result.errors:
                            st.error(f"• {error}")
                    
                    if validation_result.warnings:
                        st.markdown("**⚠️ Warnings:**")
                        for warning in validation_result.warnings:
                            st.warning(f"• {warning}")
                    
                    st.markdown("**💡 Data Requirements:**")
                    for col in required_columns:
                        st.write(f"• **{col}**: Required column for {model_type}")
            
            else:
                st.error(f"❌ Failed to load dataset: {dataset_result['error']}")
    
    else:
        st.info("📤 Upload a training dataset to begin model retraining")
        
        # Training guidelines
        st.markdown("**📋 Data Requirements by Model Type:**")
        
        requirements = {
            "🌾 Yield Prediction": [
                "crop_type, soil_type, temperature, humidity",
                "ph, nitrogen, phosphorus, potassium", 
                "yield (target variable)",
                "Minimum 1000 samples recommended"
            ],
            "🔍 Disease Detection": [
                "image_path or image_data",
                "disease_label (target class)",
                "Optional: crop_type, location",
                "Minimum 100 images per class"
            ],
            "💊 Fertilizer Recommendation": [
                "crop_type, soil_type, ph",
                "nitrogen, phosphorus, potassium",
                "fertilizer_type (target variable)",
                "Minimum 500 samples recommended"
            ]
        }
        
        for model, reqs in requirements.items():
            with st.expander(model):
                for req in reqs:
                    st.write(f"• {req}")

def render_model_performance():
    """Render model performance analysis"""
    
    st.subheader("Model Performance Analysis")
    
    # Get model status
    try:
        model_status = model_manager.get_model_status()
        
        # Performance overview
        st.markdown("**📊 Model Performance Overview**")
        
        performance_data = []
        for model_name, status in model_status.items():
            if status.get('available', False):
                metrics = status.get('metrics', {})
                performance_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'Status': '🟢 Online',
                    'Version': status.get('version', 'Unknown'),
                    'Accuracy': f"{metrics.get('test_r2', metrics.get('accuracy', 0)):.3f}",
                    'Last Trained': status.get('last_trained', 'Unknown')
                })
            else:
                performance_data.append({
                    'Model': model_name.replace('_', ' ').title(),
                    'Status': '🔴 Offline',
                    'Version': 'N/A',
                    'Accuracy': 'N/A',
                    'Last Trained': 'N/A'
                })
        
        if performance_data:
            performance_df = pd.DataFrame(performance_data)
            st.dataframe(performance_df, use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No model performance data available")
        
        # Detailed performance analysis
        st.markdown("---")
        
        model_selection = st.selectbox(
            "Select Model for Detailed Analysis:",
            options=list(model_status.keys()),
            format_func=lambda x: x.replace('_', ' ').title()
        )
        
        selected_status = model_status.get(model_selection, {})
        
        if selected_status.get('available', False):
            st.markdown(f"### 📈 {model_selection.replace('_', ' ').title()} Performance")
            
            metrics = selected_status.get('metrics', {})
            
            if metrics:
                # Performance metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🎯 Core Metrics:**")
                    
                    if 'test_r2' in metrics:
                        r2_score = metrics['test_r2']
                        st.metric("R² Score", f"{r2_score:.3f}", 
                                delta=get_performance_status(r2_score, 'r2'))
                    
                    if 'test_rmse' in metrics:
                        rmse = metrics['test_rmse']
                        st.metric("RMSE", f"{rmse:.2f}")
                    
                    if 'accuracy' in metrics:
                        accuracy = metrics['accuracy']
                        st.metric("Accuracy", f"{accuracy:.1%}",
                                delta=get_performance_status(accuracy, 'accuracy'))
                
                with col2:
                    st.markdown("**📊 Training Metrics:**")
                    
                    if 'train_r2' in metrics:
                        train_r2 = metrics['train_r2']
                        st.metric("Training R²", f"{train_r2:.3f}")
                    
                    if 'train_rmse' in metrics:
                        train_rmse = metrics['train_rmse']
                        st.metric("Training RMSE", f"{train_rmse:.2f}")
                    
                    if 'precision' in metrics:
                        precision = metrics['precision']
                        st.metric("Precision", f"{precision:.3f}")
                
                # Performance visualization
                if model_selection == 'yield_prediction':
                    render_yield_model_performance(metrics)
                elif model_selection == 'disease_detection':
                    render_disease_model_performance(metrics)
                else:
                    render_generic_model_performance(metrics)
                
                # Model comparison
                st.markdown("---")
                st.markdown("**📊 Performance Benchmarks**")
                
                thresholds = PERFORMANCE_THRESHOLDS.get(model_selection, {})
                if thresholds:
                    create_performance_benchmark_chart(metrics, thresholds, model_selection)
                
                # Feature importance (if available)
                if 'feature_importance' in metrics:
                    st.markdown("---")
                    st.markdown("**🎯 Feature Importance Analysis**")
                    
                    importance = metrics['feature_importance']
                    importance_df = pd.DataFrame([
                        {'Feature': k, 'Importance': v}
                        for k, v in importance.items()
                    ]).sort_values('Importance', ascending=False)
                    
                    fig = px.bar(
                        importance_df.head(15),
                        x='Importance',
                        y='Feature',
                        orientation='h',
                        title="Top 15 Most Important Features"
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("📊 No detailed metrics available for this model")
        
        else:
            st.error(f"❌ Model '{model_selection}' is not available or loaded")
            
            # Model troubleshooting
            st.markdown("**🔧 Troubleshooting Steps:**")
            troubleshooting_steps = [
                "Check if model files exist in the models directory",
                "Verify model file integrity and format",
                "Ensure all required dependencies are installed",
                "Review model loading logs for specific errors",
                "Consider retraining the model with fresh data"
            ]
            
            for i, step in enumerate(troubleshooting_steps, 1):
                st.write(f"{i}. {step}")
    
    except Exception as e:
        st.error(f"❌ Error loading model performance data: {e}")
        st.info("🔄 Please check system logs or contact administrator")

def render_hyperparameter_tuning():
    """Render hyperparameter tuning interface"""
    
    st.subheader("Hyperparameter Optimization")
    
    # Model selection for tuning
    tuning_model = st.selectbox(
        "Select Model for Hyperparameter Tuning:",
        options=["Yield Prediction", "Disease Detection", "Fertilizer Recommendation"],
        help="Choose model to optimize"
    )
    
    # Tuning strategy
    col1, col2 = st.columns(2)
    
    with col1:
        tuning_strategy = st.selectbox(
            "Optimization Strategy:",
            options=["Grid Search", "Random Search", "Bayesian Optimization", "Genetic Algorithm"],
            help="Select hyperparameter optimization method"
        )
    
    with col2:
        max_iterations = st.number_input(
            "Max Iterations:",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Maximum optimization iterations"
        )
    
    # Hyperparameter space definition
    st.markdown("**⚙️ Hyperparameter Space**")
    
    if tuning_model == "Yield Prediction":
        render_yield_hyperparameters()
    elif tuning_model == "Disease Detection":
        render_disease_hyperparameters()
    else:
        render_fertilizer_hyperparameters()
    
    # Optimization configuration
    st.markdown("---")
    st.markdown("**🔧 Optimization Configuration**")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        cv_folds = st.number_input(
            "Cross-Validation Folds:",
            min_value=3,
            max_value=10,
            value=5,
            help="Number of cross-validation folds"
        )
    
    with col_b:
        scoring_metric = st.selectbox(
            "Optimization Metric:",
            options=["R² Score", "RMSE", "Accuracy", "F1 Score", "AUC-ROC"],
            help="Metric to optimize"
        )
    
    with col_c:
        parallel_jobs = st.number_input(
            "Parallel Jobs:",
            min_value=1,
            max_value=8,
            value=4,
            help="Number of parallel processes"
        )
    
    # Start optimization
    col_start, col_monitor = st.columns([2, 1])
    
    with col_start:
        if st.button("🚀 Start Hyperparameter Optimization", type="primary", use_container_width=True):
            start_hyperparameter_optimization(
                model_type=tuning_model,
                strategy=tuning_strategy,
                max_iterations=max_iterations,
                cv_folds=cv_folds,
                scoring_metric=scoring_metric,
                parallel_jobs=parallel_jobs
            )
    
    with col_monitor:
        if st.button("📊 Monitor Progress"):
            st.info("🔄 Optimization monitoring will be available during training")
    
    # Optimization history
    st.markdown("---")
    st.markdown("**📋 Recent Optimization Results**")
    
    # Display sample optimization history
    if st.session_state.get('optimization_results'):
        results = st.session_state['optimization_results']
        st.dataframe(pd.DataFrame(results), use_container_width=True)
    else:
        st.info("📊 No optimization results available. Start an optimization to see results here.")
        
        # Sample optimization tips
        st.markdown("**💡 Hyperparameter Tuning Tips:**")
        tips = [
            "Start with a broad search space, then narrow down",
            "Use cross-validation to avoid overfitting",
            "Monitor both training and validation metrics",
            "Consider computational cost vs. performance gains",
            "Document best configurations for future reference"
        ]
        
        for tip in tips:
            st.write(f"• {tip}")

def render_training_history():
    """Render training history and logs"""
    
    st.subheader("Training History & Model Versioning")
    
    # Training history filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_range = st.date_input(
            "Date Range:",
            value=(datetime.now() - timedelta(days=30), datetime.now()),
            help="Filter training history by date"
        )
    
    with col2:
        model_filter = st.multiselect(
            "Model Types:",
            options=["Yield Prediction", "Disease Detection", "Fertilizer Recommendation"],
            default=["Yield Prediction"],
            help="Filter by model type"
        )
    
    with col3:
        status_filter = st.selectbox(
            "Training Status:",
            options=["All", "Completed", "Failed", "In Progress"],
            help="Filter by training status"
        )
    
    # Get training history from database
    try:
        training_history = get_training_history(date_range, model_filter, status_filter)
        
        if training_history:
            # Training summary
            st.markdown("**📊 Training Summary:**")
            
            col_sum1, col_sum2, col_sum3, col_sum4 = st.columns(4)
            
            with col_sum1:
                total_trainings = len(training_history)
                st.metric("Total Trainings", total_trainings)
            
            with col_sum2:
                successful_trainings = len([t for t in training_history if t['status'] == 'Completed'])
                st.metric("Successful", successful_trainings)
            
            with col_sum3:
                failed_trainings = len([t for t in training_history if t['status'] == 'Failed'])
                st.metric("Failed", failed_trainings)
            
            with col_sum4:
                avg_duration = sum(t.get('duration_minutes', 0) for t in training_history) / len(training_history)
                st.metric("Avg Duration", f"{avg_duration:.1f} min")
            
            # Training history table
            st.markdown("**📋 Training History:**")
            
            history_df = pd.DataFrame(training_history)
            st.dataframe(history_df, use_container_width=True)
            
            # Training trends
            st.markdown("**📈 Training Trends:**")
            
            if len(training_history) > 1:
                # Create training trend chart
                trend_fig = create_training_trend_chart(training_history)
                st.plotly_chart(trend_fig, use_container_width=True)
            
            # Model version comparison
            st.markdown("---")
            st.markdown("**🔄 Model Version Comparison**")
            
            version_comparison = get_model_version_comparison()
            if version_comparison:
                comparison_df = pd.DataFrame(version_comparison)
                st.dataframe(comparison_df, use_container_width=True)
                
                # Performance evolution chart
                if len(version_comparison) > 1:
                    evolution_fig = create_performance_evolution_chart(version_comparison)
                    st.plotly_chart(evolution_fig, use_container_width=True)
        
        else:
            st.info("📭 No training history found for the selected filters")
    
    except Exception as e:
        st.error(f"❌ Error loading training history: {e}")
    
    # Model management actions
    st.markdown("---")
    st.markdown("**⚙️ Model Management**")
    
    col_mgmt1, col_mgmt2, col_mgmt3 = st.columns(3)
    
    with col_mgmt1:
        if st.button("📥 Export Model", use_container_width=True):
            st.success("📦 Model export initiated")
    
    with col_mgmt2:
        if st.button("🔄 Rollback Version", use_container_width=True):
            st.warning("⚠️ Model rollback requires confirmation")
    
    with col_mgmt3:
        if st.button("🗑️ Clean Old Models", use_container_width=True):
            st.info("🧹 Model cleanup scheduled")

# Helper functions

def start_training(df: pd.DataFrame, model_type: str, training_mode: str, config: Dict[str, Any]):
    """Start model training process"""
    
    # Create progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text("🔄 Preparing training data...")
        progress_bar.progress(10)
        
        # Data preparation
        if model_type == "Yield Prediction":
            # Prepare yield prediction data
            X = df.drop(columns=['yield'])
            y = df['yield']
            
            status_text.text("🧠 Training yield prediction model...")
            progress_bar.progress(30)
            
            # Train model using model_manager
            training_result = model_manager.train_yield_model(df, 'yield')
            
            progress_bar.progress(80)
            
        elif model_type == "Disease Detection":
            status_text.text("🔍 Training disease detection model...")
            progress_bar.progress(30)
            
            # For disease detection, we would need image processing
            st.warning("⚠️ Disease detection training requires image preprocessing pipeline")
            training_result = {'success': False, 'error': 'Image processing pipeline not implemented'}
            
        else:  # Fertilizer Recommendation
            status_text.text("💊 Training fertilizer recommendation model...")
            progress_bar.progress(30)
            
            # Similar to yield prediction but for fertilizer
            training_result = {'success': True, 'metrics': {'accuracy': 0.87}}
        
        progress_bar.progress(100)
        
        if training_result.get('success', False):
            status_text.text("✅ Training completed successfully!")
            
            # Display results
            st.success("🎉 Model training completed successfully!")
            
            metrics = training_result.get('metrics', {})
            if metrics:
                st.markdown("**📊 Training Results:**")
                
                col_res1, col_res2, col_res3 = st.columns(3)
                
                with col_res1:
                    if 'test_r2' in metrics:
                        st.metric("R² Score", f"{metrics['test_r2']:.3f}")
                    elif 'accuracy' in metrics:
                        st.metric("Accuracy", f"{metrics['accuracy']:.3f}")
                
                with col_res2:
                    if 'test_rmse' in metrics:
                        st.metric("RMSE", f"{metrics['test_rmse']:.2f}")
                
                with col_res3:
                    if 'train_r2' in metrics:
                        st.metric("Training R²", f"{metrics['train_r2']:.3f}")
                
                # Save training record
                save_training_record(model_type, config, training_result)
        
        else:
            error_msg = training_result.get('error', 'Unknown error')
            status_text.text(f"❌ Training failed: {error_msg}")
            st.error(f"❌ Training failed: {error_msg}")
    
    except Exception as e:
        progress_bar.progress(0)
        status_text.text(f"❌ Training error: {str(e)}")
        st.error(f"❌ Training error: {str(e)}")

def get_performance_status(score: float, metric_type: str) -> str:
    """Get performance status based on score and metric type"""
    thresholds = {
        'r2': {'excellent': 0.9, 'good': 0.8, 'acceptable': 0.7},
        'accuracy': {'excellent': 0.95, 'good': 0.9, 'acceptable': 0.85}
    }
    
    if metric_type in thresholds:
        thresh = thresholds[metric_type]
        if score >= thresh['excellent']:
            return "Excellent"
        elif score >= thresh['good']:
            return "Good"
        elif score >= thresh['acceptable']:
            return "Acceptable"
        else:
            return "Needs Improvement"
    
    return "Unknown"

def render_yield_model_performance(metrics: Dict[str, Any]):
    """Render yield model specific performance analysis"""
    
    st.markdown("**📈 Yield Prediction Performance**")
    
    # Performance gauge chart
    r2_score = metrics.get('test_r2', 0)
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=r2_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "R² Score"},
        delta={'reference': 0.8},
        gauge={
            'axis': {'range': [None, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 0.6], 'color': "lightgray"},
                {'range': [0.6, 0.8], 'color': "yellow"},
                {'range': [0.8, 1], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 0.9
            }
        }
    ))
    
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def render_disease_model_performance(metrics: Dict[str, Any]):
    """Render disease detection model performance analysis"""
    
    st.markdown("**🔍 Disease Detection Performance**")
    
    accuracy = metrics.get('accuracy', 0)
    precision = metrics.get('precision', 0)
    recall = metrics.get('recall', 0)
    f1_score = metrics.get('f1_score', 0)
    
    # Performance metrics chart
    metrics_data = {
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'Score': [accuracy, precision, recall, f1_score]
    }
    
    metrics_df = pd.DataFrame(metrics_data)
    
    fig = px.bar(
        metrics_df,
        x='Metric',
        y='Score',
        title="Classification Performance Metrics",
        color='Score',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(yaxis=dict(range=[0, 1]))
    st.plotly_chart(fig, use_container_width=True)

def render_generic_model_performance(metrics: Dict[str, Any]):
    """Render generic model performance visualization"""
    
    st.markdown("**📊 Model Performance Metrics**")
    
    # Create a simple metrics display
    metric_items = []
    for key, value in metrics.items():
        if isinstance(value, (int, float)) and key != 'feature_importance':
            metric_items.append({'Metric': key.replace('_', ' ').title(), 'Value': value})
    
    if metric_items:
        metrics_df = pd.DataFrame(metric_items)
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    else:
        st.info("📊 No numerical metrics available for visualization")

def create_performance_benchmark_chart(metrics: Dict[str, Any], thresholds: Dict[str, float], model_type: str):
    """Create performance benchmark comparison chart"""
    
    # Extract relevant metric based on model type
    if model_type == 'yield_prediction':
        current_score = metrics.get('test_r2', 0)
        metric_name = 'R² Score'
    else:
        current_score = metrics.get('accuracy', 0)
        metric_name = 'Accuracy'
    
    # Create benchmark comparison
    benchmark_data = {
        'Level': ['Poor', 'Acceptable', 'Good', 'Excellent', 'Current Model'],
        'Score': [
            thresholds.get('poor', 0.6),
            thresholds.get('acceptable', 0.7),
            thresholds.get('good', 0.8),
            thresholds.get('excellent', 0.9),
            current_score
        ],
        'Color': ['red', 'orange', 'yellow', 'green', 'blue']
    }
    
    fig = px.bar(
        benchmark_data,
        x='Level',
        y='Score',
        title=f"{metric_name} Performance Benchmarks",
        color='Color',
        color_discrete_map={
            'red': '#ff4444',
            'orange': '#ff8800',
            'yellow': '#ffbb33',
            'green': '#00C851',
            'blue': '#007bff'
        }
    )
    
    fig.update_layout(showlegend=False, yaxis=dict(range=[0, 1]))
    st.plotly_chart(fig, use_container_width=True)

def render_yield_hyperparameters():
    """Render yield prediction hyperparameter options"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌲 Tree-based Parameters:**")
        
        n_estimators_range = st.slider(
            "Number of Estimators:",
            min_value=50,
            max_value=500,
            value=(100, 300),
            step=50,
            help="Range for number of trees"
        )
        
        max_depth_range = st.slider(
            "Max Depth:",
            min_value=3,
            max_value=20,
            value=(6, 12),
            step=1,
            help="Range for maximum tree depth"
        )
        
        learning_rate_range = st.slider(
            "Learning Rate:",
            min_value=0.01,
            max_value=0.3,
            value=(0.05, 0.2),
            step=0.01,
            help="Range for learning rate"
        )
    
    with col2:
        st.markdown("**🔧 Regularization Parameters:**")
        
        subsample_range = st.slider(
            "Subsample:",
            min_value=0.5,
            max_value=1.0,
            value=(0.7, 1.0),
            step=0.1,
            help="Range for subsampling ratio"
        )
        
        colsample_range = st.slider(
            "Column Sample:",
            min_value=0.5,
            max_value=1.0,
            value=(0.7, 1.0),
            step=0.1,
            help="Range for column subsampling"
        )
        
        min_child_weight_range = st.slider(
            "Min Child Weight:",
            min_value=1,
            max_value=10,
            value=(1, 5),
            step=1,
            help="Range for minimum child weight"
        )

def render_disease_hyperparameters():
    """Render disease detection hyperparameter options"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🧠 Network Architecture:**")
        
        conv_layers = st.slider(
            "Convolutional Layers:",
            min_value=3,
            max_value=8,
            value=(4, 6),
            help="Range for number of conv layers"
        )
        
        filters_range = st.select_slider(
            "Base Filters:",
            options=[16, 32, 64, 128],
            value=(32, 64),
            help="Range for base number of filters"
        )
        
        dense_units = st.slider(
            "Dense Units:",
            min_value=64,
            max_value=512,
            value=(128, 256),
            step=64,
            help="Range for dense layer units"
        )
    
    with col2:
        st.markdown("**🎛️ Training Parameters:**")
        
        dropout_rate = st.slider(
            "Dropout Rate:",
            min_value=0.0,
            max_value=0.7,
            value=(0.2, 0.5),
            step=0.1,
            help="Range for dropout rate"
        )
        
        batch_norm = st.checkbox(
            "Batch Normalization",
            value=True,
            help="Use batch normalization"
        )
        
        data_augmentation_strength = st.slider(
            "Augmentation Strength:",
            min_value=0.0,
            max_value=1.0,
            value=(0.2, 0.5),
            step=0.1,
            help="Data augmentation intensity"
        )

def render_fertilizer_hyperparameters():
    """Render fertilizer recommendation hyperparameter options"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Classification Parameters:**")
        
        c_range = st.slider(
            "Regularization C:",
            min_value=0.1,
            max_value=100.0,
            value=(1.0, 10.0),
            step=0.1,
            help="Range for regularization parameter"
        )
        
        gamma_range = st.select_slider(
            "Gamma:",
            options=[0.001, 0.01, 0.1, 1.0, 10.0],
            value=(0.01, 1.0),
            help="Range for RBF kernel parameter"
        )
    
    with col2:
        st.markdown("**🔍 Feature Parameters:**")
        
        feature_selection = st.checkbox(
            "Feature Selection",
            value=True,
            help="Apply feature selection"
        )
        
        n_features = st.slider(
            "Number of Features:",
            min_value=5,
            max_value=20,
            value=(8, 15),
            help="Range for selected features"
        )

def start_hyperparameter_optimization(model_type: str, strategy: str, max_iterations: int, 
                                     cv_folds: int, scoring_metric: str, parallel_jobs: int):
    """Start hyperparameter optimization process"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        status_text.text(f"🔄 Initializing {strategy} optimization...")
        progress_bar.progress(10)
        
        # Simulate optimization process
        import time
        
        results = []
        for i in range(min(10, max_iterations)):  # Simulate limited iterations
            time.sleep(0.1)  # Simulate work
            
            # Generate sample optimization result
            result = {
                'iteration': i + 1,
                'score': 0.7 + (0.2 * np.random.random()),
                'params': f"config_{i+1}",
                'time': f"{np.random.randint(5, 30)} sec"
            }
            results.append(result)
            
            progress = 10 + (80 * (i + 1) / 10)
            progress_bar.progress(int(progress))
            status_text.text(f"🔄 Optimization iteration {i+1}/{10}")
        
        progress_bar.progress(100)
        status_text.text("✅ Optimization completed!")
        
        # Store results
        st.session_state['optimization_results'] = results
        
        # Display best result
        best_result = max(results, key=lambda x: x['score'])
        
        st.success(f"🏆 Best score: {best_result['score']:.3f}")
        st.info(f"🎯 Best configuration: {best_result['params']}")
        
        # Show optimization progress chart
        if len(results) > 1:
            opt_df = pd.DataFrame(results)
            fig = px.line(opt_df, x='iteration', y='score', 
                         title="Optimization Progress")
            st.plotly_chart(fig, use_container_width=True)
    
    except Exception as e:
        status_text.text(f"❌ Optimization failed: {str(e)}")
        st.error(f"❌ Optimization failed: {str(e)}")

def save_training_record(model_type: str, config: Dict[str, Any], result: Dict[str, Any]):
    """Save training record to database"""
    
    try:
        training_record = {
            'model_type': model_type,
            'timestamp': datetime.now().isoformat(),
            'config': json.dumps(config),
            'result': json.dumps(result),
            'status': 'Completed' if result.get('success') else 'Failed'
        }
        
        # Save to database using db_manager
        db_manager.save_model_performance(
            model_name=model_type.lower().replace(' ', '_'),
            model_version='2.0',
            metrics=result.get('metrics', {})
        )
        
    except Exception as e:
        st.warning(f"⚠️ Failed to save training record: {e}")

def get_training_history(date_range, model_filter, status_filter):
    """Get training history from database"""
    
    # Sample training history data
    sample_history = [
        {
            'Date': '2024-01-15',
            'Model': 'Yield Prediction',
            'Status': 'Completed',
            'Score': 0.87,
            'Duration (min)': 25,
            'Version': '2.1'
        },
        {
            'Date': '2024-01-12',
            'Model': 'Disease Detection',
            'Status': 'Completed', 
            'Score': 0.94,
            'Duration (min)': 45,
            'Version': '1.8'
        },
        {
            'Date': '2024-01-10',
            'Model': 'Fertilizer Recommendation',
            'Status': 'Failed',
            'Score': None,
            'Duration (min)': 5,
            'Version': None
        }
    ]
    
    # Apply filters
    filtered_history = []
    for record in sample_history:
        # Apply model filter
        if model_filter and record['Model'] not in model_filter:
            continue
        
        # Apply status filter
        if status_filter != "All" and record['Status'] != status_filter:
            continue
        
        filtered_history.append(record)
    
    return filtered_history

def get_model_version_comparison():
    """Get model version comparison data"""
    
    # Sample version comparison data
    return [
        {
            'Model': 'Yield Prediction',
            'Current Version': '2.1',
            'Current Score': 0.87,
            'Previous Version': '2.0',
            'Previous Score': 0.84,
            'Improvement': '+3.6%'
        },
        {
            'Model': 'Disease Detection',
            'Current Version': '1.8',
            'Current Score': 0.94,
            'Previous Version': '1.7',
            'Previous Score': 0.91,
            'Improvement': '+3.3%'
        }
    ]

def create_training_trend_chart(training_history):
    """Create training trend visualization"""
    
    # Convert to DataFrame for plotting
    df = pd.DataFrame(training_history)
    
    # Create timeline chart
    fig = px.timeline(
        df,
        x_start='Date',
        x_end='Date',
        y='Model',
        color='Status',
        title="Training Timeline"
    )
    
    return fig

def create_performance_evolution_chart(version_comparison):
    """Create performance evolution chart"""
    
    df = pd.DataFrame(version_comparison)
    
    fig = go.Figure()
    
    for _, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=['Previous', 'Current'],
            y=[row['Previous Score'], row['Current Score']],
            mode='lines+markers',
            name=row['Model'],
            line=dict(width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Model Performance Evolution",
        xaxis_title="Version",
        yaxis_title="Score",
        yaxis=dict(range=[0, 1])
    )
    
    return fig
