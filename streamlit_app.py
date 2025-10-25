import streamlit as st
import sqlite3
from pathlib import Path
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add utils to path
sys.path.append(str(Path(__file__).parent / "utils"))

# FIXED IMPORT - Use utils.auth instead of just auth
from utils.auth import init_session_state, show_login_signup, show_user_profile, is_admin_authenticated, get_current_user, logout

# Page config
st.set_page_config(
    page_title="Medical Assessment Platform",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    # Initialize session state
    init_session_state()
    
    # Authentication check
    if not st.session_state.get('authenticated', False):
        # Show login page
        show_login_signup()
    else:
        # Check if user just logged in - redirect based on role
        if st.session_state.get('just_logged_in', False):
            # Clear the redirect flag
            st.session_state['just_logged_in'] = False
            user_role = st.session_state.get('user_role', 'patient')
            
            # Redirect based on user role
            if user_role in ['admin', 'doctor']:
                st.switch_page("pages/05_👨‍💼_Admin_Dashboard.py")
            else:
                st.switch_page("pages/01_🏠_Home.py")
        
        # If user somehow bypasses the redirect (shouldn't normally happen)
        st.title("🏥 Medical Assessment Platform")
        st.success(f"Welcome, {st.session_state.get('username', 'User')}!")
        
        # Show user info
        user_role = st.session_state.get('user_role', '')
        if is_admin_authenticated():
            user = get_current_user()
            st.info(f"👨‍💼 {user.get('role', 'Admin').title()}: {user.get('full_name', 'User')}")
        else:
            st.info(f"👤 Patient: {st.session_state.get('username', 'User')}")
        
        st.markdown("---")
        st.markdown("### Navigate to your desired section:")
        
        # Navigation buttons based on your page structure
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🏠 Home", type="primary", use_container_width=True):
                st.switch_page("pages/01_🏠_Home.py")  # Adjust path as needed
            
            if st.button("👁️ Eye Assessment", use_container_width=True):
                st.switch_page("pages/02_👁️_Eye_Assessment.py")  # Adjust path as needed
            
            if st.button("📋 Results History", use_container_width=True):
                st.switch_page("pages/04_📋_Results_History.py")  # Adjust path as needed
        
        with col2:
            if st.button("👂 Hearing Assessment", use_container_width=True):
                st.switch_page("pages/03_🔊_Hearing_Assessment.py")  # Adjust path as needed
            
            # Show admin dashboard button if user is admin/doctor
            if is_admin_authenticated() or st.session_state.get('user_role') in ['admin', 'doctor']:
                if st.button("👨‍💼 Admin Dashboard", use_container_width=True):
                    st.switch_page("pages/05_👨‍💼_Admin_Dashboard.py")  # Adjust path as needed
            
            if st.button("🚪 Logout", type="secondary", use_container_width=True):
                logout()
                st.rerun()
        
        st.markdown("---")
        st.info("💡 **Tip:** Use the sidebar navigation to move between different sections of the platform.")


if __name__ == "__main__":
    main()
