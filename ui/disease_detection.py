"""
Enterprise Disease Detection Interface
Professional plant disease identification with treatment recommendations
"""
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
from typing import Dict, Any, List

from services.prediction_service import prediction_service, PredictionRequest
from models.disease_detector import disease_detector
from utils.data_validation import data_validator
from utils.file_handler import file_handler
from utils.visualization import viz_engine
from config.settings import CROP_TYPES
from data.disease_info import get_disease_information, get_treatment_protocols

def render_disease_detection():
    """Render the disease detection interface"""
    
    st.header("🔍 Advanced Disease Detection")
    st.markdown("AI-powered plant disease identification with professional treatment recommendations")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📷 Image Analysis", 
        "📊 Detection History", 
        "📚 Disease Database", 
        "🛡️ Prevention Guide"
    ])
    
    with tab1:
        render_image_analysis()
    
    with tab2:
        render_detection_history()
    
    with tab3:
        render_disease_database()
    
    with tab4:
        render_prevention_guide()

def render_image_analysis():
    """Render image analysis interface"""
    
    st.subheader("Plant Disease Image Analysis")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Image upload section
        st.markdown("**📷 Upload Plant Image**")
        
        uploaded_image = st.file_uploader(
            "Choose an image...",
            type=['jpg', 'jpeg', 'png', 'bmp'],
            help="Upload a clear image of the plant showing disease symptoms"
        )
        
        # Camera capture option
        camera_image = st.camera_input("📸 Or take a photo with camera")
        
        # Use camera image if no file uploaded
        if camera_image is not None and uploaded_image is None:
            uploaded_image = camera_image
        
        if uploaded_image is not None:
            # Display uploaded image
            image = Image.open(uploaded_image)
            st.image(image, caption="Uploaded Plant Image", use_column_width=True)
            
            # Optional metadata
            with st.expander("📋 Additional Information (Optional)"):
                col_a, col_b = st.columns(2)
                
                with col_a:
                    crop_type = st.selectbox(
                        "Crop Type",
                        options=['Unknown'] + CROP_TYPES,
                        help="Type of crop in the image"
                    )
                    
                    growth_stage = st.selectbox(
                        "Growth Stage",
                        options=['Unknown', 'Seedling', 'Vegetative', 'Flowering', 'Fruiting', 'Mature'],
                        help="Current growth stage"
                    )
                
                with col_b:
                    location_name = st.text_input(
                        "Location",
                        placeholder="Farm/Field name",
                        help="Location where image was taken"
                    )
                    
                    symptoms_observed = st.multiselect(
                        "Observed Symptoms",
                        options=[
                            "Leaf spots", "Yellowing", "Wilting", "Stunted growth",
                            "Fruit damage", "Root damage", "Discoloration", "Necrosis"
                        ],
                        help="Select visible symptoms"
                    )
            
            # Analysis button
            if st.button("🔍 Analyze Image for Disease", type="primary", use_container_width=True):
                with st.spinner("🔄 Analyzing image with AI models..."):
                    try:
                        # Prepare input data
                        input_data = {
                            'image': image,
                            'crop_type': crop_type if crop_type != 'Unknown' else None,
                            'location': location_name if location_name else None,
                            'capture_date': datetime.now().isoformat()
                        }
                        
                        # Validate input
                        validation_result = data_validator.validate_disease_detection_input(input_data)
                        
                        if validation_result.is_valid:
                            # Create prediction request
                            request = PredictionRequest(
                                user_id=1,  # TODO: Get from session
                                prediction_type='disease_detection',
                                input_data=validation_result.cleaned_data
                            )
                            
                            # Get detection result
                            result = prediction_service.detect_plant_disease(request)
                            
                            if result.success:
                                st.session_state['latest_detection'] = result
                                st.success("✅ Disease analysis completed!")
                                st.rerun()
                            else:
                                st.error(f"❌ Analysis failed: {result.error}")
                        else:
                            st.error("❌ Input validation failed")
                            for error in validation_result.errors:
                                st.error(f"• {error}")
                    
                    except Exception as e:
                        st.error(f"❌ Error during analysis: {e}")
        else:
            st.info("📷 Upload an image or take a photo to begin disease analysis")
            
            # Tips for good images
            with st.expander("💡 Tips for Best Results"):
                st.markdown("""
                **📸 Photo Guidelines:**
                - Use good lighting (natural light preferred)
                - Keep image focused and clear
                - Include affected leaves/parts prominently
                - Avoid shadows and reflections
                - Take multiple angles if unsure
                
                **🎯 What to Include:**
                - Clear view of symptoms
                - Both healthy and affected areas
                - Close-up of disease patterns
                - Overall plant condition context
                """)
    
    with col2:
        # Results display
        st.markdown("**🎯 Analysis Results**")
        
        if 'latest_detection' in st.session_state:
            result = st.session_state['latest_detection']
            detection_data = result.result
            
            # Primary diagnosis
            primary_diagnosis = detection_data.get('primary_diagnosis', {})
            
            if primary_diagnosis:
                disease_name = primary_diagnosis.get('disease', 'Unknown')
                confidence = primary_diagnosis.get('confidence', 0)
                severity = primary_diagnosis.get('severity', 'Unknown')
                
                # Main result card
                confidence_color = "🟢" if confidence > 0.8 else "🟡" if confidence > 0.6 else "🔴"
                severity_color = {
                    'Low': '🟢',
                    'Moderate': '🟡', 
                    'High': '🟠',
                    'Severe': '🔴'
                }.get(severity, '⚪')
                
                st.markdown(f"""
                **🔬 Primary Diagnosis:**
                
                **Disease:** {disease_name}
                
                **Confidence:** {confidence_color} {confidence*100:.1f}%
                
                **Severity:** {severity_color} {severity}
                """)
                
                # Health status
                is_healthy = detection_data.get('is_healthy', False)
                if is_healthy:
                    st.success("✅ Plant appears healthy!")
                else:
                    requires_attention = detection_data.get('requires_attention', False)
                    if requires_attention:
                        st.error("⚠️ Immediate attention required")
                    else:
                        st.warning("⚠️ Monitor closely")
                
                # Description
                description = primary_diagnosis.get('description', '')
                if description:
                    st.markdown(f"**📋 Description:**\n{description}")
                
                # Symptoms
                symptoms = primary_diagnosis.get('symptoms', [])
                if symptoms:
                    st.markdown("**🔍 Common Symptoms:**")
                    for symptom in symptoms[:5]:
                        st.write(f"• {symptom}")
                
                # Treatment recommendations
                if result.recommendations:
                    st.markdown("**💊 Treatment Recommendations:**")
                    for recommendation in result.recommendations[:5]:
                        st.write(f"• {recommendation}")
                
                # Alternative diagnoses
                all_predictions = detection_data.get('all_predictions', [])
                if len(all_predictions) > 1:
                    with st.expander("🔍 Alternative Diagnoses"):
                        for i, alt_diagnosis in enumerate(all_predictions[1:4], 2):
                            st.write(f"**{i}. {alt_diagnosis.get('disease', 'Unknown')}**")
                            st.write(f"   Confidence: {alt_diagnosis.get('confidence', 0)*100:.1f}%")
                            st.write("")
                
                # Action buttons
                st.markdown("**⚡ Quick Actions:**")
                
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("📋 Get Treatment Plan", key="treatment_plan"):
                        st.session_state['show_treatment'] = True
                        st.rerun()
                
                with col_y:
                    if st.button("📊 View Disease Info", key="disease_info"):
                        st.session_state['selected_disease'] = disease_name
                        st.rerun()
                
                # Treatment plan modal
                if st.session_state.get('show_treatment', False):
                    with st.expander("📋 Detailed Treatment Plan", expanded=True):
                        treatment_plan = get_treatment_protocols(disease_name)
                        
                        if treatment_plan:
                            st.markdown("**🎯 Immediate Actions:**")
                            for action in treatment_plan.get('immediate_actions', []):
                                st.write(f"• {action}")
                            
                            st.markdown("**💊 Treatment Options:**")
                            for treatment in treatment_plan.get('treatments', []):
                                st.write(f"• {treatment}")
                            
                            st.markdown("**📅 Follow-up Schedule:**")
                            for followup in treatment_plan.get('followup_schedule', []):
                                st.write(f"• {followup}")
                        else:
                            st.write("Detailed treatment plan not available for this disease.")
                        
                        if st.button("❌ Close", key="close_treatment"):
                            st.session_state['show_treatment'] = False
                            st.rerun()
            
            else:
                st.error("❌ No diagnosis results available")
        
        else:
            st.info("🔍 Upload and analyze an image to see results here")
            
            # Sample capabilities
            st.markdown("**🤖 AI Capabilities:**")
            st.write("• Disease identification")
            st.write("• Confidence scoring")  
            st.write("• Severity assessment")
            st.write("• Treatment recommendations")
            st.write("• Prevention strategies")

