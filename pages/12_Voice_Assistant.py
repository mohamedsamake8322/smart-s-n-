
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.voice_assistant import voice_assistant, expert_chatbot
from utils.translations import translator
import json

st.set_page_config(page_title="Voice Assistant", page_icon="ðŸ—£ï¸", layout="wide")

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

st.title(f"ðŸ—£ï¸ {translator.get_text('voice_assistant', lang)}")
st.markdown(f"### {translator.get_text('expert_chatbot', lang)} & {translator.get_text('voice_reports', lang)}")

# Initialize chat history
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'voice_settings' not in st.session_state:
    st.session_state.voice_settings = {
        'speech_speed': 1.0,
        'voice_type': 'neutral',
        'auto_play': False,
        'language': lang
    }

# Sidebar for voice settings
st.sidebar.title(translator.get_text('voice_assistant', lang))

st.sidebar.subheader("ðŸ”§ Voice Settings")
st.session_state.voice_settings['speech_speed'] = st.sidebar.slider(
    "Speech Speed", 0.5, 2.0, 1.0, 0.1
)
st.session_state.voice_settings['voice_type'] = st.sidebar.selectbox(
    "Voice Type", 
    ["Neutral", "Professional", "Friendly"]
)
st.session_state.voice_settings['auto_play'] = st.sidebar.checkbox(
    "Auto-play responses", False
)

# Main content tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "ðŸ¤– AI Chatbot",
    "ðŸŽ™ï¸ Voice Commands", 
    "ðŸ“Š Daily Reports",
    "ðŸ”” Audio Alerts",
    "âš™ï¸ Assistant Settings"
])

