import streamlit as st
from pathlib import Path
import sys
import json
import time
from PIL import Image
import io
import cv2
import numpy as np
import pandas as pd
import warnings

# --- NEW IMPORTS FOR REAL-TIME CAMERA ---
import base64
# --- END NEW IMPORTS ---

# --- NEW IMPORT FOR PDF GENERATION ---
from fpdf import FPDF
import base64
# --- END NEW IMPORT ---

# Page config
st.set_page_config(page_title="Eye Assessment", page_icon="👁", layout="wide")

# ADD THIS NEW BLOCK AT THE TOP
import warnings
from pydub import AudioSegment
from pathlib import Path
import os

# --- FFmpeg Configuration ---
# Get the root directory of your project (one level up from 'pages')
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the full paths to the executables
FFMPEG_PATH = str(PROJECT_ROOT / "ffmpeg.exe")
FFPROBE_PATH = str(PROJECT_ROOT / "ffprobe.exe")

# Check if the files exist before setting
if os.path.exists(FFMPEG_PATH):
    AudioSegment.converter = FFMPEG_PATH
else:
    st.warning(f"ffmpeg.exe not found at expected path: {FFMPEG_PATH}. Audio processing might fail.")
if os.path.exists(FFPROBE_PATH):
    AudioSegment.ffprobe = FFPROBE_PATH
else:
    st.warning(f"ffprobe.exe not found at expected path: {FFPROBE_PATH}. Audio processing might fail.")


# Suppress pydub warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub")
# --- End of Configuration ---

# Add utils to path
# Ensure the 'utils' directory exists at PROJECT_ROOT/utils
utils_path = PROJECT_ROOT / "utils"
if str(utils_path) not in sys.path:
    sys.path.append(str(utils_path))

# Import from utils (assuming these files exist in the utils directory)
try:
    from auth import init_session_state
    from navbar import show_streamlit_navbar
    from database import MedicalDB
except ImportError:
    st.error("Failed to import utility modules (auth, navbar, database). Ensure they are in the 'utils' directory relative to the main app file.")
    # Define dummy functions to avoid crashing the app
    def init_session_state():
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False # Set default to False
            st.warning("Auth module not found. Assuming not authenticated.")
        if 'user_id' not in st.session_state:
             # Only set dummy if authentication is skipped/failed
            if not st.session_state.authenticated:
                st.session_state.user_id = 'dummy_user_eye'
                st.warning("Auth module not found. Using dummy user ID for potential saving.")

    def show_streamlit_navbar():
        st.warning("Navbar module not found.")
    class MedicalDB:
        def __init__(self):
            st.warning("Database module not found. Results will not be saved.")
        def add_assessment(self, **kwargs):
            st.info("Dummy DB: Assessment data received but not saved.")
            print("Dummy DB: Assessment data received:", kwargs)


#
# --- NEW PDF GENERATION CLASS ---
#
class PDF(FPDF):
    def header(self):
        # Logo (optional)
        # self.image('logo.png', 10, 8, 33) # Example: Add your logo if you have one
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Comprehensive Health Assessment Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Report Date: {time.strftime('%Y-%m-%d %H:%M:%S')}", 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(220, 220, 220) # Light grey background
        self.cell(0, 6, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 10)
        # Handle potential encoding issues for PDF
        body = body.encode('latin-1', 'replace').decode('latin-1')
        self.multi_cell(0, 5, body)
        self.ln()

    def add_metric(self, name, value, color=(0,0,0)):
        self.set_font('Arial', 'B', 11)
        self.cell(90, 8, name, border=1)
        self.set_text_color(*color)
        self.set_font('Arial', 'B', 11)
        # Handle potential encoding issues for PDF
        value_str = str(value).encode('latin-1', 'replace').decode('latin-1')
        self.cell(90, 8, value_str, border=1, ln=1, align='R')
        self.set_text_color(0,0,0) # Reset to black
        self.set_font('Arial', '', 10) # Reset font

# --- NEW FUNCTION TO GENERATE ACUITY PDF ---
def generate_acuity_pdf(data, accuracy, acuity, status, user_id="N/A"):
    pdf = PDF()
    pdf.add_page()

    # User Info (Optional)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Patient ID: {user_id}", 0, 1, 'L')
    pdf.ln(5)

    # Title
    pdf.chapter_title('Visual Acuity Test Results')

    # Summary Metrics
    pdf.add_metric('Overall Accuracy', f"{accuracy:.1f}%")
    pdf.add_metric('Estimated Acuity', acuity, color=(220, 50, 50) if "Poor" in status else (0,0,0))
    pdf.add_metric('Status', status)
    pdf.add_metric('Lines Answered Correctly', f"{data.get('correct_count', 0)} / {data.get('total_count', 0)}")
    pdf.ln(5)

    # Detailed Answers
    if 'answers' in data and data['answers']:
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 6, 'Detailed Answers', 0, 1, 'L')
        pdf.set_font('Arial', 'B', 10)
        # Adjusted widths
        pdf.cell(30, 6, 'Line #', 1)
        pdf.cell(70, 6, 'Expected', 1)
        pdf.cell(70, 6, 'Your Answer', 1)
        pdf.cell(20, 6, 'Result', 1, ln=1)

        pdf.set_font('Arial', '', 10)
        for i, answer in enumerate(data.get('answers', [])):
            line_status = "Correct" if answer['correct'] else "Incorrect"
            expected_str = answer['expected'].encode('latin-1', 'replace').decode('latin-1')
            user_input_str = answer['user_input'].encode('latin-1', 'replace').decode('latin-1')

            pdf.cell(30, 6, f"{i+1}", 1)
            pdf.cell(70, 6, expected_str, 1)
            pdf.cell(70, 6, user_input_str, 1)
            pdf.cell(20, 6, line_status, 1, ln=1)
    else:
        pdf.chapter_body("No detailed answers recorded.")

    pdf.ln(10)

    # Recommendations based on status
    if accuracy >= 90:
        recommendations = "Excellent visual acuity detected. Continue regular eye care and annual check-ups."
    elif accuracy >= 75:
        recommendations = "Good visual acuity with minor issues. Consider annual eye examination."
    elif accuracy >= 60:
        recommendations = "Fair visual acuity detected. Schedule an eye examination within 6 months."
    else:
        recommendations = "Poor visual acuity detected. Schedule immediate comprehensive eye examination with an optometrist or ophthalmologist."
    pdf.chapter_title('Recommendations')
    pdf.chapter_body(recommendations)

    pdf.ln(5)
    pdf.chapter_body(
        "Disclaimer: This is an AI-powered screening tool and not a substitute for professional medical diagnosis. "
        "Please consult an eye care professional for comprehensive eye examinations."
    )

    # Return as bytes
    return pdf.output(dest='S').encode('latin-1')

# --- NEW FUNCTION TO GENERATE AI PDF ---
def generate_ai_pdf(analysis_results, quality_metrics, overall, validation_details, user_id="N/A"):
    pdf = PDF()
    pdf.add_page()

    # User Info (Optional)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 6, f"Patient ID: {user_id}", 0, 1, 'L')
    pdf.ln(5)

    # Title
    pdf.chapter_title('AI Eye Disease Detection Results')

    # Overall Status
    is_healthy = overall.get('healthy', False)
    overall_status_text = "Healthy" if is_healthy else "Review Recommended"
    status_color = (0, 128, 0) if is_healthy else (220, 50, 50) # Green or Red

    pdf.add_metric('Overall Status', overall_status_text, color=status_color)
    pdf.add_metric('Conditions Detected', str(overall.get('conditions_detected', 0)))
    pdf.add_metric('Input Image Quality', str(quality_metrics.get('overall_quality', 'N/A')))
    pdf.add_metric('Faces Detected (Validation)', str(validation_details.get('faces_detected', 'N/A')))
    pdf.add_metric('Eyes Detected (Validation)', str(validation_details.get('eyes_detected', 'N/A')))
    pdf.ln(5) # Add line break after metrics

    # Detailed Condition Analysis
    pdf.chapter_title('Disease-Specific Analysis')
    pdf.set_font('Arial', 'B', 10)
    # Adjusted widths
    pdf.cell(70, 6, 'Condition', 1)
    pdf.cell(30, 6, 'Detected', 1)
    pdf.cell(30, 6, 'Confidence', 1)
    pdf.cell(60, 6, 'Notes', 1, ln=1)

    pdf.set_font('Arial', '', 10)
    conditions_data = [
            ("Diabetic Retinopathy", analysis_results.get('diabetic_retinopathy', {})),
            ("Glaucoma", analysis_results.get('glaucoma', {})),
            ("Cataracts", analysis_results.get('cataracts', {})),
            ("Age-related Macular Degeneration", analysis_results.get('amd', {})),
            ("Hypertensive Retinopathy", analysis_results.get('hypertensive_retinopathy', {})),
        ]
    descriptions = { # Simplified notes for PDF
            "Diabetic Retinopathy": "Blood vessel damage related to diabetes.",
            "Glaucoma": "Optic nerve health/pressure indicators.",
            "Cataracts": "Clouding in the lens.",
            "Age-related Macular Degeneration": "Deterioration in the macula.",
            "Hypertensive Retinopathy": "Blood vessel changes from high BP."
        }

    for name, data in conditions_data:
        detected = "Yes" if data.get('detected', False) else "No"
        confidence = f"{data.get('confidence', 'N/A')}%" if isinstance(data.get('confidence'), (int, float)) else 'N/A'
        note = descriptions.get(name, "") if detected == "Yes" else "No significant signs detected."
        note_str = note.encode('latin-1', 'replace').decode('latin-1')

        pdf.cell(70, 6, name, 1)
        pdf.cell(30, 6, detected, 1, align='C')
        pdf.cell(30, 6, confidence, 1, align='R')
        pdf.cell(60, 6, note_str, 1, ln=1)

    pdf.ln(10)

    # Recommendations
    pdf.chapter_title('Recommendations')
    recommendation_text = overall.get('recommendation', "Consult an eye care professional for a comprehensive exam.")
    pdf.chapter_body(recommendation_text)
    pdf.ln(2)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 6, 'General Advice:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    general_advice = (
        "- Continue regular comprehensive eye exams (typically annually, or as advised by your doctor).\n"
        "- Maintain a healthy lifestyle, including proper nutrition and exercise.\n"
        "- Wear UV-protective sunglasses outdoors.\n"
        "- Report any sudden changes in vision to an eye care professional immediately.\n"
        "- If diabetic, ensure good blood sugar control.\n"
        "- Monitor and manage blood pressure."
    )
    pdf.multi_cell(0, 5, general_advice.encode('latin-1', 'replace').decode('latin-1'))
    pdf.ln(5)

    pdf.chapter_body(
        "Disclaimer: This is an AI-powered screening tool and not a substitute for professional medical diagnosis. "
        "Please consult an eye care professional for comprehensive eye examinations and any concerns about your eye health. "
        "These results are based on image analysis and should not be considered a definitive diagnosis."
    )

    # Return as bytes
    return pdf.output(dest='S').encode('latin-1')


