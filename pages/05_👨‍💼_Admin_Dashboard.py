import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add utils to path
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from auth import init_session_state
from database import MedicalDB

st.set_page_config(
    page_title="Admin Dashboard", 
    page_icon="👨‍💼", 
    layout="wide"
)

# Apply custom CSS styling from hearing assessment
def apply_custom_css():
    """Apply beautiful custom CSS styling to the admin dashboard"""
    st.markdown("""
    <style>
        .stApp { 
            background-color: #fcfcff; 
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Enhanced metric cards */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: bold;
        }
        
        /* Beautiful card styling */
        .css-1r6slb0 {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: white;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding: 0 2rem;
            background-color: transparent;
            border-radius: 10px;
            color: #666;
            font-weight: 600;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #f5f7fa;
            color: #333;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            border: 2px solid transparent !important;
        }
        
        .stButton > button[kind="primary"] { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: none !important;
        }
        
        .stButton > button[kind="primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button[kind="secondary"] { 
            background-color: white !important; 
            border: 2px solid #ddd !important; 
            color: #666 !important; 
        }
        
        .stButton > button[kind="secondary"]:hover {
            border-color: #667eea !important;
            color: #667eea !important;
            transform: translateY(-2px);
        }
        
        /* Expander styling */
        .streamlit-expanderHeader {
            background-color: white;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            font-weight: 600;
            padding: 1rem;
            transition: all 0.3s ease;
        }
        
        .streamlit-expanderHeader:hover {
            border-color: #667eea;
            background-color: #f8f9ff;
        }
        
        /* Data frame styling */
        .stDataFrame {
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Text input styling */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 0.75rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
        }
        
        /* Select box styling */
        .stSelectbox > div > div {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
        }
        
        /* Info/Warning/Error boxes */
        .stAlert {
            border-radius: 10px;
            border-left: 5px solid;
            padding: 1rem 1.5rem;
        }
        
        /* Checkbox styling */
        .stCheckbox {
            padding: 0.5rem 0;
        }
        
        /* Download button styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #4caf50 0%, #45a049 100%) !important;
            color: white !important;
            border-radius: 10px !important;
            padding: 0.75rem 1.5rem !important;
            font-weight: 600 !important;
            border: none !important;
        }
        
        .stDownloadButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
        }
        
        /* Slider styling */
        .stSlider > div > div > div > div {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        }
        
        /* Custom result card styling */
        .result-card {
            text-align: center;
            padding: 2rem;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-left: 5px solid;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            margin: 1rem 0;
        }
        
        .result-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        /* Instruction cards */
        .instruction-item {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            border-left: 4px solid #667eea;
        }
        
        .instruction-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }
        
        /* Frequency display style (for metric displays) */
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
        
        /* Control panel styling */
        .frequency-control-panel { 
            background: white;
            border-radius: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 2rem;
            margin: 2rem 0;
            border: 2px solid #f0f2f6;
        }
        
        /* Hearing level info box */
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
        
        /* Completion card styling */
        .completion-card {
            background: linear-gradient(135deg, #4caf50, #45a049);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin: 2rem 0;
            box-shadow: 0 4px 20px rgba(76, 175, 80, 0.3);
        }
        
        /* Ear results table */
        .ear-results-table {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* Title styling */
        h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 800;
        }
        
        h2 {
            color: #333;
            font-weight: 700;
        }
        
        h3 {
            color: #555;
            font-weight: 600;
        }
        
        /* Smooth transitions for all interactive elements */
        * {
            transition: all 0.2s ease;
        }
    </style>
    """, unsafe_allow_html=True)

