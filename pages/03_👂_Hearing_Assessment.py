import streamlit as st
import numpy as np
import soundfile as sf
import io
import pandas as pd
import streamlit.components.v1 as components
import time
import json
import sys
from pathlib import Path

# Add utils to path
# Note: This might need adjustment depending on your exact file structure.
# Assuming 'utils' is one level up from the 'pages' directory where this file lives.
try:
    sys.path.append(str(Path(__file__).parent.parent / "utils"))
except Exception:
    # Handle cases where __file__ might not be defined (e.g., in some IDEs)
    pass

# Mock imports for utils/database if they are not available for standalone running
# In your real app, you'd use your actual imports
try:
    from auth import init_session_state
    from navbar import show_streamlit_navbar
    from database import MedicalDB
except ImportError:
    st.warning("Could not import custom utils (auth, navbar, database). Using mock functions.")
    
    def init_session_state():
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = True  # Mock authentication
            st.session_state.user_id = "mock_user_123" # Mock user
            st.session_state.page_name = "03_🦻_Hearing_Assessment"

    def show_streamlit_navbar():
        st.header(f"Page: {st.session_state.page_name}")
        st.markdown("---")

    class MedicalDB:
        def add_assessment(self, patient_id, assessment_type, results, risk_level, recommendations, critical_flag):
            print("--- MOCK DB SAVE ---")
            print(f"Patient ID: {patient_id}")
            print(f"Type: {assessment_type}")
            print(f"Results: {results}")
            print(f"Risk: {risk_level}")
            print(f"Rec: {recommendations}")
            print(f"Critical: {critical_flag}")
            print("----------------------")


st.set_page_config(page_title="Online Hearing Test", page_icon="👂", layout="wide")

def save_assessment_result(assessment_type, results, risk_level):
    """Save assessment results to database"""
    try:
        db = MedicalDB()
        user_id = st.session_state.get('user_id')
        
        if not user_id:
            st.error("User not authenticated. Please log in.")
            return False
        
        # Determine if critical based on results
        critical_flag = False
        if risk_level == "Significant":
            critical_flag = True
        
        # Create recommendations based on risk level
        if risk_level == "Normal":
            recommendations = "Your hearing is within normal limits. Continue to protect your hearing from loud noises."
        elif risk_level == "Mild":
            recommendations = "Mild hearing changes detected. Consider a professional audiological evaluation for further assessment."
        else:  # Significant
            recommendations = "Significant hearing loss detected. Please consult an audiologist as soon as possible for comprehensive evaluation and treatment options."
            
        # Save to database
        db.add_assessment(
            patient_id=user_id,
            assessment_type=assessment_type,
            results=json.dumps(results),
            risk_level=risk_level,
            recommendations=recommendations,
            critical_flag=critical_flag
        )
        
        st.success("Assessment results saved successfully!")
        return True
        
    except Exception as e:
        st.error(f"Error saving results: {str(e)}")
        return False

