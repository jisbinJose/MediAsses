import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import sys
from pathlib import Path
from io import BytesIO
import json
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from auth import init_session_state
from navbar import show_streamlit_navbar


st.set_page_config(page_title="User Profile", page_icon="👤", layout="wide")


def load_user_profile():
    """Load user profile information"""
    try:
        conn = sqlite3.connect('data/medical_assessment.db')
        user_id = st.session_state.get('user_id')
        
        if not user_id:
            return None
        
        # Get user details
        user_query = """
        SELECT name, age, gender, email, phone, created_at
        FROM patients 
        WHERE id = ?
        """
        user_df = pd.read_sql_query(user_query, conn, params=[user_id])
        
        conn.close()
        
        if not user_df.empty:
            return user_df.iloc[0].to_dict()
        return None
        
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return None


def load_user_assessments():
    """Load user's assessment history"""
    try:
        conn = sqlite3.connect('data/medical_assessment.db')
        user_id = st.session_state.get('user_id')
        
        if not user_id:
            return pd.DataFrame()
        
        query = """
        SELECT id, assessment_type, results, risk_level, recommendations, 
               critical_flag, created_at
        FROM assessments 
        WHERE patient_id = ?
        ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=[user_id])
        conn.close()
        
        return df
        
    except Exception as e:
        st.error(f"Error loading assessments: {e}")
        return pd.DataFrame()


def display_profile_info(profile_data):
    """Display user profile information - FIXED VERSION"""
    st.markdown("### 👤 Personal Information")
    
    if profile_data:
        # Use Streamlit columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Fixed: Using .format() instead of f-strings for better HTML rendering
            st.markdown("""
                <div style="
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    border-left: 4px solid #dc2626; 
                    margin-bottom: 2rem;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                ">
                    <h4 style="color: #1f2937; margin-top: 0; margin-bottom: 1rem;">Profile Details</h4>
                    <div style="line-height: 2;">
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Name:</strong> <span style="color: #1f2937;">{}</span></p>
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Age:</strong> <span style="color: #1f2937;">{}</span></p>
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Gender:</strong> <span style="color: #1f2937;">{}</span></p>
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Email:</strong> <span style="color: #1f2937;">{}</span></p>
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Phone:</strong> <span style="color: #1f2937;">{}</span></p>
                        <p style="margin: 0.5rem 0;"><strong style="color: #374151;">Member Since:</strong> <span style="color: #1f2937;">{}</span></p>
                    </div>
                </div>
            """.format(
                profile_data.get('name', 'N/A'),
                profile_data.get('age', 'N/A'),
                profile_data.get('gender', 'N/A'),
                profile_data.get('email', 'N/A'),
                profile_data.get('phone', 'N/A'),
                profile_data.get('created_at', 'N/A')[:10] if profile_data.get('created_at') else 'N/A'
            ), unsafe_allow_html=True)
    else:
        st.warning("⚠️ Profile information not available")
        st.info("💡 Try refreshing the page or contact support if the issue persists.")


def display_assessment_summary(assessments_df):
    """Display assessment summary statistics"""
    if assessments_df.empty:
        st.info("No assessments completed yet.")
        return
    
    st.markdown("### 📊 Assessment Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_assessments = len(assessments_df)
        st.metric("Total Assessments", total_assessments)
    
    with col2:
        eye_assessments = len(assessments_df[assessments_df['assessment_type'].str.contains('Eye|Visual', case=False, na=False)])
        st.metric("Eye Assessments", eye_assessments)
    
    with col3:
        hearing_assessments = len(assessments_df[assessments_df['assessment_type'].str.contains('Hearing', case=False, na=False)])
        st.metric("Hearing Assessments", hearing_assessments)
    
    with col4:
        high_risk = len(assessments_df[assessments_df['risk_level'] == 'High'])
        st.metric("High Risk Results", high_risk)


def generate_comprehensive_pdf(assessment, username):
    """Generate PDF report for assessment - Fallback function"""
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#dc2626'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    story.append(Paragraph("Medical Assessment Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Info
    story.append(Paragraph(f"<b>Patient:</b> {username}", styles['Normal']))
    story.append(Paragraph(f"<b>Assessment Type:</b> {assessment.get('assessment_type', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> {assessment.get('created_at', 'N/A')}", styles['Normal']))
    story.append(Paragraph(f"<b>Risk Level:</b> {assessment.get('risk_level', 'N/A')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Recommendations
    if assessment.get('recommendations'):
        story.append(Paragraph("<b>Recommendations:</b>", styles['Heading2']))
        story.append(Paragraph(assessment['recommendations'], styles['Normal']))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def display_recent_assessments(assessments_df):
    """Display recent assessments with download options"""
    st.markdown("### 📋 Recent Assessment Reports")
    
    if assessments_df.empty:
        st.info("No assessment reports available.")
        return
    
    # Show latest 5 assessments
    recent_assessments = assessments_df.head(5)
    
    for idx, (_, assessment) in enumerate(recent_assessments.iterrows()):
        with st.expander(f"{assessment['assessment_type']} - {assessment['created_at'][:10]} ({assessment['risk_level']} Risk)"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Date:** {assessment['created_at']}")
                st.write(f"**Risk Level:** {assessment['risk_level']}")
                if assessment['recommendations']:
                    st.write(f"**Recommendations:** {assessment['recommendations']}")
                if assessment['critical_flag']:
                    st.error("🚨 **CRITICAL**: Immediate medical attention recommended")
            
            with col2:
                try:
                    # Try to import from Results History page
                    # Use the correct import path without emoji
                    import importlib.util
                    
                    # Dynamically import the Results History module
                    results_page_path = Path(__file__).parent / "04_📊_Results_History.py"
                    if results_page_path.exists():
                        spec = importlib.util.spec_from_file_location("results_history", results_page_path)
                        results_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(results_module)
                        
                        profile_data = load_user_profile()
                        username = profile_data.get('name', 'User') if profile_data else 'User'
                        
                        pdf_bytes = results_module.generate_comprehensive_pdf(assessment, username)
                    else:
                        # Fallback: use local PDF generation
                        profile_data = load_user_profile()
                        username = profile_data.get('name', 'User') if profile_data else 'User'
                        pdf_bytes = generate_comprehensive_pdf(assessment, username)
                    
                    st.download_button(
                        "📄 Download PDF Report",
                        data=pdf_bytes,
                        file_name=f"{assessment['assessment_type'].replace(' ', '_')}_{assessment['created_at'][:10]}.pdf",
                        mime="application/pdf",
                        key=f"download_report_{assessment['id']}_{idx}",
                        use_container_width=True
                    )
                except Exception as e:
                    st.warning(f"PDF generation temporarily unavailable")
                    # Still show the data
                    pass


def show_profile_settings():
    """Show profile settings section"""
    st.markdown("### ⚙️ Profile Settings")
    
    with st.expander("Update Profile Information"):
        profile_data = load_user_profile()
        
        with st.form("update_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", value=profile_data.get('name', '') if profile_data else '')
                age = st.number_input("Age", value=profile_data.get('age', 0) if profile_data else 0, min_value=0, max_value=120)
                gender = st.selectbox("Gender", ["Male", "Female", "Other"], 
                                    index=["Male", "Female", "Other"].index(profile_data.get('gender', 'Male')) if profile_data and profile_data.get('gender') in ["Male", "Female", "Other"] else 0)
            
            with col2:
                email = st.text_input("Email", value=profile_data.get('email', '') if profile_data else '')
                phone = st.text_input("Phone", value=profile_data.get('phone', '') if profile_data else '')
            
            if st.form_submit_button("Update Profile", use_container_width=True):
                try:
                    conn = sqlite3.connect('data/medical_assessment.db')
                    user_id = st.session_state.get('user_id')
                    
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE patients 
                        SET name = ?, age = ?, gender = ?, email = ?, phone = ?
                        WHERE id = ?
                    """, (name, age, gender, email, phone, user_id))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("Profile updated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error updating profile: {e}")


