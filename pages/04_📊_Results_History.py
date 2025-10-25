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

st.set_page_config(page_title="Results History", page_icon="📋", layout="wide")

def main():
    # Initialize session state
    init_session_state()
    
    # Set current page name for navbar logic
    st.session_state.page_name = "04_📋_Results_History"
    
    # Check authentication
    if not st.session_state.get('authenticated', False):
        st.error("Please login first!")
        st.switch_page("streamlit_app.py")
        return
    
    # Show navbar
    show_streamlit_navbar()
    
    st.title("📋 Assessment Results & History")
    
    # Get user info
    username = st.session_state.get('username', 'Unknown')
    user_id = st.session_state.get('user_id')
    
    st.success(f"👤 Results for: {username}")
    
    # Load user's assessment data
    assessment_data = load_user_assessments(user_id, username)
    
    if assessment_data.empty:
        show_no_results()
    else:
        show_results_dashboard(assessment_data, username)

def load_user_assessments(user_id, username):
    """Load user's assessment history from database"""
    try:
        conn = sqlite3.connect('data/medical_assessment.db')
        
        # First, let's check what columns exist in the assessments table
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(assessments)")
        column_info = cursor.fetchall()
        columns = [row[1] for row in column_info]  # Fixed: was row[40], should be row[1]
        
        # Build query based on available columns
        if 'patient_id' in columns:
            query = """
            SELECT id, assessment_type, results, risk_level, recommendations, 
                   created_at, 
                   CASE WHEN critical_flag IS NOT NULL THEN critical_flag ELSE 0 END as critical_flag
            FROM assessments 
            WHERE patient_id = ?
            ORDER BY created_at DESC
            """
            df = pd.read_sql_query(query, conn, params=[user_id])
        else:
            # Fallback: try to get all assessments (for testing)
            query = """
            SELECT id, assessment_type, results, risk_level, recommendations, 
                   created_at,
                   CASE WHEN critical_flag IS NOT NULL THEN critical_flag ELSE 0 END as critical_flag
            FROM assessments 
            ORDER BY created_at DESC
            LIMIT 50
            """
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        # Debug: Show what we found
        if not df.empty:
            st.success(f"Found {len(df)} assessment records")
        else:
            st.warning("No assessment records found in database")
            
        return df
        
    except Exception as e:
        st.error(f"Error loading assessment data: {e}")
        # Debug: Show database structure
        try:
            conn = sqlite3.connect('data/medical_assessment.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            st.info(f"Available tables: {[table[0] for table in tables]}")
            conn.close()
        except:
            pass
        return pd.DataFrame()

def show_no_results():
    """Display message when no results are found"""
    st.info("📊 No assessment results found.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🎯 Start Your First Assessment")
        
        if st.button("👁️ Start Eye Assessment", type="primary", use_container_width=True):
            st.switch_page("pages/02_👁️_Eye_Assessment.py")
        
        if st.button("👂 Start Hearing Assessment", use_container_width=True):
            st.switch_page("pages/03_🦻_Hearing_Assessment.py")

def show_results_dashboard(df, username):
    """Display comprehensive results dashboard"""
    
    # Results Overview
    st.markdown("### 📊 Assessment Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_assessments = len(df)
        st.metric("Total Assessments", total_assessments)
    
    with col2:
        high_risk_count = len(df[df['risk_level'] == 'High'])
        st.metric("High Risk Results", high_risk_count, 
                 delta="⚠️" if high_risk_count > 0 else "✅")
    
    with col3:
        recent_assessment = df.iloc[0]['created_at'][:10] if not df.empty else "None"
        st.metric("Last Assessment", recent_assessment)
    
    with col4:
        critical_cases = len(df[df['critical_flag'] == 1])
        st.metric("Critical Cases", critical_cases,
                 delta="🚨" if critical_cases > 0 else "✅")
    
    st.markdown("---")
    
    # Latest Results Section
    st.markdown("### 🔬 Latest Assessment Results")
    
    latest_result = df.iloc[0]
    show_detailed_result(latest_result, is_latest=True)
    
    # Generate and display PDF download for latest result
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pdf_bytes = generate_comprehensive_pdf(latest_result, username)
        st.download_button(
            label="📥 Download Latest Report as PDF",
            data=pdf_bytes,
            file_name=f"medical_assessment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Assessment History
    st.markdown("### 📈 Assessment History")
    
    if len(df) > 1:
        for idx, (index, result) in enumerate(df.iterrows()):
            if idx == 0:  # Skip first (already shown above)
                continue
                
            risk_emoji = "🚨" if result['risk_level'] == 'High' else "⚠️" if result['risk_level'] == 'Moderate' else "✅"
            
            with st.expander(f"{risk_emoji} {result['assessment_type']} - {result['created_at'][:10]} ({result['risk_level']} Risk)"):
                show_detailed_result(result, is_latest=False)
                
                # Individual PDF download for each assessment
                individual_pdf = generate_comprehensive_pdf(result, username)
                st.download_button(
                    label="📄 Download This Report",
                    data=individual_pdf,
                    file_name=f"assessment_report_{result['created_at'][:10]}.pdf",
                    mime="application/pdf",
                    key=f"pdf_download_{result['id']}"
                )
    else:
        st.info("Only one assessment completed. Complete more assessments to see history.")

def show_detailed_result(result, is_latest=False):
    """Display detailed results for a single assessment"""
    
    # Parse results JSON
    try:
        results_data = json.loads(result['results'])
    except:
        results_data = {"error": "Could not parse results"}
    
    # Assessment Info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Assessment Details")
        st.write(f"**Type:** {result['assessment_type']}")
        st.write(f"**Date:** {result['created_at']}")
        st.write(f"**Risk Level:** {get_risk_badge(result['risk_level'])}")
        
        if result['critical_flag'] == 1:
            st.error("🚨 **CRITICAL**: Immediate medical attention recommended")
    
    with col2:
        st.markdown("#### 📊 Results Summary")
        
        # Display results based on assessment type
        if "Hearing" in result['assessment_type'] or "hearing" in result['assessment_type'].lower():
            display_hearing_results(results_data)
        elif "Visual Acuity" in result['assessment_type']:
            display_visual_acuity_results(results_data)
        elif "AI Eye Disease Detection" in result['assessment_type'] or "AI" in result['assessment_type']:
            display_ai_eye_results(results_data)
        elif "Risk Factor" in result['assessment_type']:
            display_risk_factor_results(results_data)
        elif "Symptom" in result['assessment_type']:
            display_symptom_results(results_data)
        elif "Comprehensive" in result['assessment_type'] or "Camera" in result['assessment_type']:
            display_image_analysis_results(results_data)
        else:
            # Fallback: show all data
            for key, value in results_data.items():
                if isinstance(value, dict):
                    st.write(f"**{key.replace('_', ' ').title()}:**")
                    for sub_key, sub_value in value.items():
                        st.write(f"  - {sub_key.replace('_', ' ').title()}: {sub_value}")
                else:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Recommendations
    if result['recommendations']:
        st.markdown("#### 🏥 Medical Recommendations")
        st.info(result['recommendations'])

def display_visual_acuity_results(data):
    """Display visual acuity test results"""
    st.write("**👁️ Visual Acuity Test Results**")
    
    # Accuracy percentage
    if 'accuracy_percentage' in data:
        st.metric("Accuracy", f"{data['accuracy_percentage']:.1f}%")
    
    # Estimated acuity
    if 'estimated_acuity' in data:
        st.write(f"**Estimated Acuity:** {data['estimated_acuity']}")
    
    # Status
    if 'status' in data:
        st.write(f"**Status:** {data['status']}")
    
    # Test details
    if 'total_lines' in data and 'correct_count' in data:
        st.write(f"**Test Summary:** {data['correct_count']}/{data['total_lines']} lines correct")
    
    # Detailed answers if available
    if 'detailed_answers' in data and data['detailed_answers']:
        with st.expander("View Detailed Answers"):
            for i, answer in enumerate(data['detailed_answers'], 1):
                status_icon = "✅" if answer.get('correct', False) else "❌"
                st.write(f"{status_icon} Line {i}: Expected `{answer.get('expected', 'N/A')}` | Your answer: `{answer.get('user_input', 'N/A')}`")

def display_ai_eye_results(data):
    """Display AI eye disease detection results"""
    st.write("**🤖 AI Eye Disease Detection Results**")
    
    # Overall health status
    if 'overall_healthy' in data:
        status = "✅ Healthy" if data['overall_healthy'] else "⚠️ Review Needed"
        st.metric("Overall Eye Health", status)
    
    # Conditions detected count
    if 'conditions_detected_count' in data:
        st.metric("Conditions Detected", data['conditions_detected_count'])
    
    # Analysis results
    if 'analysis_results' in data:
        st.write("**Disease Analysis:**")
        analysis = data['analysis_results']
        if isinstance(analysis, dict):
            for condition, details in analysis.items():
                if isinstance(details, dict):
                    detected = details.get('detected', False)
                    confidence = details.get('confidence', 0)
                    status_icon = "🚨" if detected else "✅"
                    status_text = "Detected" if detected else "Not Detected"
                    st.write(f"{status_icon} **{condition.replace('_', ' ').title()}:** {status_text} (Confidence: {confidence}%)")
                else:
                    st.write(f"**{condition.replace('_', ' ').title()}:** {details}")
    
    # Quality metrics
    if 'quality_metrics' in data:
        quality = data['quality_metrics']
        if isinstance(quality, dict) and 'overall_quality' in quality:
            st.write(f"**Image Quality:** {quality['overall_quality']}")

def display_hearing_results(data):
    """Display hearing assessment results"""
    st.write("**🎧 Hearing Assessment Results**")
    
    # Overall score
    if 'overall_score' in data:
        st.metric("Overall Hearing Score", f"{data['overall_score']}%")
    
    # Left ear results
    if 'left_ear' in data:
        left_data = data['left_ear']
        if isinstance(left_data, dict):
            threshold = left_data.get('hearing_threshold_db', 'N/A')
            classification = left_data.get('classification', 'N/A')
            st.write(f"**Left Ear:** {threshold} dB HL ({classification})")
    
    # Right ear results
    if 'right_ear' in data:
        right_data = data['right_ear']
        if isinstance(right_data, dict):
            threshold = right_data.get('hearing_threshold_db', 'N/A')
            classification = right_data.get('classification', 'N/A')
            st.write(f"**Right Ear:** {threshold} dB HL ({classification})")
    
    # Additional hearing data
    for key, value in data.items():
        if key not in ['overall_score', 'left_ear', 'right_ear', 'test_date']:
            if 'threshold' in key.lower():
                st.write(f"**{key.replace('_', ' ').title()}:** {value} dB HL")
            elif 'classification' in key.lower():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

def display_risk_factor_results(data):
    """Display risk factor assessment results"""
    if 'total_risk_score' in data:
        st.metric("Risk Score", f"{data['total_risk_score']}/100")
    
    if 'age' in data:
        st.write(f"**Age:** {data['age']} years")
    
    risk_factors = []
    if data.get('diabetes'): risk_factors.append("Diabetes")
    if data.get('family_history'): risk_factors.append("Family History")
    if data.get('smoking'): risk_factors.append("Smoking")
    if data.get('high_blood_pressure'): risk_factors.append("High BP")
    
    if risk_factors:
        st.write(f"**Risk Factors:** {', '.join(risk_factors)}")
    else:
        st.write("**Risk Factors:** None identified")

def display_symptom_results(data):
    """Display symptom assessment results"""
    if 'total_score' in data:
        st.metric("Symptom Score", f"{data['total_score']}/15")
    
    symptoms = []
    for key, value in data.items():
        if key != 'total_score' and value not in ['No', 'None']:
            symptoms.append(f"{key.replace('_', ' ').title()}: {value}")
    
    if symptoms:
        st.write("**Reported Symptoms:**")
        for symptom in symptoms:
            st.write(f"• {symptom}")
    else:
        st.write("**Symptoms:** None reported")

def display_image_analysis_results(data):
    """Display image analysis results"""
    st.write("**AI Analysis Results:**")
    
    for condition, probability in data.items():
        if isinstance(probability, (int, float)):
            percentage = f"{probability:.1%}"
            if condition == "Normal":
                st.success(f"✅ {condition}: {percentage}")
            elif probability > 0.5:
                st.error(f"🚨 {condition}: {percentage}")
            elif probability > 0.3:
                st.warning(f"⚠️ {condition}: {percentage}")
            else:
                st.info(f"📊 {condition}: {percentage}")

def get_risk_badge(risk_level):
    """Get colored badge for risk level"""
    if risk_level == "High":
        return "🚨 **HIGH**"
    elif risk_level == "Moderate":
        return "⚠️ **MODERATE**"
    else:
        return "✅ **LOW**"

def generate_comprehensive_pdf(result, username):
    """Generate comprehensive PDF report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story = []
    
    # Title
    story.append(Paragraph("🏥 MEDICAL ASSESSMENT REPORT", title_style))
    story.append(Spacer(1, 12))
    
    # Patient Information
    story.append(Paragraph("PATIENT INFORMATION", styles['Heading2']))
    patient_data = [
        ['Patient Name:', username],
        ['Assessment Date:', result['created_at'][:10]],
        ['Assessment Type:', result['assessment_type']],
        ['Risk Level:', result['risk_level']],
        ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
    ]
    
    patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
    patient_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(patient_table)
    story.append(Spacer(1, 20))
    
    # Assessment Results
    story.append(Paragraph("ASSESSMENT RESULTS", styles['Heading2']))
    
    try:
        results_data = json.loads(result['results'])
        
        # Create results table
        results_table_data = [['Parameter', 'Value']]
        
        for key, value in results_data.items():
            formatted_key = key.replace('_', ' ').title()
            if isinstance(value, dict):
                # Handle nested data (like hearing results)
                for sub_key, sub_value in value.items():
                    formatted_sub_key = f"{formatted_key} - {sub_key.replace('_', ' ').title()}"
                    formatted_value = str(sub_value)
                    results_table_data.append([formatted_sub_key, formatted_value])
            elif isinstance(value, float):
                formatted_value = f"{value:.2f}" if value < 1 else f"{value:.1%}"
                results_table_data.append([formatted_key, formatted_value])
            else:
                formatted_value = str(value)
                results_table_data.append([formatted_key, formatted_value])
        
        results_table = Table(results_table_data, colWidths=[3*inch, 3*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(results_table)
        
    except Exception as e:
        story.append(Paragraph(f"Results: {result['results']}", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Recommendations
    story.append(Paragraph("MEDICAL RECOMMENDATIONS", styles['Heading2']))
    
    if result['recommendations']:
        story.append(Paragraph(result['recommendations'], styles['Normal']))
    else:
        story.append(Paragraph("No specific recommendations at this time.", styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Risk Assessment
    story.append(Paragraph("RISK ASSESSMENT", styles['Heading2']))
    
    risk_color = colors.red if result['risk_level'] == 'High' else colors.orange if result['risk_level'] == 'Moderate' else colors.green
    
    risk_text = f"Overall Risk Level: <font color='{risk_color.hexval()}'><b>{result['risk_level']}</b></font>"
    story.append(Paragraph(risk_text, styles['Normal']))
    
    if result['critical_flag'] == 1:
        story.append(Spacer(1, 12))
        critical_text = "<font color='red'><b>⚠️ CRITICAL: This assessment indicates immediate medical attention may be required.</b></font>"
        story.append(Paragraph(critical_text, styles['Normal']))
    
    story.append(Spacer(1, 30))
    
    # Disclaimer
    story.append(Paragraph("DISCLAIMER", styles['Heading3']))
    disclaimer_text = """
    This report is generated by an AI-powered medical assessment tool and is intended for informational purposes only. 
    It should not replace professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare 
    providers for medical concerns and before making any healthcare decisions.
    """
    story.append(Paragraph(disclaimer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

if __name__ == "__main__":
    main()