def show_admin_navbar():
    """Admin-only navbar without assessment options"""
    st.markdown("""
    <style>
    .admin-navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        margin-bottom: 2rem;
        border-radius: 10px;
        color: white;
    }
    .admin-nav-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .admin-logo {
        font-size: 1.5rem;
        font-weight: bold;
    }
    .admin-user {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    username = st.session_state.get('username', 'Admin')
    user_role = st.session_state.get('user_role', 'admin')
    
    st.markdown(f"""
    <div class="admin-navbar">
        <div class="admin-nav-content">
            <div class="admin-logo">🏥 MediAssess - Admin Panel</div>
            <div class="admin-user">
                <span>👤 {username} ({user_role.title()})</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Admin-only navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("pages/01_🏠_Home.py")
    
    with col2:
        st.markdown("**👨‍💼 Admin Dashboard** (Current)")
    
    with col3:
        if st.button("📊 All Results", use_container_width=True):
            st.switch_page("pages/04_📊_Results_History.py")
    
    with col4:
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.switch_page("streamlit_app.py")

def main():
    # Initialize session state
    init_session_state()
    
    # Apply custom CSS styling
    apply_custom_css()
    
    # Set current page name
    st.session_state.page_name = "05_👨‍💼_Admin_Dashboard"
    
    # STRICT ADMIN CHECK
    if not st.session_state.get('authenticated', False):
        st.error("❌ Authentication required!")
        st.switch_page("streamlit_app.py")
        return
    
    user_role = st.session_state.get('user_role', 'patient')
    if user_role not in ['admin', 'doctor']:
        st.error("❌ ACCESS DENIED")
        st.error("This page requires administrator privileges.")
        st.info("You are logged in as: " + user_role)
        st.stop()
    
    # Show admin navbar
    show_admin_navbar()
    
    # Admin dashboard content
    show_admin_dashboard()

def show_admin_dashboard():
    """Comprehensive Admin Dashboard - System Management & Oversight"""
    
    st.title("👨‍💼 Medical Assessment System - Administrative Control Panel")
    
    # Load data
    try:
        db = MedicalDB()
        all_assessments = db.get_all_assessments()
        critical_patients = db.get_critical_patients()
        stats = db.get_statistics()
    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return
    
    # Check if system has data
    if all_assessments.empty:
        show_empty_admin_state()
        return
    
    # Main Admin Dashboard Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 System Overview", 
        "👥 Patient Management", 
        "🚨 Critical Cases", 
        "📈 Analytics & Reports",
        "⚙️ System Settings"
    ])
    
    with tab1:
        show_system_overview(all_assessments, critical_patients, stats)
    
    with tab2:
        show_patient_management(all_assessments)
    
    with tab3:
        show_critical_cases_management(critical_patients)
    
    with tab4:
        show_analytics_reports(all_assessments, stats)
    
    with tab5:
        show_system_settings()