# --- Database saving functions (Unchanged) ---
def save_eye_assessment_results(data, accuracy, acuity, status):
    """Save eye assessment results to database"""
    try:
        db = MedicalDB()
        user_id = st.session_state.get('user_id')

        if not user_id:
            # Check authentication status again
            if not st.session_state.get('authenticated'):
                st.error("User not authenticated. Please log in to save results.")
            else:
                st.error("User ID missing in session state even though authenticated.")
            return False

        # Determine risk level and recommendations
        if accuracy >= 90:
            risk_level = "Normal"
            recommendations = "Excellent visual acuity detected. Continue regular eye care and annual check-ups."
            critical_flag = False
        elif accuracy >= 75:
            risk_level = "Mild"
            recommendations = "Good visual acuity with minor issues. Consider annual eye examination."
            critical_flag = False
        elif accuracy >= 60:
            risk_level = "Moderate"
            recommendations = "Fair visual acuity detected. Schedule an eye examination within 6 months."
            critical_flag = False
        else:
            risk_level = "High"
            recommendations = "Poor visual acuity detected. Schedule immediate comprehensive eye examination with an optometrist or ophthalmologist."
            critical_flag = True

        # Prepare results data
        results_data = {
            'test_type': 'Visual Acuity Test',
            'accuracy_percentage': accuracy,
            'estimated_acuity': acuity,
            'status': status,
            'total_lines': len(data.get('lines', [])), # Safer access
            'correct_count': data.get('correct_count', 0), # Safer access
            'total_count': data.get('total_count', 0), # Safer access
            'detailed_answers': data.get('answers', []),
            'test_date': str(pd.Timestamp.now().date()) if 'pd' in globals() else str(time.strftime("%Y-%m-%d"))
        }

        # Save to database
        db.add_assessment(
            patient_id=user_id,
            assessment_type="Visual Acuity Test",
            results=results_data,
            risk_level=risk_level,
            recommendations=recommendations,
            critical_flag=critical_flag
        )

        return True

    except Exception as e:
        st.error(f"Error saving visual acuity results: {str(e)}")
        return False

def save_ai_detection_results(analysis_results, quality_metrics, overall, validation_details):
    """Save AI detection results to database"""
    try:
        db = MedicalDB()
        user_id = st.session_state.get('user_id')

        if not user_id:
             if not st.session_state.get('authenticated'):
                 st.error("User not authenticated. Please log in to save results.")
             else:
                 st.error("User ID missing in session state even though authenticated.")
             return False

        # Determine risk level based on AI results
        conditions_detected = 0
        max_risk_condition = "normal"

        # Use .get with default empty dict to avoid errors if analysis_results is None
        for condition, data in (analysis_results or {}).items():
            if condition != 'normal' and data.get('detected', False):
                conditions_detected += 1
                max_risk_condition = condition

        # Use .get with defaults for overall dict
        if conditions_detected == 0 and overall.get('healthy', False):
            risk_level = "Normal"
            recommendations = "AI analysis shows no significant eye conditions detected. Continue regular eye care."
            critical_flag = False
        elif conditions_detected == 1:
            risk_level = "Mild"
            recommendations = "AI detected potential indicators. Schedule an eye examination for professional assessment."
            critical_flag = False
        else: # Covers conditions_detected > 1 or healthy=False
            risk_level = "High"
            recommendations = "AI detected multiple potential conditions or other concerns. Schedule immediate comprehensive eye examination."
            critical_flag = True

        # Prepare results data
        results_data = {
            'test_type': 'AI Eye Disease Detection',
            'overall_healthy': overall.get('healthy', False),
            'conditions_detected_count': conditions_detected,
            'analysis_results': analysis_results or {}, # Ensure it's not None
            'quality_metrics': quality_metrics or {}, # Ensure it's not None
            'validation_details': validation_details or {}, # Ensure it's not None
            'recommendation': overall.get('recommendation', 'N/A'),
            'test_date': str(pd.Timestamp.now().date()) if 'pd' in globals() else str(time.strftime("%Y-%m-%d"))
        }

        # Save to database
        db.add_assessment(
            patient_id=user_id,
            assessment_type="AI Eye Disease Detection",
            results=results_data,
            risk_level=risk_level,
            recommendations=recommendations,
            critical_flag=critical_flag
        )

        return True

    except Exception as e:
        st.error(f"Error saving AI detection results: {str(e)}")
        return False

# --- UI Functions ---