def render_detection_history():
    """Render detection history interface"""
    
    st.subheader("Disease Detection History")
    
    # Get detection history
    try:
        from core.database import db_manager
        detection_history = db_manager.get_disease_history(
            user_id=1,  # TODO: Get from session
            limit=50
        )
        
        if detection_history:
            df_history = pd.DataFrame(detection_history)
            
            # Summary metrics
            st.markdown("**📊 Detection Summary:**")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Detections", len(detection_history))
            
            with col2:
                recent_count = len([d for d in detection_history if 
                    datetime.fromisoformat(d['created_at'].replace('Z', '+00:00')) > 
                    datetime.now() - timedelta(days=7)])
                st.metric("This Week", recent_count)
            
            with col3:
                healthy_count = len([d for d in detection_history if 
                    'healthy' in d.get('detected_disease', '').lower()])
                st.metric("Healthy Plants", healthy_count)
            
            with col4:
                disease_count = len(detection_history) - healthy_count
                st.metric("Disease Cases", disease_count)
            
            # Disease distribution chart
            if len(detection_history) > 1:
                st.markdown("**📈 Disease Distribution:**")
                disease_counts = df_history['detected_disease'].value_counts()
                
                # Create pie chart
                fig = viz_engine.create_disease_distribution_chart(detection_history)
                st.plotly_chart(fig, use_container_width=True)
            
            # Filters
            st.markdown("**🔍 Filter History:**")
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                date_filter = st.date_input(
                    "Date Range",
                    value=(datetime.now() - timedelta(days=30), datetime.now())
                )
            
            with col_b:
                disease_filter = st.multiselect(
                    "Disease Types",
                    options=df_history['detected_disease'].unique(),
                    help="Filter by specific diseases"
                )
            
            with col_c:
                confidence_filter = st.slider(
                    "Min Confidence",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1
                )
            
            # History table
            st.markdown("**📋 Detection History:**")
            
            # Prepare display data
            display_data = []
            for detection in detection_history[:20]:  # Show latest 20
                display_data.append({
                    'Date': detection.get('created_at', ''),
                    'Disease': detection.get('detected_disease', 'Unknown'),
                    'Confidence': f"{detection.get('confidence_score', 0)*100:.1f}%",
                    'Severity': detection.get('severity_level', 'Unknown'),
                    'Location': detection.get('location_name', 'Unknown'),
                    'Treatment Status': 'Pending'  # TODO: Track treatment status
                })
            
            if display_data:
                history_df = pd.DataFrame(display_data)
                st.dataframe(history_df, use_container_width=True)
                
                # Export options
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("📥 Export History (CSV)"):
                        csv = history_df.to_csv(index=False)
                        st.download_button(
                            "Download CSV",
                            csv,
                            f"disease_history_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv"
                        )
                
                with col_y:
                    if st.button("📊 Generate Report"):
                        st.success("📈 Disease detection report generated!")
            
            else:
                st.info("📭 No detection history matches the current filters")
        
        else:
            st.info("📭 No disease detection history found. Start detecting diseases to build history.")
    
    except Exception as e:
        st.error(f"❌ Error loading detection history: {e}")

