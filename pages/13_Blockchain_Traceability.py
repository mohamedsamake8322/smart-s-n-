
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.blockchain_system import agricultural_blockchain
from utils.translations import translator
import json

st.set_page_config(page_title="Blockchain Traceability", page_icon="🔗", layout="wide")

# Language selection
if 'language' not in st.session_state:
    st.session_state.language = 'en'

col_lang1, col_lang2 = st.columns([3, 1])
with col_lang2:
    available_languages = translator.get_available_languages()
    selected_lang = st.selectbox(
        "Language / Langue",
        options=list(available_languages.keys()),
        format_func=lambda x: available_languages[x],
        index=list(available_languages.keys()).index(st.session_state.language)
    )
    if selected_lang != st.session_state.language:
        st.session_state.language = selected_lang
        st.rerun()

lang = st.session_state.language

st.title(f"🔗 {translator.get_text('blockchain_traceability', lang)}")
st.markdown(f"### {translator.get_text('product_authenticity', lang)} & {translator.get_text('supply_chain', lang)}")

# Initialize blockchain data
if 'blockchain_initialized' not in st.session_state:
    # Add sample data
    farm_id = agricultural_blockchain.register_farm({
        'name': 'Green Valley Farm',
        'location': 'Ontario, Canada',
        'owner': 'John Smith',
        'size': 150,
        'certification': 'organic'
    })
    
    crop_id = agricultural_blockchain.create_crop_record({
        'farm_id': farm_id,
        'crop_type': 'wheat',
        'variety': 'Hard Red Winter',
        'planting_date': '2024-04-15',
        'area': 25,
        'seeds_source': 'Certified Organic Seeds Co.',
        'organic': True,
        'gmo_free': True
    })
    
    agricultural_blockchain.add_treatment_record(crop_id, {
        'type': 'fertilizer',
        'product': 'Organic Compost',
        'date': '2024-05-20',
        'amount': 2.5,
        'method': 'broadcast',
        'weather': 'clear, 18°C',
        'applicator': 'John Smith',
        'compliant': True
    })
    
    st.session_state.blockchain_initialized = True
    st.session_state.sample_farm_id = farm_id
    st.session_state.sample_crop_id = crop_id

# Sidebar for blockchain operations
st.sidebar.title("🔗 Blockchain Operations")

operation = st.sidebar.selectbox(
    "Select Operation",
    ["View Traceability", "Register Farm", "Create Crop Record", "Add Treatment", "Record Harvest", "Verify Product"]
)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏪 Product Verification",
    "🏭 Farm Registration", 
    "🌱 Crop Records",
    "📊 Supply Chain Analytics",
    "🏆 Certification & Premiums"
])