def main():
    # Initialize session state
    init_session_state()
    
    # Set current page name for navbar logic
    st.session_state.page_name = "06_👤_Profile"
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.error("Please login first!")
        st.switch_page("streamlit_app.py")
        return
    
    # Show navbar
    show_streamlit_navbar()
    
    st.title("👤 User Profile")
    
    # Get user info
    username = st.session_state.get('username', 'Unknown')
    st.success(f"Welcome to your profile, {username}!")
    
    # Load user data
    profile_data = load_user_profile()
    assessments_df = load_user_assessments()
    
    # Display profile sections
    display_profile_info(profile_data)
    
    st.markdown("---")
    
    # Assessment summary
    display_assessment_summary(assessments_df)
    
    st.markdown("---")
    
    # Recent assessments with downloads
    display_recent_assessments(assessments_df)
    
    st.markdown("---")
    
    # Quick navigation
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("👁️ Eye Assessment", use_container_width=True):
            st.switch_page("pages/02_👁️_Eye_Assessment.py")
    
    with col2:
        if st.button("👂 Hearing Assessment", use_container_width=True):
            st.switch_page("pages/03_👂_Hearing_Assessment.py")
    
    with col3:
        if st.button("📊 View Full Results History", use_container_width=True):
            st.switch_page("pages/04_📊_Results_History.py")
    
    st.markdown("---")
    
    # Profile settings
    show_profile_settings()


if __name__ == "__main__":
    main()