def render_disease_database():
    """Render disease information database"""
    
    st.subheader("Plant Disease Database")
    st.markdown("Comprehensive information about plant diseases and treatments")
    
    # Disease search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search Diseases",
            placeholder="Enter disease name or symptoms...",
            help="Search for specific diseases or symptoms"
        )
    
    with col2:
        crop_filter = st.selectbox(
            "Filter by Crop",
            options=['All Crops'] + CROP_TYPES,
            help="Filter diseases by crop type"
        )
    
    # Get disease information
    diseases = get_disease_information()
    
    if search_term or st.session_state.get('selected_disease'):
        # Show specific disease details
        disease_name = st.session_state.get('selected_disease', search_term)
        
        if disease_name in diseases:
            disease_info = diseases[disease_name]
            
            st.markdown(f"## 🦠 {disease_name}")
            
            # Disease overview
            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                st.markdown("**📋 Description:**")
                st.write(disease_info.get('description', 'No description available'))
                
                # Symptoms
                symptoms = disease_info.get('symptoms', [])
                if symptoms:
                    st.markdown("**🔍 Symptoms:**")
                    for symptom in symptoms:
                        st.write(f"• {symptom}")
                
                # Causes
                causes = disease_info.get('causes', [])
                if causes:
                    st.markdown("**🎯 Causes:**")
                    for cause in causes:
                        st.write(f"• {cause}")
            
            with col_b:
                # Disease severity indicator
                severity = disease_info.get('severity', 'Medium')
                severity_color = {
                    'Low': '🟢',
                    'Medium': '🟡',
                    'High': '🟠',
                    'Severe': '🔴'
                }.get(severity, '⚪')
                
                st.markdown(f"**⚠️ Severity:** {severity_color} {severity}")
                
                # Affected crops
                affected_crops = disease_info.get('affected_crops', [])
                if affected_crops:
                    st.markdown("**🌱 Affected Crops:**")
                    for crop in affected_crops[:5]:
                        st.write(f"• {crop}")
                
                # Prevalence
                prevalence = disease_info.get('prevalence', 'Unknown')
                st.markdown(f"**📊 Prevalence:** {prevalence}")
            
            # Treatment section
            st.markdown("---")
            treatment_tab1, treatment_tab2, treatment_tab3 = st.tabs([
                "💊 Treatment", "🛡️ Prevention", "📚 More Info"
            ])
            
            with treatment_tab1:
                treatments = disease_info.get('treatment', [])
                if treatments:
                    st.markdown("**Treatment Options:**")
                    for i, treatment in enumerate(treatments, 1):
                        st.write(f"{i}. {treatment}")
                else:
                    st.info("No specific treatments available")
            
            with treatment_tab2:
                prevention = disease_info.get('prevention', [])
                if prevention:
                    st.markdown("**Prevention Measures:**")
                    for i, measure in enumerate(prevention, 1):
                        st.write(f"{i}. {measure}")
                else:
                    st.info("No specific prevention measures available")
            
            with treatment_tab3:
                # Additional information
                pathogen = disease_info.get('pathogen', 'Unknown')
                transmission = disease_info.get('transmission', 'Unknown')
                
                st.markdown(f"**🦠 Pathogen:** {pathogen}")
                st.markdown(f"**📡 Transmission:** {transmission}")
                
                # External resources
                if 'resources' in disease_info:
                    st.markdown("**🔗 Additional Resources:**")
                    for resource in disease_info['resources']:
                        st.write(f"• {resource}")
        
        else:
            st.warning(f"❓ Disease '{disease_name}' not found in database")
            st.info("💡 Try searching with different keywords or check spelling")
    
    else:
        # Show disease categories
        st.markdown("**🗂️ Disease Categories:**")
        
        categories = {
            "🍄 Fungal Diseases": [
                "Late Blight", "Early Blight", "Powdery Mildew", "Leaf Spot"
            ],
            "🦠 Bacterial Diseases": [
                "Bacterial Wilt", "Fire Blight", "Crown Gall", "Soft Rot"
            ],
            "🧬 Viral Diseases": [
                "Mosaic Virus", "Leaf Curl", "Yellow Dwarf", "Ring Spot"
            ],
            "🐛 Pest-Related": [
                "Aphid Damage", "Caterpillar Damage", "Mite Damage", "Beetle Damage"
            ]
        }
        
        for category, disease_list in categories.items():
            with st.expander(category):
                cols = st.columns(2)
                for i, disease in enumerate(disease_list):
                    col_idx = i % 2
                    with cols[col_idx]:
                        if st.button(disease, key=f"disease_{disease}"):
                            st.session_state['selected_disease'] = disease
                            st.rerun()
        
        # Quick stats
        st.markdown("---")
        st.markdown("**📊 Database Statistics:**")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Diseases", len(diseases))
        with col2:
            st.metric("Fungal", len([d for d in diseases.values() if 'fungal' in d.get('pathogen', '').lower()]))
        with col3:
            st.metric("Bacterial", len([d for d in diseases.values() if 'bacterial' in d.get('pathogen', '').lower()]))
        with col4:
            st.metric("Viral", len([d for d in diseases.values() if 'viral' in d.get('pathogen', '').lower()]))