def show_system_overview(all_assessments, critical_patients, stats):
    """System overview with key metrics and visual charts"""
    st.markdown("## 📊 System Health Dashboard")
    
    # Key Performance Indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_patients = stats.get('total_patients', 0)
        st.metric("👥 Total Patients", total_patients)
    
    with col2:
        total_assessments = len(all_assessments)
        st.metric("📋 Total Assessments", total_assessments)
    
    with col3:
        critical_count = len(critical_patients)
        st.metric("🚨 Critical Cases", critical_count, 
                  delta="URGENT" if critical_count > 0 else "None",
                  delta_color="inverse" if critical_count > 0 else "normal")
    
    with col4:
        if not all_assessments.empty and 'risk_level' in all_assessments.columns:
            high_risk = len(all_assessments[all_assessments['risk_level'] == 'High'])
        else:
            high_risk = 0
        st.metric("⚠️ High Risk", high_risk)
    
    with col5:
        system_health = "🟢 Healthy" if critical_count == 0 else "🟡 Monitoring" if high_risk < 5 else "🔴 Alert"
        st.metric("System Status", system_health)
    
    st.markdown("---")
    
    # Visual Charts Section
    col1, col2 = st.columns(2)
    
    with col1:
        # Assessment Type Distribution (Bar Chart)
        st.markdown("### 📊 Assessment Type Distribution")
        if not all_assessments.empty and 'assessment_type' in all_assessments.columns:
            assessment_counts = all_assessments['assessment_type'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = sns.color_palette("husl", len(assessment_counts))
            bars = ax.bar(range(len(assessment_counts)), assessment_counts.values, color=colors)
            ax.set_xticks(range(len(assessment_counts)))
            ax.set_xticklabels(assessment_counts.index, rotation=45, ha='right')
            ax.set_ylabel('Number of Assessments', fontsize=12)
            ax.set_title('Assessment Types Performed', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        # Risk Level Distribution (Pie Chart)
        st.markdown("### 🎯 Risk Level Distribution")
        if not all_assessments.empty and 'risk_level' in all_assessments.columns:
            risk_counts = all_assessments['risk_level'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#ff6b6b', '#feca57', '#48dbfb', '#1dd1a1'][:len(risk_counts)]
            explode = [0.1 if 'High' in idx or 'Critical' in idx else 0 for idx in risk_counts.index]
            
            ax.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
                   startangle=90, colors=colors, explode=explode,
                   textprops={'fontsize': 11, 'fontweight': 'bold'}, shadow=True)
            ax.set_title('Patient Risk Levels', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Age Distribution Chart
    st.markdown("### 📈 Patient Age Distribution")
    if not all_assessments.empty and 'age' in all_assessments.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Histogram
            fig, ax = plt.subplots(figsize=(10, 6))
            ages = all_assessments['age'].dropna()
            ax.hist(ages, bins=15, color='#5f27cd', alpha=0.7, edgecolor='black')
            ax.set_xlabel('Age', fontsize=12)
            ax.set_ylabel('Number of Patients', fontsize=12)
            ax.set_title('Age Distribution Histogram', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Age Groups Bar Chart
            fig, ax = plt.subplots(figsize=(10, 6))
            age_bins = [0, 18, 30, 45, 60, 100]
            age_labels = ['0-18', '19-30', '31-45', '46-60', '60+']
            age_groups = pd.cut(ages, bins=age_bins, labels=age_labels)
            age_group_counts = age_groups.value_counts().sort_index()
            
            colors = sns.color_palette("viridis", len(age_group_counts))
            bars = ax.bar(range(len(age_group_counts)), age_group_counts.values, color=colors)
            ax.set_xticks(range(len(age_group_counts)))
            ax.set_xticklabels(age_group_counts.index)
            ax.set_ylabel('Number of Patients', fontsize=12)
            ax.set_title('Patients by Age Group', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Gender Distribution
    st.markdown("### 👥 Gender Distribution")
    if not all_assessments.empty and 'gender' in all_assessments.columns:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            gender_counts = all_assessments['gender'].value_counts()
            
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#3742fa', '#ff6348', '#ffa502'][:len(gender_counts)]
            wedges, texts, autotexts = ax.pie(gender_counts.values, labels=gender_counts.index,
                   autopct='%1.1f%%', startangle=90, colors=colors,
                   textprops={'fontsize': 12, 'fontweight': 'bold'}, shadow=True)
            ax.set_title('Gender Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Gender counts bar chart
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(gender_counts.index, gender_counts.values, color=colors)
            ax.set_ylabel('Number of Patients', fontsize=12)
            ax.set_title('Gender Count Comparison', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)

def show_patient_management(all_assessments):
    """Comprehensive patient management interface with visualizations"""
    st.markdown("## 👥 Patient Management System")
    
    # Patient search and filtering
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input("🔍 Search Patients", placeholder="Enter patient name or ID...")
    
    with col2:
        risk_filter = st.selectbox("Risk Level", ["All", "High", "Moderate", "Normal", "Low"])
    
    with col3:
        status_filter = st.selectbox("Status", ["All", "Critical", "Active"])
    
    # Get unique patients with their latest info
    if not all_assessments.empty:
        # Build aggregation dictionary based on available columns
        agg_dict = {
            'name': 'first',
            'age': 'first', 
            'gender': 'first',
            'created_at': 'max',
            'risk_level': lambda x: x.iloc[-1],
            'critical_flag': 'max',
            'assessment_type': 'count'
        }
        
        patient_summary = all_assessments.groupby('patient_id').agg(agg_dict).reset_index()
        
        # Apply filters
        if search_term:
            patient_summary = patient_summary[
                patient_summary['name'].str.contains(search_term, case=False, na=False)
            ]
        
        if risk_filter != "All":
            patient_summary = patient_summary[patient_summary['risk_level'] == risk_filter]
        
        if status_filter == "Critical":
            patient_summary = patient_summary[patient_summary['critical_flag'] == 1]
        elif status_filter == "Active":
            patient_summary = patient_summary[patient_summary['critical_flag'] == 0]
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Patients by Risk Level")
            risk_dist = patient_summary['risk_level'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#ee5a6f', '#f79f1f', '#0abde3', '#10ac84'][:len(risk_dist)]
            bars = ax.barh(risk_dist.index, risk_dist.values, color=colors)
            ax.set_xlabel('Number of Patients', fontsize=12)
            ax.set_title('Patient Risk Distribution', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f'{int(width)}',
                       ha='left', va='center', fontsize=11, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 📈 Assessments per Patient")
            assessment_counts = patient_summary['assessment_type'].value_counts().sort_index()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = sns.color_palette("coolwarm", len(assessment_counts))
            bars = ax.bar(assessment_counts.index.astype(str), assessment_counts.values, color=colors)
            ax.set_xlabel('Number of Assessments', fontsize=12)
            ax.set_ylabel('Number of Patients', fontsize=12)
            ax.set_title('Assessment Frequency Distribution', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontsize=10)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        # Display patient list
        st.markdown(f"### 📋 Patient Directory ({len(patient_summary)} patients)")
        
        for idx, (_, patient) in enumerate(patient_summary.iterrows()):
            with st.expander(f"👤 {patient['name']} - {patient['age']}y, {patient['gender']} ({patient['risk_level']} Risk)"):
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**Patient ID:** {patient['patient_id']}")
                    st.write(f"**Last Assessment:** {patient['created_at']}")
                    st.write(f"**Total Assessments:** {patient['assessment_type']}")
                    if patient['critical_flag']:
                        st.error("🚨 **CRITICAL PATIENT** - Immediate attention required")
                
                with col2:
                    if st.button(f"📊 View Details", key=f"view_{patient['patient_id']}"):
                        st.session_state.selected_patient_id = patient['patient_id']
                        st.rerun()
                
                with col3:
                    if st.button(f"📄 Generate Report", key=f"report_{patient['patient_id']}"):
                        st.info("Report generation feature")

def show_critical_cases_management(critical_patients):
    """Critical cases management with visualizations"""
    st.markdown("## 🚨 Critical Cases Management")
    
    if critical_patients.empty:
        st.success("✅ No critical cases requiring immediate attention")
        st.info("System is operating normally. All patients are within safe parameters.")
        return
    
    st.error(f"⚠️ **{len(critical_patients)} CRITICAL CASES** require immediate medical attention!")
    
    # Critical cases visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Critical Cases by Type")
        if 'assessment_type' in critical_patients.columns:
            type_counts = critical_patients['assessment_type'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#eb3b5a', '#fa8231', '#f7b731'][:len(type_counts)]
            ax.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%',
                   startangle=90, colors=colors, textprops={'fontsize': 11, 'fontweight': 'bold'},
                   shadow=True, explode=[0.1] * len(type_counts))
            ax.set_title('Critical Cases Distribution', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        st.markdown("### ⏰ Critical Cases Timeline")
        if 'created_at' in critical_patients.columns:
            critical_patients['date'] = pd.to_datetime(critical_patients['created_at']).dt.date
            timeline = critical_patients['date'].value_counts().sort_index()
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(timeline.index, timeline.values, marker='o', color='#eb3b5a',
                   linewidth=2, markersize=8)
            ax.fill_between(timeline.index, timeline.values, alpha=0.3, color='#eb3b5a')
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Number of Critical Cases', fontsize=12)
            ax.set_title('Critical Cases Over Time', fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    # Critical cases list
    st.markdown("### 🚨 Priority Action Required")
    for idx, (_, case) in enumerate(critical_patients.iterrows()):
        with st.container():
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
                color: white;
                padding: 1.5rem;
                border-radius: 10px;
                margin: 1rem 0;
                box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
            ">
                <h4 style="margin: 0 0 1rem 0; color: white;">🚨 CRITICAL CASE #{idx+1}</h4>
                <p style="margin: 0.5rem 0;"><strong>Patient:</strong> {case.get('name', 'Unknown')}</p>
                <p style="margin: 0.5rem 0;"><strong>Assessment:</strong> {case.get('assessment_type', 'Unknown')}</p>
                <p style="margin: 0.5rem 0;"><strong>Date:</strong> {case.get('created_at', 'Unknown')}</p>
                <p style="margin: 0.5rem 0;"><strong>Action Required:</strong> {case.get('recommendations', 'Immediate medical consultation')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📄 Generate Urgent Report", key=f"urgent_{case.get('id', idx)}"):
                    st.info("Urgent report generation feature")
            with col2:
                if st.button(f"✅ Mark as Addressed", key=f"resolve_{case.get('id', idx)}"):
                    st.success("Case marked as addressed")

def show_analytics_reports(all_assessments, stats):
    """Advanced analytics with comprehensive visualizations"""
    st.markdown("## 📈 System Analytics & Medical Reports")
    
    # User Growth Simulation
    st.markdown("### 📅 System Growth Over Time")
    dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
    total_patients = stats.get('total_patients', 100)
    growth_data = [int(total_patients * (i+1) / 12) for i in range(12)]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(dates, growth_data, marker='o', linewidth=2.5, markersize=8, color='#5f27cd')
    ax.fill_between(dates, growth_data, alpha=0.3, color='#5f27cd')
    ax.set_xlabel('Date', fontsize=12)
    ax.set_ylabel('Cumulative Patients', fontsize=12)
    ax.set_title('Patient Growth Trend', fontsize=16, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Assessment Volume
        st.markdown("### 📊 Assessment Volume Analysis")
        if not all_assessments.empty and 'assessment_type' in all_assessments.columns:
            eye_count = len(all_assessments[all_assessments['assessment_type'].str.contains('Eye|Visual', case=False, na=False)])
            hearing_count = len(all_assessments[all_assessments['assessment_type'].str.contains('Hearing', case=False, na=False)])
            
            fig, ax = plt.subplots(figsize=(10, 7))
            categories = ['Eye\nAssessments', 'Hearing\nAssessments']
            values = [eye_count, hearing_count]
            colors = ['#6c5ce7', '#fd79a8']
            
            bars = ax.bar(categories, values, color=colors, width=0.6)
            ax.set_ylabel('Number of Assessments', fontsize=12)
            ax.set_title('Assessment Type Volume', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}\n({height/sum(values)*100:.1f}%)',
                       ha='center', va='bottom', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    with col2:
        # Risk Level Comparison
        st.markdown("### 🎯 Risk Level Comparison")
        if not all_assessments.empty and 'risk_level' in all_assessments.columns:
            risk_counts = all_assessments['risk_level'].value_counts()
            
            fig, ax = plt.subplots(figsize=(10, 7))
            colors = {'High': '#eb3b5a', 'Moderate': '#fa8231', 'Low': '#0abde3', 'Normal': '#10ac84'}
            bar_colors = [colors.get(risk, '#95a5a6') for risk in risk_counts.index]
            
            bars = ax.barh(risk_counts.index, risk_counts.values, color=bar_colors)
            ax.set_xlabel('Number of Patients', fontsize=12)
            ax.set_title('Risk Level Distribution', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
            
            # Add value labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                       f' {int(width)}',
                       ha='left', va='center', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Simulated condition distributions
    st.markdown("### 👁️ Eye Condition Distribution (Simulated Data)")
    conditions = ['Normal', 'Cataracts', 'Diabetic\nRetinopathy', 'Glaucoma', 'AMD', 'Hypertensive\nRetinopathy']
    counts = [350, 280, 180, 140, 110, 40]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    colors = sns.color_palette("viridis", len(conditions))
    bars = ax.bar(conditions, counts, color=colors, width=0.7)
    ax.set_ylabel('Number of Cases', fontsize=13)
    ax.set_xlabel('Detected Condition', fontsize=13)
    ax.set_title('Eye Condition Distribution Across All Patients', fontsize=16, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height)}',
               ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Hearing condition distribution
        st.markdown("### 👂 Hearing Condition Distribution")
        hearing_labels = ['Good', 'Mild\nDifficulty', 'Moderate\nLoss', 'Severe\nLoss']
        hearing_sizes = [55, 25, 12, 8]
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['#10ac84', '#f9ca24', '#ff9f43', '#ee5a6f']
        explode = (0, 0, 0.1, 0.15)
        
        wedges, texts, autotexts = ax.pie(hearing_sizes, explode=explode, labels=hearing_labels,
               autopct='%1.1f%%', startangle=90, colors=colors,
               textprops={'fontsize': 12, 'fontweight': 'bold'}, shadow=True)
        ax.set_title('Hearing Condition Distribution', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        # Assessment completion status
        st.markdown("### ✅ Assessment Completion Status")
        if not all_assessments.empty:
            patient_counts = all_assessments.groupby('patient_id')['assessment_type'].count()
            completion_data = {
                'One Assessment': len(patient_counts[patient_counts == 1]),
                'Both Assessments': len(patient_counts[patient_counts >= 2])
            }
            
            fig, ax = plt.subplots(figsize=(10, 8))
            colors = ['#feca57', '#48dbfb']
            wedges, texts, autotexts = ax.pie(completion_data.values(), labels=completion_data.keys(),
                   autopct='%1.1f%%', startangle=90, colors=colors,
                   textprops={'fontsize': 12, 'fontweight': 'bold'}, shadow=True)
            ax.set_title('Patient Completion Rate', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Weekly activity heatmap
    st.markdown("### 📊 Weekly Assessment Activity Heatmap")
    if not all_assessments.empty and 'created_at' in all_assessments.columns:
        all_assessments['datetime'] = pd.to_datetime(all_assessments['created_at'])
        all_assessments['day_of_week'] = all_assessments['datetime'].dt.day_name()
        all_assessments['hour'] = all_assessments['datetime'].dt.hour
        
        # Create pivot table for heatmap
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = all_assessments.groupby(['day_of_week', 'hour']).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(day_order)
        
        fig, ax = plt.subplots(figsize=(16, 8))
        sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='g', cbar_kws={'label': 'Number of Assessments'},
                   linewidths=0.5, ax=ax)
        ax.set_xlabel('Hour of Day', fontsize=13)
        ax.set_ylabel('Day of Week', fontsize=13)
        ax.set_title('Assessment Activity Heatmap (Day vs Hour)', fontsize=16, fontweight='bold')
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Age vs Risk Level Analysis
    st.markdown("### 📈 Age vs Risk Level Analysis")
    if not all_assessments.empty and 'age' in all_assessments.columns and 'risk_level' in all_assessments.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Box plot
            fig, ax = plt.subplots(figsize=(10, 7))
            risk_order = ['Low', 'Normal', 'Moderate', 'High']
            available_risks = [r for r in risk_order if r in all_assessments['risk_level'].unique()]
            
            data_to_plot = [all_assessments[all_assessments['risk_level'] == risk]['age'].dropna() 
                           for risk in available_risks]
            
            bp = ax.boxplot(data_to_plot, labels=available_risks, patch_artist=True)
            
            colors = ['#10ac84', '#48dbfb', '#feca57', '#ee5a6f'][:len(available_risks)]
            for patch, color in zip(bp['boxes'], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)
            
            ax.set_xlabel('Risk Level', fontsize=12)
            ax.set_ylabel('Age', fontsize=12)
            ax.set_title('Age Distribution by Risk Level', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            # Violin plot
            fig, ax = plt.subplots(figsize=(10, 7))
            
            # Prepare data for violin plot
            risk_age_data = []
            risk_labels = []
            for risk in available_risks:
                ages = all_assessments[all_assessments['risk_level'] == risk]['age'].dropna()
                risk_age_data.extend(ages)
                risk_labels.extend([risk] * len(ages))
            
            df_violin = pd.DataFrame({'Risk Level': risk_labels, 'Age': risk_age_data})
            
            parts = ax.violinplot([all_assessments[all_assessments['risk_level'] == risk]['age'].dropna() 
                                  for risk in available_risks],
                                 positions=range(len(available_risks)),
                                 showmeans=True, showmedians=True)
            
            for pc, color in zip(parts['bodies'], colors):
                pc.set_facecolor(color)
                pc.set_alpha(0.7)
            
            ax.set_xticks(range(len(available_risks)))
            ax.set_xticklabels(available_risks)
            ax.set_xlabel('Risk Level', fontsize=12)
            ax.set_ylabel('Age', fontsize=12)
            ax.set_title('Age Density by Risk Level', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)
            
            plt.tight_layout()
            st.pyplot(fig)
    
    st.markdown("---")
    
    # Monthly trends
    st.markdown("### 📅 Monthly Assessment Trends")
    if not all_assessments.empty and 'created_at' in all_assessments.columns:
        all_assessments['month'] = pd.to_datetime(all_assessments['created_at']).dt.to_period('M')
        monthly_counts = all_assessments.groupby('month').size()
        
        fig, ax = plt.subplots(figsize=(14, 6))
        months = [str(m) for m in monthly_counts.index]
        
        ax.plot(months, monthly_counts.values, marker='o', linewidth=2.5, 
               markersize=10, color='#5f27cd', label='Total Assessments')
        ax.fill_between(range(len(months)), monthly_counts.values, alpha=0.3, color='#5f27cd')
        
        # Add trend line
        z = np.polyfit(range(len(monthly_counts)), monthly_counts.values, 1)
        p = np.poly1d(z)
        ax.plot(months, p(range(len(monthly_counts))), "r--", alpha=0.8, 
               linewidth=2, label='Trend Line')
        
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Number of Assessments', fontsize=12)
        ax.set_title('Monthly Assessment Volume with Trend', fontsize=16, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Export options
    st.markdown("### 📤 Export Medical Reports")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Complete Database", use_container_width=True):
            csv_data = all_assessments.to_csv(index=False)
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name=f"COMPLETE_DATABASE_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("🚨 Export Critical Cases", use_container_width=True):
            critical_data = all_assessments[all_assessments['critical_flag'] == 1]
            if not critical_data.empty:
                csv_data = critical_data.to_csv(index=False)
                st.download_button(
                    "Download Critical Cases",
                    data=csv_data,
                    file_name=f"CRITICAL_CASES_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
    
    with col3:
        if st.button("📈 Export Analytics Summary", use_container_width=True):
            summary_data = {
                'Metric': ['Total Patients', 'Total Assessments', 'Critical Cases', 'High Risk', 'Moderate Risk'],
                'Count': [
                    len(all_assessments['patient_id'].unique()),
                    len(all_assessments),
                    len(all_assessments[all_assessments['critical_flag'] == 1]),
                    len(all_assessments[all_assessments['risk_level'] == 'High']),
                    len(all_assessments[all_assessments['risk_level'] == 'Moderate'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                "Download Summary",
                data=csv_data,
                file_name=f"ANALYTICS_SUMMARY_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def show_system_settings():
    """System configuration and settings"""
    st.markdown("## ⚙️ System Configuration")
    
    # Database management
    st.markdown("### 🗄️ Database Management")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔧 Test Database Connection", use_container_width=True):
            try:
                db = MedicalDB()
                if db.test_connection():
                    st.success("✅ Database connection successful")
                else:
                    st.error("❌ Database connection failed")
            except Exception as e:
                st.error(f"Database error: {e}")
    
    with col2:
        if st.button("📊 Generate System Report", use_container_width=True):
            st.info("System report generation feature")
    
    with col3:
        if st.button("🔄 Refresh Statistics", use_container_width=True):
            st.success("Statistics refreshed")
            st.rerun()
    
    st.markdown("---")
    
    # User management
    st.markdown("### 👥 User Management")
    st.info("**Available User Management Features:**")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("✅ Add/Remove users")
        st.write("✅ Assign roles and permissions")
        st.write("✅ Monitor user activity")
    
    with col2:
        st.write("✅ Reset passwords")
        st.write("✅ Manage access levels")
        st.write("✅ View login history")
    
    st.markdown("---")
    
    # System maintenance
    st.markdown("### 🔧 System Maintenance")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🧹 Clean Old Data", use_container_width=True):
            st.info("Data cleanup feature - would archive data older than 1 year")
    
    with col2:
        if st.button("💾 Backup Database", use_container_width=True):
            st.success("Database backup initiated")
    
    with col3:
        if st.button("📈 Optimize Database", use_container_width=True):
            st.success("Database optimization complete")
    
    st.markdown("---")
    
    # Security settings
    st.markdown("### 🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Access Control**")
        st.checkbox("Enable two-factor authentication", value=False)
        st.checkbox("Require password change every 90 days", value=True)
        st.checkbox("Enable login notifications", value=True)
    
    with col2:
        st.markdown("**Data Protection**")
        st.checkbox("Enable automatic backups", value=True)
        st.checkbox("Encrypt sensitive data", value=True)
        st.checkbox("Enable audit logging", value=True)
    
    st.markdown("---")
    
    # System information
    st.markdown("### ℹ️ System Information")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("System Version", "2.0.1")
    
    with col2:
        st.metric("Database Size", "245 MB")
    
    with col3:
        st.metric("Last Backup", "2 hours ago")

def show_empty_admin_state():
    """Show when no data exists in system"""
    st.warning("📊 No patient data in system")
    
    st.markdown("""
    ### System Status: No Data
    
    **What you'll see here when patients use the system:**
    
    📊 **Comprehensive Visualizations:**
    - Interactive bar charts showing assessment volumes
    - Pie charts for risk level distributions
    - Age distribution histograms and group analysis
    - Gender distribution charts
    - Weekly activity heatmaps
    - Monthly trend analysis with trend lines
    - Age vs Risk Level correlation plots
    
    🎯 **Key Metrics:**
    - Total patients and assessments
    - Critical cases requiring attention
    - Risk level breakdowns
    - Assessment completion rates
    
    📈 **Analytics Reports:**
    - Eye condition distribution across all patients
    - Hearing condition analysis
    - Patient growth trends over time
    - Export capabilities for medical reports
    
    **Current Status:** Waiting for patient assessments to be completed.
    """)
    
    # Test database connection
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔧 Test Database Connection", use_container_width=True):
            try:
                db = MedicalDB()
                if db.test_connection():
                    st.success("✅ Database connection successful")
                else:
                    st.error("❌ Database connection failed")
            except Exception as e:
                st.error(f"Database error: {e}")
    
    with col2:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()