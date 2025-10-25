import streamlit as st
from pathlib import Path
import sys

# Page config must be the FIRST Streamlit command
st.set_page_config(page_title="Home", page_icon="🏠", layout="wide")

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from auth import init_session_state
from navbar import show_streamlit_navbar

# Custom CSS for professional red and white theme
def load_custom_css():
    st.markdown("""
    <style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #ffffff 0%, #fff5f5 100%);
        min-height: 100vh;
    }
    
    /* Welcome header styling */
    .welcome-header {
        text-align: center;
        padding: 2.5rem 2rem;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        border-radius: 16px;
        margin-bottom: 2.5rem;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.25);
        animation: fadeInDown 0.8s ease-out;
    }
    
    .welcome-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .welcome-header p {
        font-size: 1.1rem;
        font-weight: 400;
        opacity: 0.95;
    }
    
    /* Stats card styling */
    .stats-container {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1.5rem;
        margin-bottom: 2.5rem;
    }
    
    .stats-card {
        background: white;
        border-radius: 12px;
        padding: 1.8rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border-top: 3px solid #dc2626;
        transition: all 0.3s ease;
        animation: fadeInUp 0.6s ease-out;
    }
    
    .stats-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(220, 38, 38, 0.15);
    }
    
    .stats-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        display: inline-block;
    }
    
    .stats-card h3 {
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 0.5rem 0 0.3rem 0;
    }
    
    .stats-card p {
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0;
        font-weight: 400;
    }
    
    /* Assessment options container */
    .assessment-options {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2rem;
        margin: 2rem 0;
    }
    
    /* Assessment option cards */
    .assessment-option {
        background: white;
        border: 2px solid #fee2e2;
        border-radius: 16px;
        padding: 2rem 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .assessment-option::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(220, 38, 38, 0.05), transparent);
        transition: left 0.6s;
    }
    
    .assessment-option:hover::before {
        left: 100%;
    }
    
    .assessment-option:hover {
        border-color: #dc2626;
        transform: translateY(-6px);
        box-shadow: 0 12px 28px rgba(220, 38, 38, 0.2);
    }
    
    .option-icon {
        font-size: 3.5rem;
        margin-bottom: 1rem;
        display: inline-block;
        transition: transform 0.3s ease;
        filter: grayscale(0);
    }
    
    .assessment-option:hover .option-icon {
        transform: scale(1.08);
    }
    
    .option-title {
        color: #1f2937;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1rem 0 0.5rem 0;
        letter-spacing: -0.3px;
    }
    
    .option-description {
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
        font-weight: 400;
    }
    
    .option-features {
        text-align: left;
        margin: 1.2rem 0;
        padding: 1rem;
        background: #fef2f2;
        border-radius: 8px;
        font-size: 0.88rem;
        line-height: 1.7;
    }
    
    .option-features strong {
        color: #dc2626;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .option-features ul {
        margin: 0.5rem 0 0 0;
        padding-left: 1.2rem;
        list-style: none;
    }
    
    .option-features li {
        color: #374151;
        margin: 0.3rem 0;
        position: relative;
        padding-left: 0.3rem;
    }
    
    .option-features li::before {
        content: "•";
        color: #dc2626;
        font-weight: bold;
        position: absolute;
        left: -0.8rem;
    }
    
    .option-duration {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 0.6rem 1.2rem;
        border-radius: 20px;
        font-weight: 600;
        display: inline-block;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    
    /* Section headers */
    .section-header {
        color: #1f2937;
        font-size: 1.8rem;
        font-weight: 700;
        margin: 2.5rem 0 1.5rem 0;
        text-align: center;
        letter-spacing: -0.5px;
    }
    
    .section-header::before {
        content: "";
        display: block;
        width: 60px;
        height: 4px;
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        margin: 0 auto 1rem auto;
        border-radius: 2px;
    }
    
    /* Animation keyframes */
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Tips section */
    .tips-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .tip-card {
        background: white;
        border-left: 4px solid #dc2626;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .tip-card h4 {
        color: #dc2626;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    
    .tip-card ul {
        list-style: none;
        padding: 0;
        margin: 0;
    }
    
    .tip-card li {
        color: #374151;
        font-size: 0.95rem;
        margin: 0.5rem 0;
        padding-left: 1.5rem;
        position: relative;
    }
    
    .tip-card li::before {
        content: "✓";
        color: #dc2626;
        font-weight: bold;
        position: absolute;
        left: 0;
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #fee2e2, transparent);
        margin: 2.5rem 0;
        border: none;
    }
    
    /* Recent assessments */
    .assessment-history-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #dc2626;
    }
    </style>
    """, unsafe_allow_html=True)