def render_prevention_guide():
    """Render disease prevention guide"""
    
    st.subheader("Disease Prevention & Management Guide")
    st.markdown("Proactive strategies for maintaining plant health")
    
    prevention_tab1, prevention_tab2, prevention_tab3, prevention_tab4 = st.tabs([
        "🛡️ General Prevention", 
        "🌱 Crop-Specific", 
        "📅 Seasonal Calendar", 
        "🔧 Tools & Equipment"
    ])
    
    with prevention_tab1:
        st.markdown("### 🛡️ General Disease Prevention Strategies")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🌱 Cultural Practices:**")
            cultural_practices = [
                "Maintain proper plant spacing for air circulation",
                "Practice crop rotation to break disease cycles",
                "Remove and destroy infected plant debris",
                "Use certified disease-free seeds and plants",
                "Avoid overhead watering when possible",
                "Monitor plants regularly for early detection"
            ]
            
            for practice in cultural_practices:
                st.write(f"✅ {practice}")
        
        with col2:
            st.markdown("**🌿 Environmental Management:**")
            environmental_practices = [
                "Ensure proper drainage to prevent waterlogging",
                "Maintain optimal soil pH levels",
                "Provide adequate nutrition without over-fertilizing",
                "Control weeds that harbor diseases",
                "Manage humidity levels in greenhouses",
                "Implement integrated pest management"
            ]
            
            for practice in environmental_practices:
                st.write(f"✅ {practice}")
        
        # Biological control
        st.markdown("---")
        st.markdown("**🐛 Biological Control Methods:**")
        
        bio_controls = {
            "Beneficial Microorganisms": [
                "Trichoderma fungi for soil-borne diseases",
                "Bacillus subtilis for bacterial diseases",
                "Mycorrhizal fungi for root health"
            ],
            "Natural Predators": [
                "Ladybugs for aphid control",
                "Parasitic wasps for caterpillars",
                "Predatory mites for spider mites"
            ],
            "Organic Treatments": [
                "Neem oil for fungal diseases",
                "Copper compounds for bacterial diseases",
                "Diatomaceous earth for soft-bodied pests"
            ]
        }
        
        cols = st.columns(3)
        for i, (category, methods) in enumerate(bio_controls.items()):
            with cols[i]:
                st.markdown(f"**{category}:**")
                for method in methods:
                    st.write(f"• {method}")
    
    with prevention_tab2:
        st.markdown("### 🌱 Crop-Specific Prevention")
        
        crop_selection = st.selectbox(
            "Select Crop for Specific Guidelines",
            options=CROP_TYPES,
            help="Get crop-specific disease prevention strategies"
        )
        
        # Crop-specific information
        crop_info = {
            "Tomato": {
                "common_diseases": ["Late Blight", "Early Blight", "Bacterial Spot"],
                "prevention": [
                    "Use resistant varieties when available",
                    "Ensure good air circulation between plants",
                    "Avoid wetting foliage during watering",
                    "Mulch to prevent soil splash",
                    "Practice 3-4 year crop rotation"
                ],
                "optimal_conditions": "Temperature: 18-25°C, Humidity: 60-70%"
            },
            "Maize": {
                "common_diseases": ["Corn Smut", "Gray Leaf Spot", "Northern Corn Leaf Blight"],
                "prevention": [
                    "Plant resistant hybrids",
                    "Maintain proper plant population",
                    "Manage crop residue properly",
                    "Control weeds effectively",
                    "Monitor for early symptoms"
                ],
                "optimal_conditions": "Temperature: 20-30°C, Well-drained soil"
            }
        }
        
        if crop_selection in crop_info:
            info = crop_info[crop_selection]
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown(f"**🎯 Common Diseases for {crop_selection}:**")
                for disease in info["common_diseases"]:
                    st.write(f"• {disease}")
                
                st.markdown(f"**🌡️ Optimal Conditions:**")
                st.info(info["optimal_conditions"])
            
            with col_b:
                st.markdown(f"**🛡️ Prevention Strategies:**")
                for strategy in info["prevention"]:
                    st.write(f"✅ {strategy}")
        
        else:
            st.info(f"Specific guidelines for {crop_selection} will be added soon.")
    
    with prevention_tab3:
        st.markdown("### 📅 Seasonal Disease Management Calendar")
        
        season_selection = st.selectbox(
            "Select Season",
            options=["Spring", "Summer", "Autumn", "Winter"],
            help="Get season-specific management advice"
        )
        
        seasonal_advice = {
            "Spring": {
                "tasks": [
                    "Inspect plants emerging from winter dormancy",
                    "Apply preventive fungicide treatments",
                    "Prepare soil and ensure proper drainage",
                    "Start regular monitoring schedule"
                ],
                "focus": "Early detection and prevention"
            },
            "Summer": {
                "tasks": [
                    "Increase monitoring frequency during hot weather",
                    "Ensure adequate water management",
                    "Control insect vectors of diseases",
                    "Manage humidity in protected cultivation"
                ],
                "focus": "Active disease management"
            },
            "Autumn": {
                "tasks": [
                    "Remove and destroy infected plant material",
                    "Prepare soil for winter cover crops",
                    "Plan crop rotation for next season",
                    "Store seeds and equipment properly"
                ],
                "focus": "Cleanup and preparation"
            },
            "Winter": {
                "tasks": [
                    "Plan disease management strategy for next year",
                    "Order resistant varieties and beneficial organisms",
                    "Maintain and calibrate equipment",
                    "Study disease patterns from the past year"
                ],
                "focus": "Planning and preparation"
            }
        }
        
        if season_selection in seasonal_advice:
            advice = seasonal_advice[season_selection]
            
            st.markdown(f"**🎯 Focus for {season_selection}:** {advice['focus']}")
            
            st.markdown(f"**📋 Key Tasks:**")
            for task in advice['tasks']:
                st.write(f"• {task}")
    
    with prevention_tab4:
        st.markdown("### 🔧 Essential Tools & Equipment")
        
        tool_categories = {
            "🔍 Monitoring Tools": [
                "Hand lens (10x magnification) for detailed inspection",
                "Digital camera for documenting symptoms",
                "pH meter for soil testing",
                "Thermometer and hygrometer for climate monitoring"
            ],
            "🧪 Testing Equipment": [
                "Soil test kits for nutrient analysis", 
                "Disease test strips for quick diagnosis",
                "Microscope for pathogen identification",
                "Water quality test kits"
            ],
            "💧 Application Equipment": [
                "Calibrated sprayers for treatments",
                "Protective equipment (gloves, masks)",
                "Measuring tools for accurate dosing",
                "Clean containers for mixing solutions"
            ],
            "📱 Digital Tools": [
                "Plant disease identification apps",
                "Weather monitoring apps",
                "Record-keeping software",
                "GPS for field mapping"
            ]
        }
        
        cols = st.columns(2)
        for i, (category, tools) in enumerate(tool_categories.items()):
            col_idx = i % 2
            with cols[col_idx]:
                st.markdown(f"**{category}:**")
                for tool in tools:
                    st.write(f"• {tool}")
        
        # Maintenance tips
        st.markdown("---")
        st.markdown("**🔧 Equipment Maintenance Tips:**")
        
        maintenance_tips = [
            "Clean and disinfect tools between uses",
            "Calibrate sprayers regularly for accurate application",
            "Store chemicals in appropriate conditions",
            "Keep digital tools updated with latest information",
            "Maintain logs of all treatments and observations"
        ]
        
        for tip in maintenance_tips:
            st.write(f"✅ {tip}")