def main():
    # Initialize session state
    init_session_state()
    
    # Set current page name for navbar
    st.session_state.page_name = "03_🦻_Hearing_Assessment"
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.error("Please login first!")
        # Mock st.switch_page if not available
        if hasattr(st, 'switch_page'):
            st.switch_page("streamlit_app.py")
        else:
            st.warning("Mocking st.switch_page. Please login and navigate here.")
        return
    
    # Show navbar
    show_streamlit_navbar()

    # --- Custom CSS ---
    st.markdown("""
    <style>
        .stApp { 
            background-color: #fcfcff; 
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Progress Bar Styling */
        .progress-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            margin: 1rem auto 3rem auto; 
            max-width: 600px; 
        }
        .progress-step { 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            flex: 1; 
            position: relative; 
        }
        .progress-icon-container { 
            width: 40px; 
            height: 40px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            font-weight: bold; 
            margin-bottom: 10px; 
            border: 2px solid #e0e0e0; 
            background-color: white; 
            color: #ccc; 
            z-index: 2; 
            font-size: 16px;
        }
        .progress-icon-container.active { 
            border-color: #d32f2f; 
            color: #d32f2f; 
            background-color: #fff5f5;
        }
        .progress-icon-container.completed { 
            border-color: #4caf50; 
            background-color: #4caf50; 
            color: white; 
        }
        .progress-line { 
            position: absolute; 
            top: 20px; 
            width: calc(100% - 40px); 
            height: 2px; 
            background-color: #e0e0e0; 
            z-index: 1; 
            left: 20px; 
        }
        .progress-step:first-child .progress-line { 
            display: none; 
        }
        .progress-line.completed { 
            background-color: #4caf50; 
        }
        .progress-label { 
            font-size: 14px; 
            color: #999; 
            text-align: center; 
        }
        .progress-label.active { 
            color: #d32f2f; 
            font-weight: bold; 
        }
        .progress-label.completed { 
            color: #4caf50; 
            font-weight: bold; 
        }
        
        /* Frequency control panel */
        .frequency-control-panel { 
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 2rem;
            margin: 2rem 0;
            border: 2px solid #f0f2f6;
        }
        
        /* Frequency adjuster styling */
        .freq-adjuster-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            margin: 2rem 0;
            padding: 1.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            color: white;
        }
        
        /* Control buttons */
        .freq-btn .stButton > button {
            background-color: white !important;
            color: #667eea !important;
            border-radius: 50% !important;
            width: 60px !important;
            height: 60px !important;
            font-size: 24px !important;
            font-weight: bold !important;
            border: 2px solid white !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
        }
        .freq-btn .stButton > button:hover {
            background-color: #f0f2f6 !important;
            transform: scale(1.1);
            box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
        }
        
        /* Navigation Buttons */
        .stButton > button[kind="primary"] { 
            background-color: #d32f2f !important; 
            border: 1px solid #d32f2f !important; 
            border-radius: 25px !important; 
            padding: 0.75rem 2rem !important; 
            width: 150px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #b71c1c !important;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(211, 47, 47, 0.3);
        }
        .stButton > button[kind="secondary"] { 
            background-color: white !important; 
            border: 2px solid #ddd !important; 
            color: #666 !important; 
            border-radius: 25px !important; 
            padding: 0.75rem 2rem !important; 
            width: 150px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button[kind="secondary"]:hover {
            border-color: #999 !important;
            color: #333 !important;
            transform: translateY(-2px);
        }
        
        .nav-buttons { 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            margin-top: 4rem; 
            border-top: 1px solid #eee; 
            padding-top: 2rem; 
        }
        
        /* Frequency display */
        .frequency-display {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem auto;
            max-width: 500px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }
        
        /* Instruction cards */
        .instruction-item {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        .instruction-item:hover {
            transform: translateY(-2px);
        }
        
        /* Results cards */
        .result-card {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: transform 0.2s ease;
        }
        .result-card:hover {
            transform: translateY(-3px);
        }
        
        /* Audio controls */
        .audio-controls {
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .hearing-level-info {
            background: linear-gradient(45deg, #e8f5e8, #f0f8ff);
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
            border-left: 4px solid #4caf50;
        }
        
        /* Audio status indicator */
        .audio-status {
            background: #e3f2fd;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
            border-left: 4px solid #2196f3;
        }
        
        /* Slider customization */
        .stSlider > div > div > div > div {
            background-color: #667eea !important;
        }
        
        /* Volume indicator */
        .volume-indicator {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-weight: bold;
            margin: 0 1rem;
            min-width: 100px;
            text-align: center;
        }
        
        /* Ear completion results table */
        .ear-results-table {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        /* Final results completion styling */
        .completion-card {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
        }
        
        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin: 3rem 0;
        }
        
        .action-btn {
            background: white;
            color: #4caf50;
            border: 2px solid #4caf50;
            padding: 1rem 2rem;
            border-radius: 10px;
            font-weight: bold;
            text-decoration: none;
            transition: all 0.3s ease;
        }
        
        .action-btn:hover {
            background: #4caf50;
            color: white;
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)

    # --- App Logic ---
    st.title("👂 Online Hearing Test")

    # Initialize session state
    if 'test_phase' not in st.session_state:
        st.session_state.test_phase = 'introduction'
        st.session_state.questionnaire_data = {}
        st.session_state.left_ear_results = {}
        st.session_state.right_ear_results = {}

    phases = ['Introduction', 'Left Ear', 'Right Ear', 'Results']
    phase_map = {'introduction': 0, 'left_ear': 1, 'right_ear': 2, 'results': 3}
    current_phase_index = phase_map.get(st.session_state.test_phase, 0)

    create_progress_indicator(phases, current_phase_index)

    # Route to appropriate page
    if st.session_state.test_phase == 'introduction':
        show_introduction()
    elif st.session_state.test_phase == 'left_ear':
        show_ear_test('left')
    elif st.session_state.test_phase == 'right_ear':
        show_ear_test('right')
    elif st.session_state.test_phase == 'results':
        show_results()

def create_progress_indicator(phases, current_index):
    """Creates a visual progress indicator for the test phases."""
    icons = ['📋', '👂', '👂', '📊']
    progress_html = '<div class="progress-container">'
    
    for i, phase in enumerate(phases):
        state = "inactive"
        if i < current_index:
            state = "completed"
            icon = "✅"
        elif i == current_index:
            state = "active"
            icon = icons[i]
        else:
            icon = icons[i]
        
        line_state = "completed" if i < current_index else ""
        
        progress_html += f'''
            <div class="progress-step">
                <div class="progress-line {line_state}"></div>
                <div class="progress-icon-container {state}">{icon}</div>
                <div class="progress-label {state}">{phase}</div>
            </div>
        '''
    progress_html += '</div>'
    
    # Use st.html() for modern Streamlit versions
    if hasattr(st, 'html'):
        st.html(progress_html)
    else:
        st.markdown(progress_html, unsafe_allow_html=True)

def show_introduction():
    """Shows the introduction screen with instructions."""
    st.markdown("<h2 style='text-align:center; margin-bottom: 40px; color: #333;'>Get Ready for Your Test</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#666; font-size: 18px;'>Follow these steps for the most accurate results.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("""
        <div style='text-align: center; padding: 3rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-bottom: 2rem;'>
            <div style='font-size: 80px; margin-bottom: 1rem;'>🏠</div>
            <p style='font-size: 18px; font-weight: 500; color: #555;'><strong>Find a quiet, comfortable space</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        items = [
            ("🔇", "Find somewhere quiet", "with as little background noise as possible."),
            ("🎧", "Use headphones", "for accurate results for each ear."),
            ("🎵", "Adjust hearing level", "Find the minimum level where you can just hear the tone.")
        ]
        
        for icon, title, subtitle in items:
            st.markdown(f'''
            <div class="instruction-item">
                <div style='display:flex; align-items:center;'>
                    <div style='font-size:40px; margin-right:1.5rem; min-width: 60px;'>{icon}</div>
                    <div>
                        <div style='font-weight:bold; font-size:18px; color: #333;'>{title}</div>
                        <div style='color:#666; margin-top: 5px;'>{subtitle}</div>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)

    st.info("**Disclaimer:** This is a hearing screening, not a medical diagnosis. For accurate diagnosis, please consult an audiologist.", icon="⚠️")
    
    # Navigation
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4, 1, 1])
    with col2:
        st.button("Back", key="intro_back", type="secondary", disabled=True)
    with col3:
        if st.button("Continue", type="primary", key="intro_continue"):
            st.session_state.test_phase = 'left_ear'
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_ear_test(ear_side):
    """Shows the simplified ear test interface for left or right ear - single audio test."""
    test_key = f'{ear_side}_ear_test'
    if test_key not in st.session_state:
        st.session_state[test_key] = {
            'audio_playing': False,
            'last_audio_update': 0,
            'current_audio_data': None,
            'completed': False
        }
    
    test_state = st.session_state[test_key]
    
    if test_state['completed']:
        show_ear_test_completion(ear_side, test_state)
    else:
        show_single_audio_test(ear_side, test_state)

def show_single_audio_test(ear_side, test_state):
    """Show the single audio test interface for an ear."""
    # Use a standard test frequency (1000 Hz is commonly used for hearing screening)
    test_frequency = 1000
    hearing_level_key = f'hearing_level_{ear_side}'
    audio_key = f'audio_{ear_side}'
    
    # ***CORRECTED: Indentation fixed***
    # Initialize hearing level (starts at 0 dB HL - silent)
    if hearing_level_key not in st.session_state:
        st.session_state[hearing_level_key] = 0

    # Header
    st.markdown(
        f"<h2 style='text-align:center; font-weight:400; color: #333; margin-bottom: 1rem;'>"
        f"<span style='color:#d32f2f; font-weight:700;'>{ear_side.title()} Ear</span> Hearing Test"
        "</h2>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align:center; color:#888; margin-bottom: 2rem;'>Adjust the hearing level until you can just barely hear the tone</p>", unsafe_allow_html=True)

    # ***CORRECTED: Default value changed from 25 to 0***
    # Current test info
    current_hearing_level = st.session_state.get(hearing_level_key, 0)
    
    st.markdown(f'''
    <div class="frequency-display">
        <h3 style='margin: 0; font-size: 28px;'>{ear_side.title()} Ear Test</h3>
        <p style='margin: 0.5rem 0; font-size: 20px; opacity: 0.9;'>Testing: {test_frequency} Hz</p>
        <p style='margin: 0.5rem 0; font-size: 18px; opacity: 0.8;'>Hearing Level: {current_hearing_level} dB HL</p>
    </div>
    ''', unsafe_allow_html=True)

    # Hearing Level Control Panel
    st.markdown('<div class="frequency-control-panel">', unsafe_allow_html=True)
    st.markdown("### 🔊 Hearing Level Adjuster (dB HL)")
    
    # Create control layout
    col1, col2, col3 = st.columns([1, 8, 1])
    
    with col1:
        st.markdown('<div class="freq-btn">', unsafe_allow_html=True)
        if st.button("−5", key=f"dec_{hearing_level_key}", help="Decrease hearing level"):
            new_level = max(0, current_hearing_level - 5)
            st.session_state[hearing_level_key] = new_level
            # Pass ear_side
            update_audio_if_playing(test_state, test_frequency, new_level, ear_side, audio_key)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        # Volume display and slider container
        st.markdown('<div class="freq-adjuster-container">', unsafe_allow_html=True)
        subcol1, subcol2, subcol3 = st.columns([1, 6, 1])
        
        with subcol1:
            st.markdown(f'<div class="volume-indicator">0</div>', unsafe_allow_html=True)
        
        with subcol2:
            new_hearing_level = st.slider(
                f"Hearing Level", 
                0, 100, 
                current_hearing_level, 
                step=5,
                key=f"hl_slider_{hearing_level_key}", 
                label_visibility="collapsed",
                help="Adjust the hearing level until you can just hear the tone"
            )
        
        with subcol3:
            st.markdown(f'<div class="volume-indicator">100</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
            
    with col3:
        st.markdown('<div class="freq-btn">', unsafe_allow_html=True)
        if st.button("+5", key=f"inc_{hearing_level_key}", help="Increase hearing level"):
            new_level = min(100, current_hearing_level + 5)
            st.session_state[hearing_level_key] = new_level
            # Pass ear_side
            update_audio_if_playing(test_state, test_frequency, new_level, ear_side, audio_key)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Update hearing level if slider changed
    if new_hearing_level != current_hearing_level:
        st.session_state[hearing_level_key] = new_hearing_level
        # Pass ear_side
        update_audio_if_playing(test_state, test_frequency, new_hearing_level, ear_side, audio_key)

    # Show hearing level interpretation
    interpretation, color = get_hearing_interpretation(new_hearing_level)
    
    st.markdown(f'''
    <div class="hearing-level-info">
        🎯 <strong>Current Level:</strong> {new_hearing_level} dB HL<br>
        📊 <strong>Classification:</strong> <span style="color: {color}; font-weight: bold;">{interpretation}</span><br>
        💡 <strong>Goal:</strong> Find the minimum level where you can just detect the tone
    </div>
    ''', unsafe_allow_html=True)

    # Audio controls
    st.markdown('<div class="audio-controls">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if not test_state['audio_playing']:
            if st.button("🔊 Play Test Tone", key=f"start_{audio_key}", type="primary", use_container_width=True):
                # Pass ear_side
                audio_data = generate_hearing_level_tone(test_frequency, new_hearing_level, ear_side, duration=3.0)
                if audio_data:
                    test_state['current_audio_data'] = audio_data
                    test_state['audio_playing'] = True
                    test_state['last_audio_update'] = time.time()
                    st.rerun()
                else:
                    st.error("Failed to generate audio tone.")
        else:
            # Show audio status
            if new_hearing_level > 0:
                st.markdown(f'<div class="audio-status">🎵 <strong>Tone is playing in {ear_side} ear...</strong><br>Adjust the level to find your hearing threshold</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="audio-status">🔇 <strong>Tone is silent</strong><br>Increase the hearing level to hear the tone</div>', unsafe_allow_html=True)
                
            if st.button("⏹️ Stop Tone", key=f"stop_{audio_key}", type="secondary", use_container_width=True):
                test_state['audio_playing'] = False
                test_state['current_audio_data'] = None
                st.rerun()
            
    st.markdown('</div>', unsafe_allow_html=True)

    # Play the audio if active
    if test_state['audio_playing'] and test_state['current_audio_data']:
        try:
            st.audio(test_state['current_audio_data'], format='audio/wav', autoplay=True, loop=True)
        except Exception as e:
            st.error(f"Error playing audio: {str(e)}")
            test_state['audio_playing'] = False

    # Instructions (Updated based on last request)
    st.markdown(f'''
    <div style='text-align:center; background:#f8f9fa; padding:1.5rem; border-radius:12px; margin:2rem 0;'>
        <p style='margin: 0; color:#666; font-size: 16px;'>
            <strong>Instructions:</strong> 
            <br>1. Click "Play Test Tone" to start the audio
            <br>2. The test will start at <strong>0 dB</strong> (silent)
            <br>3. <strong>Slowly increase</strong> the level until you can *just barely* hear the tone
            <br>4. This is your hearing threshold. Click "Continue"
        </p>
    </div>
    ''', unsafe_allow_html=True)

    # Navigation
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4, 1, 1])
    with col2:
        if st.button("Back", key=f"{ear_side}_back", type="secondary"):
            test_state['audio_playing'] = False
            test_state['current_audio_data'] = None
                
            if ear_side == 'left':
                st.session_state.test_phase = 'introduction'
            else:
                st.session_state.test_phase = 'left_ear'
            st.rerun()
    with col3:
        if st.button("Continue", key=f"{ear_side}_continue", type="primary"):
            test_state['audio_playing'] = False
            test_state['current_audio_data'] = None
            
            # Save the hearing threshold
            result_data = {
                'hearing_threshold_db': new_hearing_level,
                'classification': interpretation,
                'test_frequency': test_frequency
            }
            
            # Save to session state
            if ear_side == 'left':
                st.session_state.left_ear_results = result_data
            else:
                st.session_state.right_ear_results = result_data
                
            test_state['completed'] = True
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_ear_test_completion(ear_side, test_state):
    """Shows completion screen for an ear test with results."""
    st.success(f"✅ {ear_side.title()} ear test completed!")
    
    # Get the results
    if ear_side == 'left':
        result_data = st.session_state.left_ear_results
    else:
        result_data = st.session_state.right_ear_results
    
    if result_data:
        threshold = result_data['hearing_threshold_db']
        classification = result_data['classification']
        test_freq = result_data.get('test_frequency', 1000)
        
        # Calculate score (lower threshold = better hearing = higher score)
        score = max(0, 100 - threshold)
        
        # Get color based on classification
        _, color = get_hearing_interpretation(threshold)
        
        # Summary card
        st.markdown(f'''
        <div class="result-card" style="border-left-color: {color}; margin: 2rem 0;">
            <h3 style='color: {color}; margin: 0 0 1rem 0;'>{ear_side.title()} Ear Results</h3>
            <p style='font-size: 32px; font-weight: bold; margin: 1rem 0; color: {color};'>{int(score)}%</p>
            <p style='margin: 0; color: #666; font-size: 16px;'>{classification}</p>
            <p style='margin: 0.5rem 0 0 0; color: #888; font-size: 14px;'>Threshold: {threshold} dB HL at {test_freq} Hz</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Detailed results
        with st.expander(f"📊 Detailed Results for {ear_side.title()} Ear", expanded=True):
            st.markdown('<div class="ear-results-table">', unsafe_allow_html=True)
            
            # Create results display
            st.markdown(f'''
            <div style='background: #f8f9fa; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='margin: 0 0 1rem 0; color: #333;'>Test Results Summary</h4>
                <p><strong>Test Frequency:</strong> {test_freq} Hz</p>
                <p><strong>Hearing Threshold:</strong> {threshold} dB HL</p>
                <p><strong>Classification:</strong> <span style='color: {color}; font-weight: bold;'>{classification}</span></p>
                <p><strong>Hearing Score:</strong> {int(score)}%</p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('''
            <div style='background: #f0f2f6; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                <p style='margin: 0; color: #666; font-size: 14px;'>
                    <strong>Interpretation:</strong><br>
                    • Lower thresholds indicate better hearing sensitivity<br>
                    • 0-20 dB HL: Normal hearing<br>
                    • 21-40 dB HL: Mild hearing loss<br>  
                    • 41+ dB HL: More significant hearing loss
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Determine next step
    if ear_side == 'left':
        next_phase = 'right_ear'
        next_text = "Test Right Ear"
    else:
        next_phase = 'results'
        next_text = "View Final Results"
    
    st.info(f"Your {ear_side} ear results have been saved. Click '{next_text}' to continue.", icon="💾")
    
    # Navigation
    st.markdown('<div class="nav-buttons">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4, 1, 1])
    with col2:
        if st.button("Back", key=f"{ear_side}_completion_back", type="secondary"):
            # Reset this ear's test to allow retesting
            test_state['completed'] = False
            st.rerun()
    with col3:
        if st.button(next_text, type="primary", key=f"{ear_side}_next"):
            st.session_state.test_phase = next_phase
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def show_results():
    """Shows the final results screen."""
    st.markdown("<h2 style='text-align:center; color: #333; margin-bottom: 2rem;'>🎉 Your Hearing Test Results</h2>", unsafe_allow_html=True)
    
    left_results = st.session_state.left_ear_results
    right_results = st.session_state.right_ear_results

    # Analyze results
    left_score, left_status, left_color = analyze_single_ear_results(left_results)
    right_score, right_status, right_color = analyze_single_ear_results(right_results)
    overall_score = (left_score + right_score) // 2 if left_score is not None and right_score is not None else 0

    # Determine overall color and risk level
    if overall_score >= 80:
        overall_color = "#4caf50"
        risk_level = "Normal"
    elif overall_score >= 60:
        overall_color = "#ff9800"
        risk_level = "Mild"
    else:
        overall_color = "#f44336"
        risk_level = "Significant"

    # Results cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f'''
        <div class="result-card" style="border-left-color: {left_color};">
            <h3 style='color: {left_color}; margin: 0;'>Left Ear</h3>
            <p style='font-size: 32px; font-weight: bold; margin: 1rem 0; color: {left_color};'>{left_score if left_score is not None else "N/A"}%</p>
            <p style='margin: 0; color: #666; font-size: 16px;'>{left_status}</p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col2:
        st.markdown(f'''
        <div class="result-card" style="border-left-color: {right_color};">
            <h3 style='color: {right_color}; margin: 0;'>Right Ear</h3>
            <p style='font-size: 32px; font-weight: bold; margin: 1rem 0; color: {right_color};'>{right_score if right_score is not None else "N/A"}%</p>
            <p style='margin: 0; color: #666; font-size: 16px;'>{right_status}</p>
        </div>
        ''', unsafe_allow_html=True)
        
    with col3:
        st.markdown(f'''
        <div class="result-card" style="border-left-color: {overall_color};">
            <h3 style='color: {overall_color}; margin: 0;'>Overall</h3>
            <p style='font-size: 32px; font-weight: bold; margin: 1rem 0; color: {overall_color};'>{overall_score}%</p>
            <p style='margin: 0; color: #666; font-size: 16px;'>Hearing Score</p>
        </div>
        ''', unsafe_allow_html=True)

    # Recommendations
    st.markdown("<br>", unsafe_allow_html=True)
    
    if overall_score >= 80:
        st.success("**Normal Hearing Detected!** Your hearing thresholds are within normal limits. Continue to protect your hearing from loud noises.", icon="🎉")
    elif overall_score >= 60:
        st.warning("**Mild Hearing Changes Detected.** Your results suggest some hearing threshold elevation. Consider a professional audiological evaluation.", icon="⚠️")
    else:
        st.error("**Significant Hearing Loss Detected.** Your results suggest hearing loss that may benefit from professional treatment. Please consult an audiologist.", icon="🚨")

    # Detailed breakdown
    with st.expander("📊 Show Detailed Results", expanded=False):
        if left_results and right_results:
            # Create comparison table
            st.markdown('<div class="ear-results-table">', unsafe_allow_html=True)
            
            left_threshold = left_results.get('hearing_threshold_db', 'N/A')
            left_class = left_results.get('classification', 'Not tested')
            left_freq = left_results.get('test_frequency', 1000)
            
            right_threshold = right_results.get('hearing_threshold_db', 'N/A')
            right_class = right_results.get('classification', 'Not tested')
            right_freq = right_results.get('test_frequency', 1000)
            
            data = [{
                'Ear': 'Left Ear',
                'Test Frequency (Hz)': f"{left_freq} Hz",
                'Threshold (dB HL)': left_threshold,
                'Classification': left_class,
                'Score': f"{left_score}%"
            }, {
                'Ear': 'Right Ear', 
                'Test Frequency (Hz)': f"{right_freq} Hz",
                'Threshold (dB HL)': right_threshold,
                'Classification': right_class,
                'Score': f"{right_score}%"
            }]
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown('''
            <div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-top: 1rem;'>
                <p style='margin: 0; color: #666; font-size: 14px;'>
                    <strong>Results Interpretation:</strong><br>
                    • <strong>0-20 dB HL:</strong> Normal hearing<br>
                    • <strong>21-40 dB HL:</strong> Mild hearing loss<br>  
                    • <strong>41-70 dB HL:</strong> Moderate hearing loss<br>
                    • <strong>71-90 dB HL:</strong> Severe hearing loss<br>
                    • <strong>90+ dB HL:</strong> Profound hearing loss<br><br>
                    <strong>Note:</strong> This test uses 1000 Hz as the standard test frequency for hearing screening.
                </p>
            </div>
            ''', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Complete the test for both ears to see detailed results.")

    # Save results to database
    results_data = {
        "left_ear": left_results, 
        "right_ear": right_results,
        "overall_score": overall_score,
        "test_date": str(pd.Timestamp.now().date()),
        "left_threshold": left_results.get('hearing_threshold_db', 'N/A'),
        "right_threshold": right_results.get('hearing_threshold_db', 'N/A'),
        "left_classification": left_results.get('classification', 'Not tested'),
        "right_classification": right_results.get('classification', 'Not tested')
    }
    
    # Save assessment result to database
    save_result = save_assessment_result("Online Hearing Test", results_data, risk_level)
    
    # Completion card with database save status
    if save_result:
        st.markdown('''
        <div class="completion-card">
            <h3 style='margin: 0 0 1rem 0;'>✅ Assessment Complete!</h3>
            <p style='margin: 0; font-size: 18px; opacity: 0.9;'>Your hearing test results have been saved to your medical record.</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.warning("Assessment completed but there was an issue saving your results. Please contact support if this persists.")
    
    # Navigation options with report generation and cross-navigation
    st.markdown('<div class="action-buttons">', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Mocking st.switch_page for standalone
    def mock_switch_page(page_name):
        st.success(f"Mock navigation: Would switch to {page_name}")
        
    switch_page = st.switch_page if hasattr(st, 'switch_page') else mock_switch_page

    with col1:
        if st.button("👁️ Continue to Eye Assessment", type="primary", key="continue_eye", use_container_width=True):
            reset_test_session()
            switch_page("pages/02_👁️_Eye_Assessment.py")
    
    with col2:
        if st.button("📄 Generate Report", key="generate_hearing_report", use_container_width=True):
            if save_result:
                st.success("✅ Hearing assessment report already generated and saved!")
                st.info("📋 You can download your report from your Profile page.")
            else:
                st.error("❌ Please complete the test first before generating a report.")
    
    with col3:
        if st.button("📊 View Results History", key="view_results_history", use_container_width=True):
            reset_test_session()
            switch_page("pages/04_📊_Results_History.py")
    
    with col4:
        if st.button("🔄 Test Again", key="test_again", use_container_width=True):
            reset_test_session()
            st.rerun()
    
    with col5:
        if st.button("← Back to Tests", key="back_from_hearing", use_container_width=True):
            reset_test_session()
            switch_page("pages/01_🏠_Home.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show celebration
    if save_result:
        st.balloons()

def analyze_single_ear_results(results):
    """Analyze single ear test results and return score, status, and color."""
    if not results: 
        return None, "Not Tested", "#999"
    
    # Get hearing threshold
    threshold = results.get('hearing_threshold_db', 0)
    
    # Score based on hearing threshold (lower threshold = better hearing = higher score)
    score = max(0, 100 - threshold)
    
    if threshold <= 20:
        return int(score), "Normal Hearing", "#4caf50"
    elif threshold <= 40:
        return int(score), "Mild Hearing Loss", "#ff9800"
    elif threshold <= 70:
        return int(score), "Moderate Hearing Loss", "#f44336"
    elif threshold <= 90:
        return int(score), "Severe Hearing Loss", "#d32f2f"
    else:
        return int(score), "Profound Hearing Loss", "#8e24aa"

def get_hearing_interpretation(hearing_level):
    """Get hearing interpretation based on dB HL level."""
    if hearing_level <= 20:
        return "Normal Hearing", "#4caf50"
    elif hearing_level <= 40:
        return "Mild Hearing Loss", "#ff9800"
    elif hearing_level <= 70:
        return "Moderate Hearing Loss", "#f44336"
    elif hearing_level <= 90:
        return "Severe Hearing Loss", "#d32f2f"
    else:
        return "Profound Hearing Loss", "#8e24aa"

def update_audio_if_playing(test_state, frequency, hearing_level, ear_side, audio_key):
    """Update audio if currently playing and enough time has passed."""
    if (test_state['audio_playing'] and 
        time.time() - test_state.get('last_audio_update', 0) > 0.3):  # Rate limit updates
        try:
            # Pass 'ear_side' to the generator
            new_audio_data = generate_hearing_level_tone(frequency, hearing_level, ear_side, duration=3.0)
            if new_audio_data:
                test_state['current_audio_data'] = new_audio_data
                test_state['last_audio_update'] = time.time()
        except Exception as e:
            print(f"Error updating audio: {str(e)}")

def reset_test_session():
    """Reset all test session data."""
    keys_to_reset = [
        'test_phase', 'questionnaire_data', 'left_ear_results', 'right_ear_results', 
        'left_ear_test', 'right_ear_test'
    ]
    other_keys = [k for k in st.session_state.keys() if k.startswith(('hearing_level_', 'audio_'))]
    for key in keys_to_reset + other_keys:
        if key in st.session_state: 
            del st.session_state[key]

def generate_hearing_level_tone(frequency, hearing_level_db, ear_side, duration=3.0):
    """
    Generate a tone at a specific hearing level (dB HL) for a specific ear.
    
    Args:
        frequency (int): Frequency in Hz
        hearing_level_db (int): Hearing level in dB HL (0-100)
        ear_side (str): 'left' or 'right'
        duration (float): Duration in seconds
    
    Returns:
        BytesIO: WAV audio data or None if error
    """
    try:
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        
        # Convert hearing level to amplitude
        if hearing_level_db <= 0:
            amplitude = 0.0  # Silent
        else:
            # Exponential mapping for more realistic hearing level simulation
            # Map 0-100 dB HL to 0-0.7 amplitude (avoid clipping)
            normalized_db = min(100, max(0, hearing_level_db))
            amplitude = (normalized_db / 100.0) ** 0.4 * 0.7
        
        # Generate pure tone
        tone = np.sin(2 * np.pi * frequency * t)
        
        # Apply amplitude and envelope
        audio_signal = np.zeros_like(tone) # Start with silence
        
        if amplitude > 0:
            # Create smooth envelope to prevent clicks
            fade_samples = int(0.02 * sample_rate)  # 20ms fade
            envelope = np.ones(len(t))
            
            if len(t) > 2 * fade_samples:
                # Smooth fade in/out using raised cosine
                fade_in = 0.5 * (1 - np.cos(np.pi * np.arange(fade_samples) / fade_samples))
                fade_out = 0.5 * (1 + np.cos(np.pi * np.arange(fade_samples) / fade_samples))
                envelope[:fade_samples] = fade_in
                envelope[-fade_samples:] = fade_out
            
            audio_signal = amplitude * envelope * tone
        
        # --- Create Stereo Signal ---
        # Create a 2-channel array (shape: [samples, 2])
        stereo_signal = np.zeros((len(t), 2))
        
        if ear_side == 'left':
            stereo_signal[:, 0] = audio_signal  # Put signal in Left channel (index 0)
        elif ear_side == 'right':
            stereo_signal[:, 1] = audio_signal  # Put signal in Right channel (index 1)
        
        # Normalize to prevent clipping
        if np.max(np.abs(stereo_signal)) > 0:
            max_val = np.max(np.abs(stereo_signal))
            if max_val > 0.95:
                stereo_signal = stereo_signal * 0.95 / max_val
        
        # Convert to 16-bit PCM
        audio_data = np.clip(stereo_signal * 32767, -32767, 32767).astype(np.int16)
        
        # Create WAV file in memory
        buffer = io.BytesIO()
        sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"Error in generate_hearing_level_tone: {str(e)}")
        return None

if __name__ == "__main__":
    main()