def show_assessment_stats():
    """Show platform statistics with professional icons"""
    stats_html = """
    <div class="stats-container">
        <div class="stats-card">
            <div class="stats-icon">👁️</div>
            <h3>Eye Health</h3>
            <p>AI-Powered Detection</p>
        </div>
        <div class="stats-card">
            <div class="stats-icon">👂</div>
            <h3>Hearing Test</h3>
            <p>Comprehensive Analysis</p>
        </div>
        <div class="stats-card">
            <div class="stats-icon">⚡</div>
            <h3>Quick Results</h3>
            <p>Instant Analysis</p>
        </div>
        <div class="stats-card">
            <div class="stats-icon">🏥</div>
            <h3>Medical Grade</h3>
            <p>Professional Quality</p>
        </div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

def show_assessment_options():
    """Show direct assessment options"""
    st.markdown('<div class="section-header">Choose Your Health Assessment</div>', unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6b7280; margin-bottom: 2rem;'>Select an assessment to begin your health screening journey</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        eye_card_html = """
        <div class="assessment-option">
            <div class="option-icon">👁️</div>
            <div class="option-title">Eye Assessment</div>
            <div class="option-description">Comprehensive eye health evaluation</div>
            <div class="option-features">
                <strong>🔍 What's Included:</strong>
                <ul>
                    <li>Diabetic Retinopathy Detection</li>
                    <li>Glaucoma Risk Assessment</li>
                    <li>Cataract Analysis</li>
                    <li>Visual Acuity Testing</li>
                    <li>AI-Powered Diagnosis</li>
                </ul>
            </div>
            <div class="option-duration">⏱️ 10-15 minutes</div>
        </div>
        """
        st.markdown(eye_card_html, unsafe_allow_html=True)
        
        if st.button("Start Eye Assessment", key="eye_assessment", type="primary", use_container_width=True):
            st.session_state["assessment_choice"] = "Eye Assessment"
            st.session_state["assessment_step"] = 0
            st.switch_page("pages/02_👁️_Eye_Assessment.py")
    
    with col2:
        hearing_card_html = """
        <div class="assessment-option">
            <div class="option-icon">👂</div>
            <div class="option-title">Hearing Assessment</div>
            <div class="option-description">Complete hearing health evaluation</div>
            <div class="option-features">
                <strong>🎵 What's Included:</strong>
                <ul>
                    <li>Pure Tone Audiometry</li>
                    <li>Speech Recognition Test</li>
                    <li>Tinnitus Assessment</li>
                    <li>Frequency Analysis</li>
                    <li>Hearing Loss Detection</li>
                </ul>
            </div>
            <div class="option-duration">⏱️ 15-20 minutes</div>
        </div>
        """
        st.markdown(hearing_card_html, unsafe_allow_html=True)
        
        if st.button("Start Hearing Assessment", key="hearing_assessment", type="primary", use_container_width=True):
            st.session_state["assessment_choice"] = "Hearing Assessment"
            st.session_state["assessment_step"] = 0
            st.switch_page("pages/03_👂_Hearing_Assessment.py")
    
    with col3:
        complete_card_html = """
        <div class="assessment-option">
            <div class="option-icon">🎯</div>
            <div class="option-title">Complete Assessment</div>
            <div class="option-description">Full health screening package</div>
            <div class="option-features">
                <strong>🏆 Premium Package:</strong>
                <ul>
                    <li>Full Eye Assessment</li>
                    <li>Complete Hearing Test</li>
                    <li>Comprehensive Report</li>
                    <li>Health Recommendations</li>
                    <li>Priority Support</li>
                </ul>
            </div>
            <div class="option-duration">⏱️ 25-35 minutes</div>
        </div>
        """
        st.markdown(complete_card_html, unsafe_allow_html=True)
        
        if st.button("Start Complete Assessment", key="complete_assessment", type="primary", use_container_width=True):
            st.session_state["assessment_choice"] = "Both (Eye + Hearing)"
            st.session_state["assessment_step"] = 0
            st.switch_page("pages/02_👁️_Eye_Assessment.py")

def show_recent_assessments():
    """Show user's recent assessments"""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Your Recent Assessments</div>', unsafe_allow_html=True)
    
    user_assessments = get_user_recent_assessments()
    
    if not user_assessments.empty:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            for _, assessment in user_assessments.iterrows():
                risk_color = "🔴" if assessment.get('risk_level') == 'High' else "🟡" if assessment.get('risk_level') == 'Moderate' else "🟢"
                
                with st.expander(f"{risk_color} {assessment.get('assessment_type', 'Assessment')} - {str(assessment.get('created_at', ''))[:10]}"):
                    st.write(f"**Risk Level:** {assessment.get('risk_level', 'Unknown')}")
                    st.write(f"**Date:** {assessment.get('created_at', 'Unknown')}")
                    if assessment.get('recommendations'):
                        st.write(f"**Recommendations:** {assessment.get('recommendations', 'None')}")
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📋 View All Results", type="secondary", use_container_width=True):
                st.switch_page("pages/04_📊_Results_History.py")
    else:
        st.info("🎯 No previous assessments found. Start your first assessment above!")