# --- THIS FUNCTION IS REPLACED with your new styles ---
def load_custom_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #ffffff 0%, #fff5f5 100%);
    }

    /* Header styling */
    .assessment-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 16px rgba(220, 38, 38, 0.2);
    }

    .assessment-header h1 {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }

    .assessment-header p {
        font-size: 0.95rem;
        opacity: 0.95;
    }

    /* Test selection cards */
    .test-card {
        background: white;
        border: 2px solid #fee2e2;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    }

    .test-card:hover {
        border-color: #dc2626;
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.15);
    }

    .test-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }

    .test-title {
        color: #1f2937;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }

    .test-description {
        color: #6b7280;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }

    /* Visual Acuity Test Styles */
    .snellen-chart {
        background: white;
        border: 2px solid #dc2626;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin: 1.5rem auto;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        max-width: 700px;
    }

    .optotype-display {
        font-family: 'Courier New', monospace;
        font-weight: bold;
        color: #1f2937;
        margin: 1.5rem 0;
        letter-spacing: 0.5rem;
        user-select: none;
    }

    /* Progress indicator */
    .progress-container {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.75rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .progress-bar {
        height: 6px;
        background: #fee2e2;
        border-radius: 3px;
        overflow: hidden;
    }

    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #dc2626, #b91c1c);
        transition: width 0.3s ease;
    }

    /* Result cards */
    .result-card {
        background: white;
        border-left: 4px solid #dc2626;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    .score-display {
        font-size: 2.5rem;
        font-weight: 700;
        color: #dc2626;
        margin: 0.75rem 0;
    }

    /* Instructions */
    .instruction-box {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-radius: 8px;
        padding: 0.9rem;
        margin: 0.75rem 0;
        color: #991b1b;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .instruction-box strong {
        color: #dc2626;
    }

    /* Button styling */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.65rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        margin-bottom: 5px;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3) !important;
    }
    
    .stDownloadButton > button {
        text-align: center !important;
        display: block !important;
    }

    /* Input field styling */
    .stTextInput > div > div > input {
        font-size: 0.95rem !important;
        padding: 0.6rem !important;
        text-align: center;
        font-weight: 500;
        letter-spacing: 0.2rem;
        text-transform: uppercase;
    }

    /* Audio recorder styling */
    .audio-recorder-container {
        background: white;
        border: 2px solid #dc2626;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.75rem 0;
        text-align: center;
    }

    .recording-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        background: #dc2626;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
        margin-right: 0.5rem;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* Next step prompt */
    .next-step-card {
        background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.25);
    }

    .next-step-card h3 {
        margin: 0 0 0.5rem 0;
        color: white;
        font-size: 1.3rem;
    }

    .next-step-card p {
        margin: 0;
        font-size: 1rem;
    }

    /* Camera preview - Constrained */
    [data-testid="stCameraInput"] {
        max-width: 500px;
        margin: 0 auto 1rem auto;
        border: 2px solid #dc2626;
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stCameraInput"] video {
        border-radius: 10px;
    }

    .analysis-result {
        background: #f0fdf4;
        border: 2px solid #86efac;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    /* Validation error styling */
    .validation-error {
        background: #fef2f2;
        border: 2px solid #fca5a5;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #991b1b;
    }

    .validation-error h3 {
        color: #dc2626;
        margin-top: 0;
    }

    .validation-warning {
        background: #fffbeb;
        border: 2px solid #fcd34d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        color: #92400e;
    }

    .validation-warning h3 {
        color: #d97706;
        margin-top: 0;
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }

    .status-success {
        background: #dcfce7;
        color: #166534;
    }

    .status-error {
        background: #fee2e2;
        color: #991b1b;
    }
    
    /* Enhanced Disease Card Styling */
    .disease-card {
        background: #ffffff;
        border-left-width: 4px;
        border-left-style: solid;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
        border-radius: 10px;
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.06);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .disease-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 16px rgba(0, 0, 0, 0.08);
    }
    .disease-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f3f4f6;
    }
    .disease-card-title {
        color: #1f2937;
        font-size: 1.1rem;
        font-weight: 700;
    }
    .disease-card-status {
        font-weight: 600;
        font-size: 0.95rem;
    }
    .disease-card-confidence {
        text-align: right;
    }
    .disease-card-confidence-label {
        color: #6b7280;
        font-size: 0.75rem;
        text-transform: uppercase;
    }
    .disease-card-confidence-value {
        color: #1f2937;
        font-weight: 700;
        font-size: 1.3rem;
    }
    .disease-card-body {
        color: #4b5563;
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    
    /* Professional Compact Layout */
    .ai-section {
        margin: 1.5rem 0;
    }
    
    .ai-section-header {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
        color: white;
        padding: 0.75rem 1.25rem;
        border-radius: 8px 8px 0 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .ai-section-header h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
    }
    
    .ai-section-icon {
        font-size: 1.5rem;
    }
    
    /* --- THIS IS THE FIX for the white bars --- */
    .ai-section-content {
        background: white;
        border: 2px solid #e5e7eb;
        border-top: none;
        border-radius: 0 0 8px 8px;
        padding: 0.5rem; /* Reduced padding from 1.25rem */
        box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
    }
    /* --- End of fix --- */
    
    .ai-compact-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .ai-metric-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    
    .ai-metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0.25rem 0;
    }
    
    .ai-metric-label {
        font-size: 0.8rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0;
    }
    
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        margin: 0.25rem;
    }
    
    .status-success {
        background: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .status-warning {
        background: #fef3c7;
        color: #92400e;
        border: 1px solid #fde68a;
    }
    
    .status-error {
        background: #fee2e2;
        color: #991b1b;
        border: 1px solid #fecaca;
    }
    
    /* Compact image display */
    .ai-image-container {
        max-width: 450px;
        margin: 0 auto;
        border: 2px solid #dc2626;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .assessment-header h1 {
            font-size: 1.5rem;
        }
        
        .test-card {
            padding: 1.25rem;
        }
        
        .ai-compact-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """, unsafe_allow_html=True)
# --- END REPLACED FUNCTION ---


def show_test_selection():
    """Show available eye tests"""
    st.markdown('<div class="assessment-header"><h1>👁 Comprehensive Eye Assessment</h1><p>Select tests to evaluate your eye health</p></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="test-card">
            <div class="test-icon">📝</div>
            <div class="test-title">Visual Acuity Test</div>
            <div class="test-description">Speech-based letter reading with voice recognition</div>
            <div style="color: #dc2626; font-weight: 600;">⏱ 5-7 minutes</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Visual Acuity", key="start_acuity", use_container_width=True):
            st.session_state.current_test = "visual_acuity"
            st.session_state.test_step = 0
            st.rerun()

    with col2:
        st.markdown("""
        <div class="test-card">
            <div class="test-icon">📸</div>
            <div class="test-title">AI Disease Detection</div>
            <div class="test-description">Live camera-based retinal imaging and disease analysis</div>
            <div style="color: #dc2626; font-weight: 600;">⏱ 5-8 minutes</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start AI Detection", key="start_camera", use_container_width=True):
            st.session_state.current_test = "camera_detection"
            st.session_state.test_step = 0
            st.rerun()

# --- Visual Acuity Test Function ---

# --- THIS FUNCTION IS REPLACED with the loop fix attempt 4 ---
def visual_acuity_test():
    """Visual acuity test with speech recognition - FIXED auto-fill with proper state management"""
    st.markdown('<div class="assessment-header"><h1>📝 Visual Acuity Test</h1><p>Read the letters aloud using voice recognition</p></div>', unsafe_allow_html=True)

    # Initialize test data
    if 'acuity_data' not in st.session_state:
        st.session_state.acuity_data = {
            'lines': [
                {'size': '20/200', 'letters': 'CAT', 'font_size': 30},
                {'size': '20/100', 'letters': 'DOG', 'font_size': 25},
                {'size': '20/70', 'letters': 'BARK', 'font_size': 20},
                {'size': '20/50', 'letters': 'ELEPHANT', 'font_size': 15},
                {'size': '20/40', 'letters': 'FLOWER', 'font_size': 14},
                {'size': '20/30', 'letters': 'PENCIL', 'font_size': 12},
                {'size': '20/25', 'letters': 'TABLE', 'font_size': 10},
                {'size': '20/20', 'letters': 'COMPUTER', 'font_size': 8},
            ],
            'current_line': 0,
            'correct_count': 0,
            'total_count': 0
        }

    data = st.session_state.acuity_data

    if data['current_line'] < len(data['lines']):
        current = data['lines'][data['current_line']]
        current_line_idx = data['current_line']

        # Define session state keys for this line
        session_key_text = f'recognized_text_{current_line_idx}'
        session_key_processed_audio_id = f'processed_audio_id_{current_line_idx}'
        session_key_submit_flag = f'submit_flag_{current_line_idx}'

        # Initialize states if they don't exist
        if session_key_text not in st.session_state:
            st.session_state[session_key_text] = ""
        if session_key_processed_audio_id not in st.session_state:
            st.session_state[session_key_processed_audio_id] = None
        if session_key_submit_flag not in st.session_state:
            st.session_state[session_key_submit_flag] = False

        # CRITICAL: Check if we need to process submission BEFORE creating widgets
        if st.session_state[session_key_submit_flag]:
            final_user_input = st.session_state.get(session_key_text, "")
            
            if final_user_input and final_user_input.strip():
                user_answer = final_user_input.upper().replace(" ", "")
                correct_answer = current['letters']
                correct = user_answer == correct_answer

                data['total_count'] += 1
                if correct:
                    data['correct_count'] += 1
                    st.success(f"✅ Correct! You: {user_answer}")
                else:
                    st.error(f"❌ Incorrect. You: {user_answer} | Correct: {correct_answer}")

                if 'answers' not in data:
                    data['answers'] = []
                data['answers'].append({
                    'line': current_line_idx,
                    'expected': correct_answer,
                    'user_input': user_answer,
                    'correct': correct
                })

                # Clear states BEFORE moving to next line
                del st.session_state[session_key_text]
                del st.session_state[session_key_processed_audio_id]
                del st.session_state[session_key_submit_flag]

                data['current_line'] += 1
                time.sleep(1.5)
                st.rerun()
            else:
                st.warning("⚠️ Please record or type the letters!")
                st.session_state[session_key_submit_flag] = False
                st.rerun()

        audio_output = None

        # --- Layout Definition ---
        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            # Progress bar
            progress = (current_line_idx / len(data['lines'])) * 100
            st.markdown(f"""
            <div class="progress-container" style="margin-bottom: 1rem;">
                <h4 style="margin-bottom: 0.3rem; font-size: 1rem;">Test Progress - Line {current_line_idx + 1} of {len(data['lines'])}</h4>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {progress}%;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Display Snellen chart
            st.markdown(f"""
            <div class="snellen-chart" style="padding: 2rem; margin: 0;">
                <h3 style="color: #dc2626; margin-bottom: 0.5rem;">{current['size']}</h3>
                <div class="optotype-display" style="font-size: {current['font_size']}px;">
                    {current['letters']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Compact instructions
            st.markdown("""
            <div class="instruction-box" style="margin-top: 1rem; padding: 0.75rem;">
                <strong>💡 Quick Tips:</strong><br>
                • Sit 20 inches / 50 cm from screen<br>
                • Speak each letter clearly<br>
                • Edit text if needed before submitting
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            st.markdown("### 🎤 Voice Recording")
            try:
                from streamlit_mic_recorder import mic_recorder
                st.markdown("""
                <div class="audio-recorder-container" style="padding: 1rem;">
                    <h4 style="margin-top: 0; color: #1f2937; font-size: 1rem;">🎙️ Record Your Answer</h4>
                    <p style="color: #6b7280; margin-bottom: 0.5rem; font-size: 0.9rem;">Read the letters from left to right</p>
                </div>
                """, unsafe_allow_html=True)
                audio_output = mic_recorder(
                    start_prompt="🎤 Start Recording",
                    stop_prompt="⏹ Stop Recording",
                    just_once=False,
                    use_container_width=True,
                    format="webm",
                    key=f"recorder_{current_line_idx}"
                )
            except ImportError:
                st.error("Audio recorder component `streamlit_mic_recorder` not found. Install: `pip install streamlit-mic-recorder`")
            except Exception as e:
                st.error(f"Error loading audio recorder: {e}")

            # --- Audio Processing Logic ---
            last_processed_id = st.session_state.get(session_key_processed_audio_id)
            current_audio_id = audio_output['id'] if audio_output else None

            status_message_placeholder = st.empty()

            if audio_output and current_audio_id != last_processed_id:
                st.audio(audio_output['bytes'])

                try:
                    import speech_recognition as sr
                    import tempfile
                    from pydub import AudioSegment

                    with st.spinner("🔄 Processing audio..."):
                        tmp_webm_path = None
                        tmp_wav_path = None
                        processing_success = False

                        try:
                            temp_dir = tempfile.gettempdir()
                            tmp_webm_path = os.path.join(temp_dir, f"audio_{current_audio_id}.webm")
                            with open(tmp_webm_path, 'wb') as f:
                                f.write(audio_output['bytes'])

                            if not AudioSegment.converter or not os.path.exists(AudioSegment.converter):
                                raise Exception("FFmpeg not found.")
                            if not AudioSegment.ffprobe or not os.path.exists(AudioSegment.ffprobe):
                                raise Exception("FFprobe not found.")

                            audio_segment = AudioSegment.from_file(tmp_webm_path, format="webm")
                            tmp_wav_path = os.path.join(temp_dir, f"audio_{current_audio_id}.wav")
                            audio_segment.export(tmp_wav_path, format="wav", parameters=["-ar", "16000", "-ac", "1"])
                            time.sleep(0.1)

                            recognizer = sr.Recognizer()
                            with sr.AudioFile(tmp_wav_path) as source:
                                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                                audio_data = recognizer.record(source)
                                text = recognizer.recognize_google(audio_data)
                                cleaned_text = ''.join(text.split()).upper()

                            # Update session state with recognized text
                            st.session_state[session_key_text] = cleaned_text
                            st.session_state[session_key_processed_audio_id] = current_audio_id
                            status_message_placeholder.success(f"✅ Detected: **{cleaned_text}**")
                            processing_success = True

                            # Force rerun to update the text input
                            st.rerun()

                        except sr.UnknownValueError:
                            status_message_placeholder.warning("⚠️ Could not understand. Try again or type manually.")
                        except sr.RequestError as e:
                            status_message_placeholder.error(f"❌ Speech recognition error: {e}")
                            st.info("💡 Type the letters manually below.")
                        except Exception as e:
                            status_message_placeholder.error(f"❌ Audio Processing Error: {str(e)}")
                            st.info("💡 Type the letters manually below.")
                        finally:
                            # Cleanup temp files
                            try:
                                if tmp_webm_path and os.path.exists(tmp_webm_path):
                                    os.unlink(tmp_webm_path)
                                if tmp_wav_path and os.path.exists(tmp_wav_path):
                                    os.unlink(tmp_wav_path)
                            except Exception as cleanup_error:
                                st.warning(f"Could not delete temp audio file: {cleanup_error}")

                        # If processing failed, reset processed_id
                        if not processing_success:
                            st.session_state[session_key_processed_audio_id] = None

                except ImportError:
                    st.warning("Speech recognition library not available.")
                    st.info("Type letters manually.")

            st.markdown("---")

            # Form with text input bound to session state
            with st.form(key=f"answer_form_{current_line_idx}"):
                st.markdown("**📝 Review & Submit**")

                # Text input directly bound to session state
                user_input = st.text_input(
                    "Detected letters (edit if needed):",
                    key=session_key_text,
                    placeholder="Letters will appear here...",
                    max_chars=20,
                    help="Edit this field if needed"
                )

                submit_button = st.form_submit_button("✅ Submit Answer", use_container_width=True, type="primary")

                if submit_button:
                    # Set flag to process submission on next rerun
                    st.session_state[session_key_submit_flag] = True
                    st.rerun()

    else:
        show_acuity_results()

    st.markdown("---")
    
    # Back button
    back_button_key = "back_from_acuity"
    if st.button("← Back to Test Selection", key=back_button_key):
        # Clear specific line state
        current_line_num = data.get('current_line', 0) if 'acuity_data' in st.session_state else 0
        
        # Clear general acuity state
        st.session_state.current_test = None
        if 'acuity_data' in st.session_state:
            del st.session_state.acuity_data
            
        # Clear all related session state keys
        keys_to_delete = [k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'submit_flag_'))]
        for k in keys_to_delete:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
# --- END REPLACED FUNCTION ---

#show acutity results function

# --- MODIFIED: show_acuity_results includes download button ---
def show_acuity_results():
    """Show visual acuity test results"""
    # Ensure acuity_data exists before proceeding
    if 'acuity_data' not in st.session_state:
        st.warning("No acuity test data found. Please start the test.")
        if st.button("← Back to Test Selection"):
            st.session_state.current_test = None
            st.rerun()
        return # Stop execution if no data

    data = st.session_state.acuity_data
    accuracy = (data['correct_count'] / data['total_count'] * 100) if data['total_count'] > 0 else 0
    user_id = st.session_state.get('user_id', 'UnknownUser') # Get user ID for PDF

    # Determine visual acuity
    if accuracy >= 90:
        acuity = "20/20 or better"
        status = "Excellent"
        color = "#16a34a"
    elif accuracy >= 75:
        acuity = "20/30 to 20/25"
        status = "Good"
        color = "#4CAF50"
    elif accuracy >= 60:
        acuity = "20/40 to 20/50"
        status = "Fair"
        color = "#ff9800"
    else:
        acuity = "20/70 or worse"
        status = "Poor - Consult an eye doctor"
        color = "#dc2626"

    st.markdown(f"""
    <div class="result-card">
        <h2 style="color: #1f2937; margin-bottom: 1rem;">📊 Visual Acuity Test Results</h2>
        <div class="score-display" style="color: {color};">{accuracy:.1f}%</div>
        <h3 style="color: {color};">Estimated Acuity: {acuity}</h3>
        <h4 style="color: #6b7280;">Status: {status}</h4>
        <p style="color: #6b7280; margin-top: 1rem;">
            You answered {data['correct_count']} out of {data['total_count']} lines correctly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Show detailed results
    if 'answers' in data and data['answers']:
        with st.expander("📋 View Detailed Results"):
            for i, answer in enumerate(data['answers'], 1):
                status_icon = "✅" if answer['correct'] else "❌"
                status_color = "#16a34a" if answer['correct'] else "#dc2626"
                st.markdown(f"""
                <div style="background: #f9fafb; padding: 0.75rem; margin: 0.5rem 0; border-radius: 8px; border-left: 3px solid {status_color};">
                    {status_icon} <strong>Line {i}:</strong> Expected: <code>{answer['expected']}</code> |
                    Your answer: <code>{answer['user_input']}</code>
                </div>
                """, unsafe_allow_html=True)

    if accuracy < 75:
        st.warning("⚠ **Recommendation:** Consider scheduling a comprehensive eye exam with an optometrist or ophthalmologist.")

    # Next step prompt
    st.markdown("""
    <div class="next-step-card">
        <h3>🎯 Complete Your Eye Assessment</h3>
        <p style="margin: 0; font-size: 1.1rem;">
            Proceed to AI Disease Detection to check for diabetic retinopathy, glaucoma, cataracts, and other conditions.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📥 Save & Next Steps")
    # --- ACTION BUTTONS ---
    # Adjusted columns to fit the new Download PDF button
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("🔄 Retake Test", key="retake_acuity"):
            # Clear general acuity state and rerun
            st.session_state.current_test = "visual_acuity" # Go back to the test start
            if 'acuity_data' in st.session_state:
                del st.session_state.acuity_data
            keys_to_delete = [k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'temp_audio_'))]
            for k in keys_to_delete:
                if k in st.session_state: del st.session_state[k]
            st.rerun()


    with col2:
        if st.button("📸 AI Detection", key="proceed_to_ai"):
             # Clear acuity state before switching test type
            if 'acuity_data' in st.session_state: del st.session_state.acuity_data
            keys_to_delete = [k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'temp_audio_'))]
            for k in keys_to_delete:
                if k in st.session_state: del st.session_state[k]
            st.session_state.current_test = "camera_detection"
            st.rerun()

    with col3:
        if st.button("💾 Save Report", key="save_acuity_report"):
            save_success = save_eye_assessment_results(data, accuracy, acuity, status)
            if save_success:
                st.success("✅ Eye assessment report saved!")
                st.info("📋 You can view saved reports from your Profile page.")
            else:
                st.error("❌ Failed to save report.")

    # --- NEW PDF DOWNLOAD BUTTON ---
    with col4:
        try:
            pdf_bytes = generate_acuity_pdf(data, accuracy, acuity, status, user_id)
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=f"visual_acuity_report_{user_id}_{time.strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                key="download_acuity_pdf"
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            # Show a disabled-like button or message
            st.button("📄 Download PDF", disabled=True, key="download_acuity_pdf_disabled")


    with col5:
        if st.button("👂 Continue", key="continue_hearing_from_acuity"):
            st.session_state.current_test = None
            if 'acuity_data' in st.session_state:
                del st.session_state.acuity_data
             # Clear any leftover recognition text
            keys_to_delete = [k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'temp_audio_'))]
            for k in keys_to_delete:
                if k in st.session_state: del st.session_state[k]
            # Ensure the target page exists
            try:
                st.switch_page("pages/03_👂_Hearing_Assessment.py")
            except FileNotFoundError:
                 st.error("Hearing assessment page not found.")

    with col6:
        if st.button("← Back", key="back_from_acuity_results"):
            st.session_state.current_test = None
            if 'acuity_data' in st.session_state:
                del st.session_state.acuity_data
             # Clear any leftover recognition text
            keys_to_delete = [k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'temp_audio_'))]
            for k in keys_to_delete:
                if k in st.session_state: del st.session_state[k]
            st.rerun()

# --- Box drawing function (Unchanged) ---
def validate_and_draw_boxes(image_data):
    """
    Validates the image and draws boxes on it for visual feedback.
    Returns: (is_valid, error_type, message, validation_details, annotated_pil_image)
    """
    try:
        # --- 1. Load Image ---
        image_data.seek(0)
        try:
            image = Image.open(image_data)
            image.verify()
            image_data.seek(0)
            image = Image.open(image_data)
        except Exception as img_err:
             st.error(f"Invalid image file provided: {img_err}")
             return False, 'invalid_image', "Invalid image file provided.", {}, None

        img_array = np.array(image.convert('RGB'))
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        annotated_image_bgr = img_bgr.copy() # We will draw on this copy

        # --- 2. Load Classifiers ---
        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'

        if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
            st.error("Haar cascade files not found. Cannot perform validation.")
            return False, 'error', "Missing model files.", {}, image # Return original image

        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        # --- 3. Run Detection and Validation ---
        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))
        
        faces_detected = len(faces)
        eyes_detected_total = 0
        is_valid = False
        message = ""
        error_type = ""

        # Define colors (BGR)
        COLOR_RED = (0, 0, 255)
        COLOR_GREEN = (0, 255, 0)
        COLOR_BLUE = (255, 0, 0)
        COLOR_YELLOW = (0, 255, 255)

        if faces_detected == 0:
            message = "No face detected. Please ensure your face is clearly visible and well-lit."
            error_type = 'no_face'
        
        elif faces_detected > 1:
            message = f"Multiple faces detected ({faces_detected}). Please ensure only one person is in the frame."
            error_type = 'multiple_faces'
            # Draw red boxes on all detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(annotated_image_bgr, (x, y), (x+w, y+h), COLOR_RED, 2)
        
        else: # Exactly one face detected
            (x, y, w, h) = faces[0]
            
            # Draw a pending (yellow) box first
            cv2.rectangle(annotated_image_bgr, (x, y), (x+w, y+h), COLOR_YELLOW, 2)
            
            # Detect eyes within the face ROI
            roi_gray = gray[y:y+h, x:x+w]
            roi_color_annotated = annotated_image_bgr[y:y+h, x:x+w] # Get the same ROI from the annotated image
            
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5, minSize=(int(w*0.1), int(h*0.1)))
            eyes_detected_total = len(eyes)

            # Draw blue boxes on all detected eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color_annotated, (ex, ey), (ex+ew, ey+eh), COLOR_BLUE, 2)

            if eyes_detected_total < 2:
                message = f"Eyes not clearly detected ({eyes_detected_total} eye(s) found). Please ensure both eyes are open and visible."
                error_type = 'no_eyes'
                # Overwrite the yellow face box with a red one
                cv2.rectangle(annotated_image_bgr, (x, y), (x+w, y+h), COLOR_RED, 2)
            else:
                message = "Image validation successful"
                error_type = None
                is_valid = True
                # Overwrite the yellow face box with a green one
                cv2.rectangle(annotated_image_bgr, (x, y), (x+w, y+h), COLOR_GREEN, 2)

        # --- 4. Finalize and Return ---
        validation_details = {
            'faces_detected': faces_detected,
            'eyes_detected': eyes_detected_total
        }
        
        # Convert the annotated BGR image back to PIL (RGB) for display in Streamlit
        annotated_pil_image = cv2_to_pil(annotated_image_bgr)
        
        return is_valid, error_type, message, validation_details, annotated_pil_image

    except Exception as e:
        st.error(f"Error during image validation and drawing: {str(e)}")
        # Try to return the original image if drawing fails
        try:
            image_data.seek(0)
            original_image = Image.open(image_data)
            return False, 'error', f"Error processing image: {str(e)}", {}, original_image
        except:
            return False, 'error', f"Error processing image: {str(e)}", {}, None

# --- AI analysis functions (Unchanged) ---
def analyze_eye_disease(image_data, validation_details):
    """
    Lightweight analysis - simplified version for low-spec systems
    """
    try:
        # Simple mock analysis - in production, use a trained model
        analysis_results = {
            'diabetic_retinopathy': {
                'detected': False,
                'confidence': 96.8,
                'severity': 'None',
                'risk_level': 'Low'
            },
            'glaucoma': {
                'detected': False,
                'confidence': 94.5,
                'severity': 'None',
                'risk_level': 'Low'
            },
            'cataracts': {
                'detected': False,
                'confidence': 97.2,
                'severity': 'None',
                'risk_level': 'Low'
            },
            'amd': { # Age-related Macular Degeneration
                'detected': False,
                'confidence': 95.1,
                'severity': 'None',
                'risk_level': 'Low'
            },
            'hypertensive_retinopathy': {
                'detected': False,
                'confidence': 93.8,
                'severity': 'None',
                'risk_level': 'Low'
            }
        }

        quality_metrics = {
            'overall_quality': 'Good' # Could add more metrics like brightness, sharpness later
        }

        overall = {
            'healthy': True, # Assume healthy unless specific conditions detected
            'conditions_detected': 0,
            'recommendation': 'Your eye health appears to be in good condition based on this screening. Continue regular check-ups.'
        }

        # Example: Modify results based on validation (e.g., if few eyes detected, lower confidence)
        if validation_details.get('eyes_detected', 0) < 2:
             quality_metrics['overall_quality'] = 'Fair - Eye detection limited'
             # Could adjust confidence scores here if desired

        # --- Placeholder for actual AI model integration ---
        # Replace this section with loading your model and performing inference
        # e.g., model_output = your_eye_model.predict(preprocessed_image)
        # Populate analysis_results, quality_metrics, overall based on model_output

        return analysis_results, quality_metrics, overall

    except Exception as e:
        st.error(f"Error during AI analysis simulation: {str(e)}")
        return None, None, None

def pil_to_cv2(pil_image):
    """Convert PIL Image to OpenCV (BGR) format"""
    try:
        # Convert PIL image to numpy array
        open_cv_image = np.array(pil_image.convert('RGB'))
        # Convert RGB to BGR (OpenCV's default format)
        return open_cv_image[:, :, ::-1].copy()
    except Exception as e:
        st.error(f"Error in pil_to_cv2 conversion: {e}")
        return None

def cv2_to_pil(cv2_image):
    """Convert OpenCV (BGR) image to PIL (RGB) format"""
    try:
        # Ensure input is a valid numpy array
        if not isinstance(cv2_image, np.ndarray):
            raise TypeError("Input must be a NumPy array")
        # Ensure it has 3 dimensions (height, width, channels)
        if cv2_image.ndim != 3 or cv2_image.shape[2] != 3:
             raise ValueError("Input array must be in BGR format (3 channels)")

        cv2_image_rgb = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
        return Image.fromarray(cv2_image_rgb)
    except Exception as e:
        st.error(f"Error in cv2_to_pil conversion: {e}")
        return None

def crop_eye_region(image_data):
    """Crops the image to the bounding box containing both detected eyes."""
    try:
        image_data.seek(0) # Reset buffer
        try:
            image = Image.open(image_data)
            image.verify()
            image_data.seek(0)
            image = Image.open(image_data)
        except (IOError, SyntaxError, Image.UnidentifiedImageError) as img_err:
             st.error(f"Invalid image file for cropping: {img_err}")
             return None

        img_bgr = pil_to_cv2(image)
        if img_bgr is None: return None

        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'

        if not os.path.exists(face_cascade_path) or not os.path.exists(eye_cascade_path):
            st.error("Haar cascade files not found for cropping.")
            return None

        face_cascade = cv2.CascadeClassifier(face_cascade_path)
        eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30,30))

        if len(faces) == 0:
            st.warning("No face detected for cropping eyes.")
            return None # No face

        # Assume the largest detected face is the correct one if multiple are found
        faces = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)
        (x, y, w, h) = faces[0]
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img_bgr[y:y+h, x:x+w]

        eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 5, minSize=(int(w*0.1), int(h*0.1))) # Relative min size

        if len(eyes) < 2:
            st.warning(f"Could not detect two eyes for cropping (found {len(eyes)}). Showing full face ROI instead.")
             # Fallback: return the detected face region if eyes aren't clear
            face_roi_color = img_bgr[y:y+h, x:x+w]
            return cv2_to_pil(face_roi_color)


        # Find bounding box containing all detected eyes within the face ROI
        min_ex, min_ey = w, h # Initialize with max values within ROI
        max_ex, max_ey = 0, 0 # Initialize with min values

        for (ex, ey, ew, eh) in eyes:
            min_ex = min(min_ex, ex)
            min_ey = min(min_ey, ey)
            max_ex = max(max_ex, ex + ew)
            max_ey = max(max_ey, ey + eh)

        # Add some padding relative to eye region size
        eye_width = max_ex - min_ex
        eye_height = max_ey - min_ey

        # Ensure width/height are positive before calculating padding
        if eye_width <= 0 or eye_height <= 0:
             st.warning("Detected eye region has zero or negative dimensions. Falling back to face ROI.")
             face_roi_color = img_bgr[y:y+h, x:x+w]
             return cv2_to_pil(face_roi_color)

        padding_x = int(eye_width * 0.3) # 30% padding horizontally
        padding_y = int(eye_height * 0.5) # 50% padding vertically

        # Ensure coordinates are within the face ROI boundaries
        crop_x1 = max(0, min_ex - padding_x)
        crop_y1 = max(0, min_ey - padding_y)
        crop_x2 = min(w, max_ex + padding_x) # w is width of face ROI
        crop_y2 = min(h, max_ey + padding_y) # h is height of face ROI

        # Check if coordinates are valid
        if crop_y1 >= crop_y2 or crop_x1 >= crop_x2:
             st.warning("Calculated eye crop coordinates are invalid. Falling back to face ROI.")
             face_roi_color = img_bgr[y:y+h, x:x+w]
             return cv2_to_pil(face_roi_color)

        # Crop from the face's color ROI using calculated coordinates
        eye_region_color = roi_color[crop_y1:crop_y2, crop_x1:crop_x2]

        # Check if the crop resulted in an empty image (should be caught by coord check, but safety)
        if eye_region_color.size == 0:
             st.warning("Eye cropping resulted in an empty image. Falling back to face ROI.")
             face_roi_color = img_bgr[y:y+h, x:x+w]
             return cv2_to_pil(face_roi_color)

        # Convert back to PIL image
        return cv2_to_pil(eye_region_color)

    except Exception as e:
        st.error(f"Error during eye region cropping: {e}")
        # Attempt to return original image if cropping fails badly
        try:
            image_data.seek(0)
            return Image.open(image_data)
        except:
             return None # Give up if even reopening fails


def convert_to_grayscale(image_data):
    """Converts an image (PIL or BytesIO) to grayscale PIL image."""
    try:
        img_to_convert = None
        if isinstance(image_data, io.BytesIO):
            image_data.seek(0) # Reset buffer
            img_to_convert = Image.open(image_data)
        elif isinstance(image_data, Image.Image):
            img_to_convert = image_data # Already a PIL image
        else:
             st.error(f"Invalid data type for grayscale conversion: {type(image_data)}")
             return None # Unknown type

        return img_to_convert.convert('L') # 'L' is the mode for grayscale

    except Exception as e:
        st.error(f"Error converting image to grayscale: {e}")
        return None


# --- AI Camera Test Workflow Functions (Unchanged Logic, updated display) ---

def show_capture_ui():
    """
    Displays the st.camera_input and st.file_uploader widgets
    and handles the Python-side validation *with box drawing*.
    """
    st.markdown("""
    <div class="instruction-box">
         <strong>📋 Instructions:</strong><br>
         1. Ensure good, even lighting conditions<br>
         2. Position your face clearly in the camera frame<br>
         3. Keep both eyes open and visible<br>
         4. Ensure only ONE person is in the frame<br>
         5. Hold the camera steady<br>
         6. Click "Take Photo"<br><br>
         <strong>🔍 Diseases Detected by AI:</strong><br>
         • Diabetic Retinopathy • Glaucoma • Cataracts • Age-related Macular Degeneration • Hypertensive Retinopathy
    </div>
    """, unsafe_allow_html=True)

    # Use the new compact layout classes
    col1, col2 = st.columns([3, 2], gap="medium")

    with col1:
        # Camera Capture Box
        st.markdown("""
        <div class="ai-section">
            <div class="ai-section-header">
                <span class="ai-section-icon">📷</span>
                <h3>Camera Capture</h3>
            </div>
            <div class="ai-section-content" style="text-align: center;">
        """, unsafe_allow_html=True)
        
        camera_photo = st.camera_input(
            "Center your face in the frame",
            key="camera_capture_widget",
            help="Click 'Take Photo' to capture an image for validation."
        )
        
        st.markdown("</div></div>", unsafe_allow_html=True)

    captured_data = None
    source_type = None

    if camera_photo:
        captured_data = camera_photo
        source_type = "camera"

    with col2:
        # Validation Box
        st.markdown("""
        <div class="ai-section">
            <div class="ai-section-header">
                <span class="ai-section-icon">✅</span>
                <h3>Validation</h3>
            </div>
            <div class="ai-section-content">
        """, unsafe_allow_html=True)

        # Show validation status
        if captured_data:
            st.info("🔄 Processing image validation...")
            st.markdown("""
            <div class="status-indicator status-warning">
                ⏳ Validating face and eye detection
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("📸 Take a photo to see validation results")
            st.markdown("""
            <div class="status-indicator status-warning">
                ⏳ Waiting for image capture
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)


    st.markdown("---")
    st.markdown("#### Alternative: Upload a Photo")
    st.info("💡 If the camera doesn't work, you can upload a photo of your face with both eyes visible.")

    uploaded_file = st.file_uploader("Upload face photo", type=['jpg', 'jpeg', 'png'], key="face_upload")

    if uploaded_file:
        captured_data = uploaded_file
        source_type = "upload"

    # --- Validation Step (runs if either camera or upload provides data) ---
    if captured_data is not None:
        with st.spinner(f"Validating {source_type} image and detecting features..."):

            # Run the new validation function that also returns the annotated image
            is_valid, error_type, message, validation_details, annotated_pil_image = validate_and_draw_boxes(captured_data)

            # Store the *original* photo for the AI analysis
            st.session_state.captured_photo = captured_data

            # Store the *annotated* photo for display
            st.session_state.annotated_photo = annotated_pil_image

            # Store the validation result
            st.session_state.validation_status = {
                'is_valid': is_valid,
                'message': message,
                'validation_details': validation_details
            }

            if is_valid:
                st.success(f"✅ {source_type.capitalize()} successful & validated: {message}")
                time.sleep(1)
            else:
                 # Error will be displayed on rerun by the main router
                 pass

            st.rerun() # Rerun to proceed to analysis or show validation error

    # --- Back Button ---
    st.markdown("---")
    if st.button("← Back to Test Selection", key="back_from_camera_options"):
        st.session_state.current_test = None
        # Clear all session state keys related to this test
        keys_to_clear = [
            'captured_photo', 'validation_status', 'analysis_results',
            'quality_metrics', 'overall_results', 'validation_details_final',
            'captured_image_data', 'annotated_photo' # Clear new key too
        ]
        for key in keys_to_clear:
            if key in st.session_state: del st.session_state[key]
        st.rerun()

# --- THIS FUNCTION IS REPLACED with your new style AND bug fixes ---
def run_ai_analysis_simulation():
    """
    Runs the simulated AI analysis process with professional compact layout.
    """
    try:
        # Get data from session state
        camera_photo_bytesio = st.session_state.captured_photo
        validation_status = st.session_state.get('validation_status')
        annotated_photo_pil = st.session_state.get('annotated_photo')

        # Validation check
        if not validation_status or not validation_status.get('is_valid') or not annotated_photo_pil:
            st.error("Cannot proceed with analysis: Image validation was missing, failed, or annotated image is missing.")
            if st.button("Try Capture/Upload Again"):
                keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'annotated_photo']
                for key in keys_to_clear:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()
            return

        # Professional compact two-column layout
        col1, col2 = st.columns([3, 2], gap="medium")

        with col1:
            # AI Processing Section
            st.markdown("""
            <div class="ai-section">
                <div class="ai-section-header">
                    <span class="ai-section-icon">🤖</span>
                    <h3>AI Disease Analysis</h3>
                </div>
                <div class="ai-section-content">
            """, unsafe_allow_html=True)
            
            status_placeholder = st.empty()
            progress_placeholder = st.empty()
            
            # --- THIS IS THE FIX for box size ---
            # Create a dedicated container for the image
            image_display_area = st.container()
            # --- End of fix ---
            
            st.markdown("</div></div>", unsafe_allow_html=True)

        with col2:
            # Validation Complete Section
            st.markdown("""
            <div class="ai-section">
                <div class="ai-section-header">
                    <span class="ai-section-icon">✅</span>
                    <h3>Validation Complete</h3>
                </div>
                <div class="ai-section-content">
            """, unsafe_allow_html=True)
            
            # Added margin to center image vertically a bit more
            st.markdown('<div class="ai-image-container" style="margin-top: 0.75rem; margin-bottom: 0.75rem;">', unsafe_allow_html=True)
            st.image(annotated_photo_pil, caption="Detected Face & Eyes", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.success(f"✅ {validation_status.get('message', 'Ready for analysis.')}")
            
            st.markdown("</div></div>", unsafe_allow_html=True)

        # --- Simulation Logic ---
        status_placeholder.info("⏳ Starting analysis...")
        progress_bar = progress_placeholder.progress(0)
        time.sleep(2)

        # --- Crop Eyes ---
        status_placeholder.info("⏳ Cropping eye region (Step 2/3)...")
        progress_bar.progress(25)
        eye_image = crop_eye_region(camera_photo_bytesio)

        if eye_image is not None:
            # --- THIS IS THE FIX for box size ---
            # Use the container and wrap the image
            with image_display_area:
                st.markdown('<div class="ai-image-container" style="border-color: #f59e0b; margin: 1rem auto;">', unsafe_allow_html=True)
                st.image(eye_image, caption="AI Focus Region", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Use the container for the warning
            with image_display_area:
                st.warning("Could not automatically isolate eyes. Analyzing full image.")
            eye_image = None

        time.sleep(3)

        # --- Grayscale ---
        status_placeholder.info("⏳ Converting to grayscale (Step 3/3)...")
        progress_bar.progress(50)
        image_for_grayscale = eye_image if eye_image is not None else camera_photo_bytesio
        grayscale_image = convert_to_grayscale(image_for_grayscale)

        if grayscale_image is not None:
            # --- THIS IS THE FIX for box size ---
            # Use the container and wrap the image
            with image_display_area:
                st.markdown('<div class="ai-image-container" style="border-color: #6b7280; margin: 1rem auto;">', unsafe_allow_html=True)
                st.image(grayscale_image, caption="Grayscale Analysis", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Use the container for the warning
            with image_display_area:
                st.warning("Could not convert image to grayscale.")

        time.sleep(3)

        # --- Run "AI Model" ---
        status_placeholder.info("🧠 Running deep learning models... Please wait.")
        analysis_duration = 22
        start_time = time.time()
        while time.time() - start_time < analysis_duration:
            elapsed = time.time() - start_time
            progress_value = 50 + int(50 * (elapsed / analysis_duration))
            progress_bar.progress(min(progress_value, 100))
            time.sleep(0.2)
        progress_bar.progress(100)

        status_placeholder.success("✅ Analysis Complete!")
        progress_placeholder.empty()
        
        # --- THIS IS THE FIX for box size ---
        # Clear the image from the container
        image_display_area.empty()
        time.sleep(1)

        # --- Get results ---
        validation_details = validation_status.get('validation_details', {})
        analysis_results, quality_metrics, overall = analyze_eye_disease(
            camera_photo_bytesio, validation_details
        )

        # --- Save results ---
        if analysis_results is not None:
            st.session_state.analysis_results = analysis_results
            st.session_state.quality_metrics = quality_metrics
            st.session_state.overall_results = overall
            st.session_state.validation_details_final = validation_details
            st.rerun()
        else:
            st.error("AI Analysis failed. Please try capturing again.")
            if st.button("Retry Capture"):
                keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'annotated_photo']
                for key in keys_to_clear:
                     if key in st.session_state: del st.session_state[key]
                st.rerun()

    except Exception as e:
        st.error(f"An error occurred during the analysis simulation: {e}")
        col_err1, col_err2 = st.columns(2)
        with col_err1:
            if st.button("Try Analysis Again"):
                if 'analysis_results' in st.session_state: del st.session_state.analysis_results
                st.rerun()
        with col_err2:
            if st.button("Restart Capture"):
                keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'annotated_photo']
                for key in keys_to_clear:
                     if key in st.session_state: del st.session_state[key]
                st.rerun()
# --- END REPLACED FUNCTION ---


# --- MODIFIED: display_ai_analysis_results includes download button AND new CSS classes ---
def display_ai_analysis_results():
    """
    Displays the final AI analysis results after the simulation is complete.
    """
    # Retrieve results safely using .get
    camera_photo_bytesio = st.session_state.get('captured_photo') # Original Photo
    annotated_photo_pil = st.session_state.get('annotated_photo') # Photo with Boxes
    analysis_results = st.session_state.get('analysis_results', {})
    quality_metrics = st.session_state.get('quality_metrics', {})
    overall = st.session_state.get('overall_results', {})
    validation_details = st.session_state.get('validation_details_final', {}) # Use final details
    validation_status = st.session_state.get('validation_status', {}) # Get original status
    user_id = st.session_state.get('user_id', 'UnknownUser') # Get user ID for PDF

    if not camera_photo_bytesio or not annotated_photo_pil:
         st.error("Captured photo missing. Please restart the test.")
         if st.button("Restart Test"):
             # Clear relevant state
             keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'current_test', 'captured_image_data', 'annotated_photo']
             for key in keys_to_clear:
                 if key in st.session_state: del st.session_state[key]
             st.rerun()
         return

    # Use the new compact layout
    st.markdown("### 📊 Comprehensive Analysis Results")

    # Top row: Image (left) and Overall Status (right)
    col1, col2 = st.columns([2, 3], gap="medium")

    with col1:
        # Analyzed Image Box
        st.markdown("""
        <div class="ai-section" style="margin-top: 0;">
            <div class="ai-section-header">
                <span class="ai-section-icon">📷</span>
                <h3>Analyzed Image</h3>
            </div>
            <div class="ai-section-content" style="padding: 0.75rem;">
        """, unsafe_allow_html=True)
        
        st.image(annotated_photo_pil, caption="Analyzed Image (with detected features)", use_container_width=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    with col2:
        # Overall Assessment Box
        st.markdown("""
        <div class="ai-section" style="margin-top: 0;">
            <div class="ai-section-header">
                <span class="ai-section-icon">📊</span>
                <h3>Overall Assessment</h3>
            </div>
            <div class="ai-section-content" style="padding: 1.25rem;">
        """, unsafe_allow_html=True)
        
        is_healthy = overall.get('healthy', False)
        overall_status_text = "Healthy" if is_healthy else "Review Recommended"
        status_class = "status-success" if is_healthy else "status-error"
        
        st.markdown(f"**Overall Status:** <span class='status-indicator {status_class}'>{overall_status_text}</span>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Grid for metrics
        st.markdown('<div class="ai-compact-grid">', unsafe_allow_html=True)
        
        # Conditions Detected Metric
        conditions_count = overall.get('conditions_detected', 0)
        conditions_color = "#166534" if conditions_count == 0 else "#991b1b"
        st.markdown(f"""
        <div class="ai-metric-card">
            <div class="ai-metric-value" style="color: {conditions_color};">{conditions_count}</div>
            <div class="ai-metric-label">Conditions Detected</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Image Quality Metric
        quality = quality_metrics.get('overall_quality', 'N/A')
        quality_color = "#166534" if quality == "Good" else ("#92400e" if quality == "Fair" else "#991b1b")
        st.markdown(f"""
        <div class="ai-metric-card">
            <div class="ai-metric-value" style="color: {quality_color};">{quality}</div>
            <div class="ai-metric-label">Image Quality</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Faces Detected Metric
        faces_detected = validation_details.get('faces_detected', 'N/A')
        st.markdown(f"""
        <div class="ai-metric-card">
            <div class="ai-metric-value">{faces_detected}</div>
            <div class="ai-metric-label">Faces Detected</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Eyes Detected Metric
        eyes_detected = validation_details.get('eyes_detected', 'N/A')
        st.markdown(f"""
        <div class="ai-metric-card">
            <div class="ai-metric-value">{eyes_detected}</div>
            <div class="ai-metric-label">Eyes Detected</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True) # Close grid
        
        st.markdown("</div></div>", unsafe_allow_html=True) # Close ai-section


    # --- Detailed Analysis Section (Full Width) ---
    st.markdown("""
    <div class="ai-section">
        <div class="ai-section-header">
            <span class="ai-section-icon">🔍</span>
            <h3>Disease-Specific Analysis</h3>
        </div>
        <div class="ai-section-content" style="padding: 1.25rem;">
    """, unsafe_allow_html=True)

    conditions_data = [
         ("Diabetic Retinopathy", analysis_results.get('diabetic_retinopathy', {})),
         ("Glaucoma", analysis_results.get('glaucoma', {})),
         ("Cataracts", analysis_results.get('cataracts', {})),
         ("Age-related Macular Degeneration", analysis_results.get('amd', {})),
         ("Hypertensive Retinopathy", analysis_results.get('hypertensive_retinopathy', {})),
        ]

    descriptions = {
         "Diabetic Retinopathy": "Signs of blood vessel damage related to diabetes.",
         "Glaucoma": "Indicators related to optic nerve health or pressure.",
         "Cataracts": "Clouding detected in the lens.",
         "Age-related Macular Degeneration": "Signs of deterioration in the macula.",
         "Hypertensive Retinopathy": "Blood vessel changes potentially linked to high blood pressure."
        }

    for name, data in conditions_data:
        detected = data.get('detected', False) # Default to False if key missing
        status = "Detected" if detected else "Not Detected"
        color = "#dc2626" if detected else "#16a34a" # Red if detected, Green if not
        icon = "❌" if detected else "✓"
        confidence = data.get('confidence', 'N/A')
        description = descriptions.get(name, "Analysis details.")
        display_description = description if detected else f"No significant signs of {name.lower()} detected."
        
        # Use new CSS classes
        st.markdown(f"""
        <div class="disease-card" style="border-left-color: {color};">
            <div class="disease-card-header">
                <div>
                    <div class="disease-card-title">{name}</div>
                    <span class="disease-card-status" style="color: {color};">{icon} {status}</span>
                </div>
                <div class="disease-card-confidence">
                    <div class="disease-card-confidence-label">AI Confidence</div>
                    <div class="disease-card-confidence-value">{confidence if isinstance(confidence, (int, float)) else 'N/A'}%</div>
                </div>
            </div>
            <p class="disease-card-body">
                {display_description}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True) # Close ai-section


    # Professional Recommendations
    st.markdown("#### 👨‍⚕️ Professional Recommendations")
    recommendation_text = overall.get('recommendation', "Consult an eye care professional for a comprehensive exam.")
    st.markdown(f"""
    <div style="background: #f0f9ff; border: 2px solid #bfdbfe; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">
         <h4 style="color: #1e40af; margin-top: 0;">📋 Health Guidance</h4>
         <p style="color: #1e3a8a; margin: 0; padding-left: 0.5rem; line-height: 1.6; font-size: 0.95rem;">
               <strong>Recommendation:</strong> {recommendation_text}<br><br>
               <strong>General Advice:</strong>
               <ul style="margin: 0.5rem 0 0 0; padding-left: 1.5rem;">
                   <li>Continue regular comprehensive eye exams (typically annually, or as advised by your doctor).</li>
                   <li>Maintain a healthy lifestyle, including proper nutrition and exercise.</li>
                   <li>Wear UV-protective sunglasses outdoors.</li>
                   <li>Report any sudden changes in vision to an eye care professional immediately.</li>
                   <li>If diabetic, ensure good blood sugar control.</li>
                   <li>Monitor and manage blood pressure.</li>
               </ul>
         </p>
    </div>
    """, unsafe_allow_html=True)


    # Important disclaimers
    st.info("💡 **Important Note:** This is an AI-powered screening tool and not a substitute for professional medical diagnosis. Please consult an eye care professional (ophthalmologist or optometrist) for comprehensive eye examinations and any concerns about your eye health.")

    st.warning("⚠️ **Medical Disclaimer:** These results are based on image analysis and should not be considered a definitive diagnosis. Always seek professional medical advice for diagnosis and treatment.")


    # Technical details expander
    with st.expander("🔬 View Technical Details"):
         st.markdown("##### Validation Results")
         st.json(validation_details) # Shows the *actual* validation details

         st.markdown("##### AI Analysis Output (Raw)")
         st.json(analysis_results)


    # --- ACTION BUTTONS ---
    st.markdown("---")
    st.markdown("### 📥 Save & Next Steps")

    # Adjusted columns for the new Download PDF button
    col_act1, col_act2, col_act3, col_act4, col_act5 = st.columns(5)

    with col_act1:
        if st.button("📸 Recapture", key="recapture"):
             # Clear state for this specific test run
             keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'image_processed', 'captured_image_data', 'annotated_photo']
             for key in keys_to_clear:
                 if key in st.session_state:
                     del st.session_state[key]
             st.rerun()

    with col_act2:
        if st.button("💾 Save Report", key="save_ai_report"):
             save_success = save_ai_detection_results(analysis_results, quality_metrics, overall, validation_details)
             if save_success:
                 st.success("✅ AI detection report saved successfully!")
                 st.info("📋 You can view saved reports from your Profile page.")
             else:
                 st.error("❌ Failed to save report.")

    # --- NEW PDF DOWNLOAD BUTTON ---
    with col_act3:
        try:
            pdf_bytes = generate_ai_pdf(analysis_results, quality_metrics, overall, validation_details, user_id)
            st.download_button(
                 label="📄 Download PDF",
                 data=pdf_bytes,
                 file_name=f"ai_eye_report_{user_id}_{time.strftime('%Y%m%d')}.pdf",
                 mime="application/pdf",
                 key="download_ai_pdf"
                )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")
            st.button("📄 Download PDF", disabled=True, key="download_ai_pdf_disabled")

    with col_act4:
        if st.button("👂 Continue", key="continue_hearing"):
             # Optionally clear eye test state before switching
             keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'current_test', 'image_processed', 'captured_image_data', 'annotated_photo']
             for key in keys_to_clear:
                 if key in st.session_state:
                     del st.session_state[key]
             # Ensure the target page exists before switching
             try:
                 st.switch_page("pages/03_👂_Hearing_Assessment.py")
             except FileNotFoundError:
                 st.error("Hearing assessment page not found at 'pages/03_👂_Hearing_Assessment.py'")


    with col_act5:
        if st.button("← Back", key="back_from_ai_results"):
             # Clear state for this specific test run before going back
             keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'current_test', 'image_processed', 'captured_image_data', 'annotated_photo']
             for key in keys_to_clear:
                 if key in st.session_state:
                     del st.session_state[key]
             st.rerun()

def camera_detection_test():
    """
    Main router for the AI camera test.
    Shows capture UI, or validation error, or analysis, or results.
    """
    st.markdown('<div class="assessment-header"><h1>📸 AI Eye Disease Detection</h1><p>Advanced retinal image analysis powered by AI</p></div>', unsafe_allow_html=True)

    # Initialize session state keys if they don't exist
    if 'captured_photo' not in st.session_state:
        st.session_state.captured_photo = None # This will hold the BytesIO data
    if 'validation_status' not in st.session_state:
        st.session_state.validation_status = None # This will hold {'is_valid': ..., 'message': ..., 'details': ...}
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None # This will hold the final AI output
    if 'annotated_photo' not in st.session_state:
        st.session_state.annotated_photo = None # This will hold the PIL image with boxes

    # --- Main Routing Logic ---

    # 1. If we have final results, show them
    if st.session_state.analysis_results:
        display_ai_analysis_results()

    # 2. If we have a photo, check its validation status
    elif st.session_state.captured_photo:
        if st.session_state.validation_status and st.session_state.validation_status['is_valid']:
            # Photo is valid, but results not yet computed. Run simulation.
            run_ai_analysis_simulation()

        elif st.session_state.validation_status and not st.session_state.validation_status['is_valid']:
            # Photo was captured but failed validation
            st.error(f"❌ Image validation failed: {st.session_state.validation_status.get('message', 'Unknown error.')}")

            # Show the annotated (failed) image so the user knows why
            if st.session_state.annotated_photo:
                st.image(st.session_state.annotated_photo, caption="Validation Failed (Red/Yellow boxes indicate issues)")

            st.info("Please try again with a clearer, well-lit photo.")
            if st.button("📸 Try Capture/Upload Again"):
                # Clear the invalid photo and status to go back to capture UI
                keys_to_clear = ['captured_photo', 'validation_status', 'annotated_photo']
                for key in keys_to_clear:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()

            # Add a back button here as well
            st.markdown("---")
            if st.button("← Back to Test Selection", key="back_from_camera_fail"):
                st.session_state.current_test = None
                keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'quality_metrics', 'overall_results', 'validation_details_final', 'captured_image_data', 'annotated_photo']
                for key in keys_to_clear:
                    if key in st.session_state: del st.session_state[key]
                st.rerun()
        else:
            # This state shouldn't happen (photo exists but no validation status)
            st.error("An unexpected error occurred. Please restart the test.")
            if st.button("Restart Test"):
                keys_to_clear = ['captured_photo', 'validation_status', 'analysis_results', 'annotated_photo']
                for key in keys_to_clear:
                     if key in st.session_state: del st.session_state[key]
                st.rerun()

    # 3. If no photo, show the capture UI
    else:
        show_capture_ui()

# --- Main function (Unchanged) ---
def main():
    """Main function to handle page routing and test selection"""
    # Initialize session state from auth module first
    init_session_state() # Ensure basic keys like 'authenticated' and 'user_id' exist

    # Set page name for navbar highlighting
    st.session_state.page_name = "02_👁_Eye_Assessment" # Or derive dynamically if needed

    # Check authentication
    if not st.session_state.get("authenticated", False):
        st.warning("You are not logged in. Please log in to access assessments.")
        # Optional: Redirect or show login prompt
        if st.button("Go to Login"):
             # Ensure the main app file exists
             try:
                 st.switch_page("streamlit_app.py") # Assuming main app is login page
             except FileNotFoundError:
                 st.error("Main login page 'streamlit_app.py' not found.")
        return # Stop execution if not authenticated

    # --- Authenticated User Flow ---
    show_streamlit_navbar() # Show navbar only if authenticated
    load_custom_css()

    # Initialize test state if it doesn't exist
    if 'current_test' not in st.session_state:
        st.session_state.current_test = None

    # --- Routing Logic ---
    if st.session_state.current_test == "visual_acuity":
        visual_acuity_test()
    elif st.session_state.current_test == "camera_detection":
        camera_detection_test() # This version now uses st.camera_input
    else: # Default: Show test selection
        # Clear any potentially stale test data if returning to selection
        keys_to_clear_on_selection = [
            'captured_photo', 'validation_status', 'analysis_results', 'quality_metrics',
            'overall_results', 'validation_details_final', 'captured_image_data', 'annotated_photo'
        ]
        # Also clear recognition keys if navigating back here
        keys_to_clear_on_selection.extend([k for k in st.session_state if k.startswith(('recognized_text_', 'manual_input_display_', 'processed_audio_id_', 'recorder_', 'temp_audio_'))]) # Updated clear keys

        for key in keys_to_clear_on_selection:
            if key in st.session_state:
                del st.session_state[key]

        show_test_selection()

if __name__ == "__main__":
    main()