with tab1:
    st.subheader("🔍 Product Authentication & Traceability")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔎 Verify Product Authenticity:**")
        
        product_id_input = st.text_input(
            "Enter Product ID:",
            value=st.session_state.get('sample_crop_id', ''),
            help="Scan QR code or enter product ID"
        )
        
        if st.button("🔍 Verify Product", use_container_width=True) and product_id_input:
            verification_result = agricultural_blockchain.verify_product_authenticity(product_id_input)
            
            if verification_result['verified']:
                st.success("✅ Product Verified - Authentic!")
                
                # Display traceability information
                st.markdown("**📋 Product Information:**")
                crop_data = verification_result['crop_data']
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Crop Type:** {crop_data['crop_type'].title()}")
                    st.info(f"**Variety:** {crop_data['variety']}")
                    st.info(f"**Planting Date:** {crop_data['planting_date']}")
                    st.info(f"**Area:** {crop_data['area_planted']} hectares")
                
                with col_b:
                    st.success(f"**Organic Certified:** {'Yes' if crop_data['organic_certified'] else 'No'}")
                    st.success(f"**GMO Free:** {'Yes' if crop_data['gmo_free'] else 'No'}")
                    st.info(f"**Seeds Source:** {crop_data['seeds_source']}")
                
                # Farm information
                if verification_result['farm_info']:
                    st.markdown("**🏭 Farm Information:**")
                    farm_info = verification_result['farm_info']
                    
                    col_c, col_d = st.columns(2)
                    with col_c:
                        st.info(f"**Farm Name:** {farm_info['farm_name']}")
                        st.info(f"**Location:** {farm_info['location']}")
                    with col_d:
                        st.info(f"**Owner:** {farm_info['owner']}")
                        st.info(f"**Size:** {farm_info['size_hectares']} hectares")
                
                # Treatment history
                if verification_result['treatments']:
                    st.markdown("**💊 Treatment History:**")
                    treatments_df = pd.DataFrame([
                        {
                            'Date': t['application_date'],
                            'Type': t['treatment_type'].replace('_', ' ').title(),
                            'Product': t['product_name'],
                            'Amount': f"{t['amount_applied']} kg/ha",
                            'Method': t['application_method'],
                            'Compliant': '✅' if t['certification_compliant'] else '❌'
                        }
                        for t in verification_result['treatments']
                    ])
                    st.dataframe(treatments_df, use_container_width=True)
                
                # Harvest information
                if verification_result['harvest_data']:
                    st.markdown("**🌾 Harvest Information:**")
                    harvest = verification_result['harvest_data']
                    
                    col_e, col_f = st.columns(2)
                    with col_e:
                        st.info(f"**Harvest Date:** {harvest['harvest_date']}")
                        st.info(f"**Yield:** {harvest['yield_amount']} tons")
                    with col_f:
                        st.info(f"**Quality Grade:** {harvest['quality_grade']}")
                        st.info(f"**Moisture:** {harvest['moisture_content']}%")
            
            else:
                st.error("❌ Product verification failed!")
                if 'error' in verification_result:
                    st.error(f"Error: {verification_result['error']}")
    
    with col2:
        st.markdown("**📱 QR Code Scanner:**")
        
        # QR Code display (placeholder)
        st.markdown("""
        <div style='text-align: center; padding: 20px; border: 2px dashed #ccc; border-radius: 10px;'>
            <h3>📱 QR Code Scanner</h3>
            <p>In a real implementation, this would be a camera interface for scanning QR codes on products</p>
            <button style='padding: 10px 20px; background: #4CAF50; color: white; border: none; border-radius: 5px;'>
                📷 Open Camera
            </button>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**🎯 Quick Product Lookup:**")
        
        quick_products = [
            "Organic Wheat Batch #2024-001",
            "Premium Corn Batch #2024-002", 
            "Certified Soybeans #2024-003"
        ]
        
        for product in quick_products:
            if st.button(f"🔍 {product}", key=f"quick_{product}"):
                st.info(f"Looking up: {product}")

with tab2:
    st.subheader("🏭 Farm Registration & Certification")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Register New Farm:**")
        
        with st.form("farm_registration"):
            farm_name = st.text_input("Farm Name *", placeholder="e.g., Green Valley Organic Farm")
            farm_owner = st.text_input("Owner Name *", placeholder="e.g., John Smith")
            farm_location = st.text_input("Location *", placeholder="e.g., Ontario, Canada")
            farm_size = st.number_input("Farm Size (hectares) *", min_value=0.1, value=50.0, step=0.1)
            
            certification_type = st.selectbox(
                "Certification Type *",
                ["Conventional", "Organic", "Biodynamic", "Fair Trade", "Rainforest Alliance", "GAP Certified"]
            )
            
            additional_certifications = st.multiselect(
                "Additional Certifications",
                ["ISO 14001", "GlobalGAP", "SQF", "BRC", "HACCP", "Non-GMO Project"]
            )
            
            farm_description = st.text_area(
                "Farm Description",
                placeholder="Brief description of farming practices, specialties, etc."
            )
            
            submitted = st.form_submit_button("🏭 Register Farm")
            
            if submitted and farm_name and farm_owner and farm_location:
                farm_data = {
                    'name': farm_name,
                    'owner': farm_owner,
                    'location': farm_location,
                    'size': farm_size,
                    'certification': certification_type.lower(),
                    'additional_certs': additional_certifications,
                    'description': farm_description
                }
                
                farm_id = agricultural_blockchain.register_farm(farm_data)
                
                st.success(f"✅ Farm registered successfully!")
                st.info(f"**Farm ID:** `{farm_id}`")
                st.info("Save this ID for future crop registrations.")
                
                # Generate QR code info
                st.markdown("**📱 Farm QR Code Information:**")
                qr_data = {
                    'type': 'farm',
                    'id': farm_id,
                    'name': farm_name,
                    'verification_url': f"https://blockchain-verify.com/farm/{farm_id}"
                }
                st.code(json.dumps(qr_data, indent=2))
    
    with col2:
        st.markdown("**🏆 Registered Farms:**")
        
        # Display registered farms
        if agricultural_blockchain.certified_farms:
            farms_data = []
            for farm_id, farm_info in agricultural_blockchain.certified_farms.items():
                farm_data = farm_info['data']
                farms_data.append({
                    'Farm ID': farm_id[:8] + '...',
                    'Name': farm_data['farm_name'],
                    'Owner': farm_data['owner'],
                    'Location': farm_data['location'],
                    'Size (ha)': farm_data['size_hectares'],
                    'Certification': farm_data['certification_type'].title(),
                    'Status': '✅ Verified' if farm_info['verified'] else '⏳ Pending'
                })
            
            farms_df = pd.DataFrame(farms_data)
            st.dataframe(farms_df, use_container_width=True)
        else:
            st.info("No farms registered yet.")
        
        st.markdown("**📊 Certification Statistics:**")
        
        # Create sample stats
        cert_stats = {
            'Organic': 12,
            'Conventional': 8,
            'Biodynamic': 3,
            'Fair Trade': 5,
            'GAP Certified': 7
        }
        
        fig_certs = px.pie(
            values=list(cert_stats.values()),
            names=list(cert_stats.keys()),
            title="Farm Certifications Distribution"
        )
        st.plotly_chart(fig_certs, use_container_width=True)

with tab3:
    st.subheader("🌱 Crop Production Records")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**📝 Create Crop Record:**")
        
        with st.form("crop_record"):
            # Farm selection
            available_farms = list(agricultural_blockchain.certified_farms.keys())
            if available_farms:
                selected_farm = st.selectbox(
                    "Select Farm *",
                    options=available_farms,
                    format_func=lambda x: agricultural_blockchain.certified_farms[x]['data']['farm_name']
                )
            else:
                st.warning("Please register a farm first.")
                selected_farm = None
            
            crop_type = st.selectbox(
                "Crop Type *",
                ["Wheat", "Corn", "Rice", "Soybeans", "Barley", "Cotton", "Tomatoes", "Potatoes", "Other"]
            )
            
            if crop_type == "Other":
                crop_type = st.text_input("Specify Crop Type", placeholder="e.g., Quinoa")
            
            variety = st.text_input("Variety", placeholder="e.g., Hard Red Winter Wheat")
            planting_date = st.date_input("Planting Date *")
            area_planted = st.number_input("Area Planted (hectares) *", min_value=0.1, value=10.0, step=0.1)
            
            seeds_source = st.text_input(
                "Seeds Source *",
                placeholder="e.g., Certified Organic Seeds Co."
            )
            
            col_a, col_b = st.columns(2)
            with col_a:
                organic_certified = st.checkbox("Organic Certified", False)
            with col_b:
                gmo_free = st.checkbox("GMO Free", True)
            
            cultivation_notes = st.text_area(
                "Cultivation Notes",
                placeholder="Special practices, soil preparation, etc."
            )
            
            submitted = st.form_submit_button("🌱 Create Crop Record")
            
            if submitted and selected_farm and crop_type and seeds_source:
                crop_data = {
                    'farm_id': selected_farm,
                    'crop_type': crop_type,
                    'variety': variety,
                    'planting_date': planting_date.isoformat(),
                    'area': area_planted,
                    'seeds_source': seeds_source,
                    'organic': organic_certified,
                    'gmo_free': gmo_free,
                    'notes': cultivation_notes
                }
                
                crop_id = agricultural_blockchain.create_crop_record(crop_data)
                
                st.success(f"✅ Crop record created successfully!")
                st.info(f"**Crop ID:** `{crop_id}`")
                st.info("Use this ID to add treatments and harvest records.")
    
    with col2:
        st.markdown("**🌾 Production Records:**")
        
        if agricultural_blockchain.product_records:
            records_data = []
            for crop_id, record_info in agricultural_blockchain.product_records.items():
                crop_data = record_info['data']
                records_data.append({
                    'Crop ID': crop_id[:8] + '...',
                    'Crop Type': crop_data['crop_type'].title(),
                    'Variety': crop_data['variety'],
                    'Planting Date': crop_data['planting_date'],
                    'Area (ha)': crop_data['area_planted'],
                    'Organic': '✅' if crop_data['organic_certified'] else '❌',
                    'GMO Free': '✅' if crop_data['gmo_free'] else '❌'
                })
            
            records_df = pd.DataFrame(records_data)
            st.dataframe(records_df, use_container_width=True)
        else:
            st.info("No crop records created yet.")
        
        st.markdown("**📈 Production Analytics:**")
        
        # Sample production data
        production_data = {
            'Wheat': 45,
            'Corn': 32,
            'Soybeans': 28,
            'Rice': 15,
            'Other': 10
        }
        
        fig_production = px.bar(
            x=list(production_data.keys()),
            y=list(production_data.values()),
            title="Crop Production by Type (hectares)",
            labels={'x': 'Crop Type', 'y': 'Area (hectares)'}
        )
        st.plotly_chart(fig_production, use_container_width=True)

with tab4:
    st.subheader("📊 Supply Chain Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔗 Blockchain Network Stats:**")
        
        # Blockchain statistics
        total_blocks = len(agricultural_blockchain.chain)
        total_farms = len(agricultural_blockchain.certified_farms)
        total_products = len(agricultural_blockchain.product_records)
        
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Total Blocks", total_blocks)
        with col_b:
            st.metric("Registered Farms", total_farms)
        with col_c:
            st.metric("Product Records", total_products)
        
        # Chain validity check
        is_valid = agricultural_blockchain.is_chain_valid()
        if is_valid:
            st.success("✅ Blockchain integrity verified")
        else:
            st.error("❌ Blockchain integrity compromised")
        
        st.markdown("**📈 Network Growth:**")
        
        # Sample growth data
        dates = pd.date_range(start='2024-01-01', end='2024-06-12', freq='W')
        blocks_over_time = np.cumsum(np.random.poisson(2, len(dates)))
        
        fig_growth = px.line(
            x=dates,
            y=blocks_over_time,
            title="Blockchain Growth Over Time",
            labels={'x': 'Date', 'y': 'Total Blocks'}
        )
        st.plotly_chart(fig_growth, use_container_width=True)
    
    with col2:
        st.markdown("**🌍 Supply Chain Transparency:**")
        
        # Sample supply chain data
        supply_chain_data = [
            {'Stage': 'Farm Registration', 'Completion': 100, 'Farms': 23},
            {'Stage': 'Crop Planting', 'Completion': 85, 'Farms': 20},
            {'Stage': 'Treatment Records', 'Completion': 78, 'Farms': 18},
            {'Stage': 'Harvest Records', 'Completion': 45, 'Farms': 10},
            {'Stage': 'Distribution', 'Completion': 23, 'Farms': 5}
        ]
        
        fig_supply_chain = px.funnel(
            pd.DataFrame(supply_chain_data),
            x='Completion',
            y='Stage',
            title="Supply Chain Completion Funnel"
        )
        st.plotly_chart(fig_supply_chain, use_container_width=True)
        
        st.markdown("**🎯 Traceability Coverage:**")
        
        coverage_data = {
            'Fully Traceable': 15,
            'Partially Traceable': 8,
            'Not Traceable': 2
        }
        
        fig_coverage = px.pie(
            values=list(coverage_data.values()),
            names=list(coverage_data.keys()),
            title="Product Traceability Coverage",
            color_discrete_map={
                'Fully Traceable': '#2E8B57',
                'Partially Traceable': '#FFA500', 
                'Not Traceable': '#DC143C'
            }
        )
        st.plotly_chart(fig_coverage, use_container_width=True)

with tab5:
    st.subheader("🏆 Environmental Certification & Premium Pricing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🌱 Environmental Score Calculator:**")
        
        product_id_for_score = st.selectbox(
            "Select Product for Environmental Assessment:",
            options=list(agricultural_blockchain.product_records.keys()) if agricultural_blockchain.product_records else ["No products available"],
            format_func=lambda x: f"Crop: {agricultural_blockchain.product_records[x]['data']['crop_type'].title()}" if x != "No products available" else x
        )
        
        if product_id_for_score != "No products available":
            if st.button("🧮 Calculate Environmental Score", use_container_width=True):
                score_result = agricultural_blockchain.get_environmental_score(product_id_for_score)
                
                if 'error' not in score_result:
                    score = score_result['environmental_score']
                    
                    # Display score with color coding
                    if score >= 90:
                        st.success(f"🌟 **Environmental Score: {score}/100** - Premium Eligible!")
                    elif score >= 80:
                        st.success(f"🌱 **Environmental Score: {score}/100** - Certification Eligible!")
                    elif score >= 60:
                        st.warning(f"⚠️ **Environmental Score: {score}/100** - Needs Improvement")
                    else:
                        st.error(f"❌ **Environmental Score: {score}/100** - Major Improvements Needed")
                    
                    # Certification eligibility
                    col_cert, col_premium = st.columns(2)
                    with col_cert:
                        if score_result['certification_eligible']:
                            st.success("✅ Certification Eligible")
                        else:
                            st.error("❌ Not Certification Eligible")
                    
                    with col_premium:
                        if score_result['premium_eligible']:
                            st.success("💰 Premium Pricing Eligible")
                        else:
                            st.info("💰 Standard Pricing")
                    
                    # Recommendations
                    if score_result['recommendations']:
                        st.markdown("**💡 Improvement Recommendations:**")
                        for rec in score_result['recommendations']:
                            st.write(f"• {rec}")
                else:
                    st.error(f"Error: {score_result['error']}")
        
        st.markdown("**🎯 Certification Programs:**")
        
        cert_programs = [
            {"name": "Organic Premium", "min_score": 85, "premium": "15-25%"},
            {"name": "Carbon Neutral", "min_score": 80, "premium": "10-20%"},
            {"name": "Sustainable Agriculture", "min_score": 75, "premium": "8-15%"},
            {"name": "Biodiversity Friendly", "min_score": 70, "premium": "5-10%"}
        ]
        
        for program in cert_programs:
            st.info(f"**{program['name']}**: Min Score {program['min_score']} → {program['premium']} price premium")
    
    with col2:
        st.markdown("**💰 Premium Pricing Calculator:**")
        
        base_price = st.number_input("Base Market Price ($/ton)", min_value=0.0, value=400.0, step=10.0)
        
        environmental_score_input = st.slider(
            "Environmental Score", 0, 100, 75, 1
        )
        
        # Calculate premium
        if environmental_score_input >= 90:
            premium_percentage = 25
            certification_level = "Premium Organic"
        elif environmental_score_input >= 80:
            premium_percentage = 15
            certification_level = "Certified Sustainable"
        elif environmental_score_input >= 70:
            premium_percentage = 8
            certification_level = "Eco-Friendly"
        else:
            premium_percentage = 0
            certification_level = "Standard"
        
        premium_amount = base_price * (premium_percentage / 100)
        final_price = base_price + premium_amount
        
        st.metric(
            "Certification Level",
            certification_level,
            help=f"Based on environmental score of {environmental_score_input}"
        )
        
        col_base, col_premium, col_total = st.columns(3)
        with col_base:
            st.metric("Base Price", f"${base_price:.2f}")
        with col_premium:
            st.metric("Premium", f"${premium_amount:.2f}", f"{premium_percentage}%")
        with col_total:
            st.metric("Final Price", f"${final_price:.2f}")
        
        # Annual revenue projection
        st.markdown("**📈 Revenue Projection:**")
        
        annual_production = st.number_input("Annual Production (tons)", min_value=0.0, value=100.0, step=10.0)
        
        standard_revenue = base_price * annual_production
        premium_revenue = final_price * annual_production
        additional_revenue = premium_revenue - standard_revenue
        
        col_std, col_prem, col_add = st.columns(3)
        with col_std:
            st.metric("Standard Revenue", f"${standard_revenue:,.0f}")
        with col_prem:
            st.metric("Premium Revenue", f"${premium_revenue:,.0f}")
        with col_add:
            st.metric("Additional Revenue", f"${additional_revenue:,.0f}")
        
        if additional_revenue > 0:
            st.success(f"💰 Potential additional annual revenue: ${additional_revenue:,.0f}")

# Footer
st.markdown("---")
st.markdown("""
### 🔗 Blockchain Benefits:
- **🔒 Immutable Records**: All data is permanently recorded and cannot be altered
- **🌍 Full Traceability**: Track products from farm to consumer
- **✅ Instant Verification**: Verify authenticity in seconds  
- **💰 Premium Pricing**: Earn premiums for sustainable practices
- **🏆 Certifications**: Streamlined certification processes
- **🤝 Trust Building**: Build consumer confidence in your products
""")