def get_user_recent_assessments():
    """Get current user's recent assessments"""
    try:
        import pandas as pd
        import sqlite3
        
        if not st.session_state.get('user_id'):
            return pd.DataFrame()
        
        conn = sqlite3.connect('data/medical_assessment.db')
        
        query = """
        SELECT a.assessment_type, a.risk_level, a.created_at, a.recommendations
        FROM assessments a 
        JOIN patients p ON a.patient_id = p.id 
        WHERE p.id = ?
        ORDER BY a.created_at DESC 
        LIMIT 3
        """
        
        df = pd.read_sql_query(query, conn, params=[st.session_state['user_id']])
        conn.close()
        return df
        
    except Exception as e:
        return pd.DataFrame()

def show_assessment_tips():
    """Show assessment tips"""
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Assessment Tips</div>', unsafe_allow_html=True)
    
    tips_html = """
    <div class="tips-container">
        <div class="tip-card">
            <h4>📱 Before Starting</h4>
            <ul>
                <li>Ensure you're in a quiet, well-lit environment</li>
                <li>Have your medical history information ready</li>
                <li>Allow adequate time for complete testing</li>
                <li>Close other applications for better performance</li>
            </ul>
        </div>
        <div class="tip-card">
            <h4>🎯 For Best Results</h4>
            <ul>
                <li>Use headphones for hearing tests</li>
                <li>Have a camera ready for eye image capture</li>
                <li>Follow all instructions carefully</li>
                <li>Sit comfortably at arm's length from screen</li>
            </ul>
        </div>
    </div>
    """
    st.markdown(tips_html, unsafe_allow_html=True)

def main():
    init_session_state()
    
    st.session_state.page_name = "01_🏠_Home"
    
    if not st.session_state.get("authenticated", False):
        st.switch_page("streamlit_app.py")
        return
    
    show_streamlit_navbar()
    load_custom_css()
    
    username = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'patient')
    
    st.markdown(f"""
    <div class="welcome-header">
        <h1>🏥 Welcome back, {username}!</h1>
        <p style='font-size: 1.2rem; margin: 0.8rem 0;'>Comprehensive AI-Powered Eye & Hearing Health Screening</p>
        <p style='font-size: 0.95rem; opacity: 0.9;'>👤 Logged in as: {user_role.title()}</p>
    </div>
    """, unsafe_allow_html=True)
    
    show_assessment_stats()
    show_assessment_options()
    show_recent_assessments()
    show_assessment_tips()

if __name__ == "__main__":
    main()