with tab1:
    st.subheader("ðŸ¤– Expert Agricultural Chatbot")
    
    # Chat interface
    st.markdown("**Ask me anything about farming, crops, diseases, soil, weather, or agricultural best practices!**")
    
    # Display chat history
    chat_container = st.container()
    
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['type'] == 'user':
                st.markdown(f"**ðŸ§‘â€ðŸŒ¾ You:** {message['content']}")
            else:
                st.markdown(f"**ðŸ¤– AI Expert:** {message['content']}")
                
                if 'confidence' in message:
                    confidence_color = "green" if message['confidence'] > 80 else "orange" if message['confidence'] > 60 else "red"
                    st.markdown(f"<small style='color: {confidence_color}'>Confidence: {message['confidence']}% | Expertise: {message.get('expertise_area', 'General')}</small>", unsafe_allow_html=True)
                
                if 'follow_up_questions' in message:
                    st.markdown("**Suggested follow-up questions:**")
                    for j, question in enumerate(message['follow_up_questions']):
                        if st.button(f"â“ {question}", key=f"followup_{i}_{j}"):
                            # Add follow-up question to chat
                            st.session_state.chat_history.append({
                                'type': 'user',
                                'content': question,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            # Get AI response
                            response = expert_chatbot.chat(question)
                            st.session_state.chat_history.append({
                                'type': 'assistant',
                                'content': response['message'],
                                'confidence': response['confidence'],
                                'expertise_area': response['expertise_area'],
                                'follow_up_questions': response.get('follow_up_questions', []),
                                'timestamp': datetime.now().isoformat()
                            })
                            st.rerun()
                
                st.markdown("---")
    
    # Chat input
    user_input = st.text_input(
        "ðŸ’¬ Ask your agricultural question:",
        placeholder="e.g., 'My wheat crops have yellow spots on the leaves, what could be wrong?'",
        key="chat_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("ðŸ“¤ Send", use_container_width=True) and user_input:
            # Add user message
            st.session_state.chat_history.append({
                'type': 'user',
                'content': user_input,
                'timestamp': datetime.now().isoformat()
            })
            
            # Get AI response
            response = expert_chatbot.chat(user_input)
            st.session_state.chat_history.append({
                'type': 'assistant',
                'content': response['message'],
                'confidence': response['confidence'],
                'expertise_area': response['expertise_area'],
                'follow_up_questions': response.get('follow_up_questions', []),
                'timestamp': datetime.now().isoformat()
            })
            
            # Clear input and rerun
            st.rerun()
    
    with col2:
        if st.button("ðŸ—‘ï¸ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("ðŸ’¾ Export Chat History", use_container_width=True):
            chat_export = {
                'export_date': datetime.now().isoformat(),
                'total_messages': len(st.session_state.chat_history),
                'messages': st.session_state.chat_history
            }
            st.download_button(
                label="Download Chat",
                data=json.dumps(chat_export, indent=2),
                file_name=f"agricultural_chat_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )

with tab2:
    st.subheader("ðŸŽ™ï¸ Voice Command Interface")
    
    st.info("ðŸŽ¤ Voice recognition feature would be implemented here using Web Speech API or similar technology.")
    
    # Simulate voice command interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**ðŸŽ¯ Quick Voice Commands:**")
        
        voice_commands = [
            "What's today's weather?",
            "Check soil moisture levels",
            "Show my crop predictions",
            "Any disease alerts?",
            "Schedule irrigation",
            "Generate daily report",
            "What fertilizer should I use?",
            "Check market prices"
        ]
        
        for cmd in voice_commands:
            if st.button(f"ðŸŽ¤ '{cmd}'", key=f"voice_cmd_{cmd}"):
                # Process voice command
                response = voice_assistant.process_voice_command(cmd)
                
                st.success(f"**Command processed:** {cmd}")
                st.info(f"**AI Response:** {response['text_response']}")
                
                if response['actions']:
                    st.markdown(f"**Suggested actions:** {', '.join(response['actions'])}")
    
    with col2:
        st.markdown("**ðŸ”Š Voice Response Preview:**")
        
        sample_text = st.text_area(
            "Enter text to hear AI voice response:",
            value="Your crops are looking healthy. Soil moisture is at optimal levels.",
            height=100
        )
        
        if st.button("ðŸ”Š Play Voice Response"):
            st.audio("data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAAAAQABAAA...", format="audio/wav")
            st.success("ðŸŽµ Voice synthesis would play here")
        
        st.markdown("**ðŸŽ›ï¸ Voice Customization:**")
        voice_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1, key="voice_speed_tab2")
        voice_pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
        voice_volume = st.slider("Volume", 0.1, 1.0, 0.8, 0.1)

with tab3:
    st.subheader("ðŸ“Š Daily Voice Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**ðŸ“ˆ Today's Farm Report:**")
        
        # Generate sample daily report
        sample_farm_data = {
            'weather': {
                'condition': 'Partly Cloudy',
                'temperature': 24,
                'humidity': 68
            },
            'soil_moisture': 45,
            'alerts': [
                'Low soil moisture in Zone 3',
                'Disease risk: High humidity detected'
            ]
        }
        
        daily_report = voice_assistant.get_daily_report(sample_farm_data)
        
        st.text_area("Voice Report Text:", value=daily_report, height=150, disabled=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("ðŸ”Š Play Daily Report", use_container_width=True):
                st.success("ðŸŽµ Daily report would be played via text-to-speech")
        
        with col_b:
            if st.button("ðŸ“§ Email Report", use_container_width=True):
                st.success("ðŸ“§ Report sent to your email!")
    
    with col2:
        st.markdown("**â° Report Schedule:**")
        
        report_time = st.time_input("Daily Report Time", datetime.now().time())
        
        report_frequency = st.selectbox(
            "Report Frequency",
            ["Daily", "Twice Daily", "Weekly", "Custom"]
        )
        
        report_content = st.multiselect(
            "Include in Report:",
            [
                "Weather Summary",
                "Soil Conditions", 
                "Irrigation Status",
                "Disease Alerts",
                "Market Prices",
                "Task Reminders",
                "Equipment Status"
            ],
            default=["Weather Summary", "Soil Conditions", "Disease Alerts"]
        )
        
        if st.button("ðŸ’¾ Save Report Settings", use_container_width=True):
            st.success("âœ… Report settings saved!")
        
        st.markdown("**ðŸ“ Recent Reports:**")
        recent_reports = [
            {"date": "2024-06-12", "type": "Daily", "status": "Delivered"},
            {"date": "2024-06-11", "type": "Daily", "status": "Delivered"},
            {"date": "2024-06-10", "type": "Daily", "status": "Delivered"}
        ]
        
        for report in recent_reports:
            st.markdown(f"â€¢ **{report['date']}** - {report['type']} ({report['status']})")

with tab4:
    st.subheader("ðŸ”” Smart Audio Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**âš ï¸ Active Alerts:**")
        
        alerts = [
            {
                "type": "Critical",
                "message": "Severe water stress detected in Field A",
                "time": "10 minutes ago",
                "priority": "high"
            },
            {
                "type": "Warning", 
                "message": "Disease risk conditions in Field B",
                "time": "1 hour ago",
                "priority": "medium"
            },
            {
                "type": "Info",
                "message": "Optimal harvesting conditions predicted",
                "time": "2 hours ago", 
                "priority": "low"
            }
        ]
        
        for alert in alerts:
            priority_color = {"high": "ðŸ”´", "medium": "ðŸŸ¡", "low": "ðŸŸ¢"}
            st.markdown(f"{priority_color[alert['priority']]} **{alert['type']}:** {alert['message']}")
            st.caption(f"â° {alert['time']}")
            
            col_play, col_dismiss = st.columns(2)
            with col_play:
                if st.button(f"ðŸ”Š Play", key=f"play_{alert['message'][:10]}"):
                    st.success("ðŸŽµ Alert audio played")
            with col_dismiss:
                if st.button(f"âœ… Dismiss", key=f"dismiss_{alert['message'][:10]}"):
                    st.success("Alert dismissed")
            
            st.markdown("---")
    
    with col2:
        st.markdown("**ðŸ”§ Alert Settings:**")
        
        alert_types = st.multiselect(
            "Enable Audio Alerts For:",
            [
                "Critical System Failures",
                "Irrigation Needs",
                "Disease Outbreaks", 
                "Weather Warnings",
                "Equipment Maintenance",
                "Harvest Reminders",
                "Market Price Changes"
            ],
            default=["Critical System Failures", "Irrigation Needs", "Disease Outbreaks"]
        )
        
        alert_volume = st.slider("Alert Volume", 0.1, 1.0, 0.7, 0.1)
        alert_repeat = st.checkbox("Repeat critical alerts", True)
        quiet_hours = st.checkbox("Enable quiet hours", True)
        
        if quiet_hours:
            quiet_start = st.time_input("Quiet hours start", datetime.strptime("22:00", "%H:%M").time())
            quiet_end = st.time_input("Quiet hours end", datetime.strptime("06:00", "%H:%M").time())
        
        if st.button("ðŸ’¾ Save Alert Settings", use_container_width=True):
            st.success("âœ… Alert settings saved!")

with tab5:
    st.subheader("âš™ï¸ Assistant Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**ðŸŽ¯ AI Assistant Personality:**")
        
        personality = st.selectbox(
            "Assistant Personality",
            ["Professional Expert", "Friendly Advisor", "Technical Specialist", "Conversational Helper"]
        )
        
        expertise_focus = st.multiselect(
            "Primary Expertise Areas:",
            [
                "Crop Production",
                "Plant Pathology", 
                "Soil Science",
                "Agricultural Engineering",
                "Farm Economics",
                "Sustainable Agriculture",
                "Precision Farming"
            ],
            default=["Crop Production", "Plant Pathology", "Soil Science"]
        )
        
        response_length = st.selectbox(
            "Response Length Preference",
            ["Brief & Concise", "Detailed Explanations", "Comprehensive Analysis"]
        )
        
        include_citations = st.checkbox("Include scientific citations", False)
        multilingual_support = st.checkbox("Enable multilingual responses", True)
    
    with col2:
        st.markdown("**ðŸ”„ Learning & Adaptation:**")
        
        learning_mode = st.checkbox("Enable continuous learning", True)
        feedback_collection = st.checkbox("Collect response feedback", True)
        
        if feedback_collection:
            st.markdown("**Rate Recent Responses:**")
            
            recent_responses = [
                "Disease diagnosis for wheat rust",
                "Irrigation scheduling advice",
                "Fertilizer recommendation for corn"
            ]
            
            for response in recent_responses:
                rating = st.select_slider(
                    f"{response}:",
                    options=["Poor", "Fair", "Good", "Excellent"],
                    value="Good",
                    key=f"rating_{response[:10]}"
                )
        
        st.markdown("**ðŸ“Š Usage Statistics:**")
        st.metric("Questions Answered", "247")
        st.metric("Average Response Time", "1.2s")
        st.metric("User Satisfaction", "94%")
        
        if st.button("ðŸ”„ Reset Assistant", use_container_width=True):
            st.warning("This will reset all learning data and preferences.")
            if st.button("âš ï¸ Confirm Reset"):
                st.success("Assistant has been reset to default settings.")

# Footer with voice assistant tips
st.markdown("---")
st.markdown("""
### ðŸ’¡ Voice Assistant Tips:
- **Ask specific questions** for better responses (e.g., "My tomato leaves are yellowing, what nutrients might be lacking?")
- **Provide context** about your location, crop type, and current conditions  
- **Use follow-up questions** to get more detailed explanations
- **Enable daily reports** to stay informed about your farm conditions
- **Set up audio alerts** for critical situations that need immediate attention
""")





