import streamlit as st
from pathlib import Path

def load_navbar_css():
    """Load custom CSS for the navbar"""
    st.markdown("""
    <style>
    /* Navbar container */
    .navbar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 9999;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 0.75rem 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
        animation: slideDown 0.5s ease-out;
    }
    
    /* Navbar content */
    .navbar-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* Logo section */
    .navbar-logo {
        display: flex;
        align-items: center;
        color: white;
        font-size: 1.5rem;
        font-weight: bold;
        text-decoration: none;
        transition: all 0.3s ease;
    }
    
    .navbar-logo:hover {
        transform: scale(1.05);
        text-shadow: 0 0 10px rgba(255,255,255,0.3);
    }
    
    /* Navigation links */
    .navbar-nav {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .nav-item {
        position: relative;
        padding: 0.5rem 1rem;
        color: white;
        text-decoration: none;
        border-radius: 25px;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 2px solid transparent;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    
    .nav-item:hover {
        background: rgba(255,255,255,0.2);
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255,255,255,0.2);
        border-color: rgba(255,255,255,0.3);
    }
    
    .nav-item.active {
        background: rgba(255,255,255,0.3);
        border-color: rgba(255,255,255,0.5);
        font-weight: bold;
    }
    
    /* Back button */
    .back-button {
        background: rgba(255,255,255,0.15);
        border: 2px solid rgba(255,255,255,0.3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .back-button:hover {
        background: rgba(255,255,255,0.25);
        transform: translateX(-3px);
        border-color: rgba(255,255,255,0.5);
    }
    
    /* User info section */
    .navbar-user {
        display: flex;
        align-items: center;
        gap: 1rem;
        color: white;
    }
    
    .user-avatar {
        width: 35px;
        height: 35px;
        border-radius: 50%;
        background: rgba(255,255,255,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        transition: all 0.3s ease;
    }
    
    .user-avatar:hover {
        background: rgba(255,255,255,0.3);
        transform: scale(1.1);
    }
    
    /* Dropdown menu */
    .dropdown {
        position: relative;
    }
    
    .dropdown-content {
        display: none;
        position: absolute;
        right: 0;
        top: 100%;
        background: white;
        min-width: 200px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-radius: 10px;
        padding: 0.5rem 0;
        margin-top: 0.5rem;
        z-index: 1000;
        animation: fadeInDown 0.3s ease-out;
    }
    
    .dropdown:hover .dropdown-content {
        display: block;
    }
    
    .dropdown-item {
        padding: 0.75rem 1rem;
        color: #333;
        text-decoration: none;
        display: block;
        transition: all 0.2s ease;
    }
    
    .dropdown-item:hover {
        background: #f8f9ff;
        color: #667eea;
        padding-left: 1.5rem;
    }
    
    /* Animations */
    @keyframes slideDown {
        from {
            transform: translateY(-100%);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Mobile responsiveness */
    @media (max-width: 768px) {
        .navbar {
            padding: 0.5rem 1rem;
        }
        
        .navbar-nav {
            gap: 0.5rem;
        }
        
        .nav-item {
            padding: 0.4rem 0.8rem;
            font-size: 0.9rem;
        }
        
        .navbar-user {
            gap: 0.5rem;
        }
    }
    
    /* Main content padding to account for fixed navbar */
    .main .block-container {
        padding-top: 5rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

def get_current_page():
    """Get the current page name from the URL"""
    try:
        # Get the current page from Streamlit's session state
        if hasattr(st, 'session_state') and hasattr(st.session_state, 'page_name'):
            return st.session_state.page_name
        
        # Fallback: try to get from the file path
        import inspect
        frame = inspect.currentframe()
        if frame and frame.f_back and frame.f_back.f_code:
            filename = frame.f_back.f_code.co_filename
            page_name = Path(filename).stem
            return page_name
        
        return "Home"
    except:
        return "Home"

def get_previous_page(current_page):
    """Get the logical previous page based on navigation flow"""
    page_hierarchy = {
        "streamlit_app": None,  # Login page has no previous
        "01_🏠_Home": "streamlit_app",
        "02_👁️_Eye_Assessment": "01_🏠_Home",
        "03_👂_Hearing_Assessment": "01_🏠_Home",
        "04_📊_Results_History": "01_🏠_Home",  # Fixed: Updated emoji to match your file
        "05_👨‍💼_Admin_Dashboard": "01_🏠_Home",
        "06_👤_Profile": "01_🏠_Home"
    }
    
    return page_hierarchy.get(current_page, "01_🏠_Home")

def get_page_display_name(page_name):
    """Convert page filename to display name"""
    display_names = {
        "streamlit_app": "Login",
        "01_🏠_Home": "Home",
        "02_👁️_Eye_Assessment": "Eye Assessment",
        "03_👂_Hearing_Assessment": "Hearing Assessment",
        "04_📊_Results_History": "Results History",  # Fixed: Updated emoji
        "05_👨‍💼_Admin_Dashboard": "Admin Dashboard",
        "06_👤_Profile": "Profile"
    }
    return display_names.get(page_name, page_name)

def show_navbar():
    """Display the navigation bar"""
    load_navbar_css()
    
    # Get current page and user info
    current_page = get_current_page()
    username = st.session_state.get('username', 'User')
    user_role = st.session_state.get('user_role', 'patient')
    is_admin = st.session_state.get('user_role') in ['admin', 'doctor']
    
    # Get previous page for back button
    previous_page = get_previous_page(current_page)
    
    # Create navbar HTML
    navbar_html = f"""
    <div class="navbar">
        <div class="navbar-content">
            <!-- Logo Section -->
            <div class="navbar-logo">
                🏥 MediAssess
            </div>
            
            <!-- Back Button (if applicable) -->
            {f'''
            <div class="back-button" onclick="goToPreviousPage()">
                ← Back to {get_page_display_name(previous_page)}
            </div>
            ''' if previous_page else ''}
            
            <!-- Navigation Links -->
            <div class="navbar-nav">
                <div class="nav-item {'active' if current_page == '01_🏠_Home' else ''}" onclick="navigateToPage('pages/01_🏠_Home.py')">
                    🏠 Home
                </div>
                <div class="nav-item {'active' if current_page == '02_👁️_Eye_Assessment' else ''}" onclick="navigateToPage('pages/02_👁️_Eye_Assessment.py')">
                    👁️ Eye Test
                </div>
                <div class="nav-item {'active' if current_page == '03_👂_Hearing_Assessment' else ''}" onclick="navigateToPage('pages/03_👂_Hearing_Assessment.py')">
                    👂 Hearing Test
                </div>
                <div class="nav-item {'active' if current_page == '04_📊_Results_History' else ''}" onclick="navigateToPage('pages/04_📊_Results_History.py')">
                    📊 Results
                </div>
                {f'''
                <div class="nav-item {'active' if current_page == '05_👨‍💼_Admin_Dashboard' else ''}" onclick="navigateToPage('pages/05_👨‍💼_Admin_Dashboard.py')">
                    👨‍💼 Admin
                </div>
                ''' if is_admin else ''}
            </div>
            
            <!-- User Section -->
            <div class="navbar-user">
                <div class="dropdown">
                    <div class="user-avatar">
                        👤
                    </div>
                    <div class="dropdown-content">
                        <div class="dropdown-item" onclick="navigateToPage('pages/06_👤_Profile.py')">
                            👤 Profile
                        </div>
                        <div class="dropdown-item" onclick="logout()">
                            🚪 Logout
                        </div>
                    </div>
                </div>
                <div>
                    <div style="font-weight: bold; font-size: 0.9rem;">{username}</div>
                    <div style="font-size: 0.8rem; opacity: 0.8;">{user_role.title()}</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
    function navigateToPage(page) {{
        // Use Streamlit's switch_page functionality
        const event = new CustomEvent('streamlit:switch_page', {{
            detail: {{ page: page }}
        }});
        window.dispatchEvent(event);
        
        // Fallback: reload with page parameter
        window.location.href = window.location.origin + '/' + page;
    }}
    
    function goToPreviousPage() {{
        const previousPage = '{previous_page}';
        if (previousPage === 'streamlit_app') {{
            navigateToPage('streamlit_app.py');
        }} else {{
            navigateToPage('pages/' + previousPage + '.py');
        }}
    }}
    
    function logout() {{
        // Clear session and redirect to login
        fetch('/logout', {{method: 'POST'}})
            .then(() => {{
                window.location.href = window.location.origin;
            }})
            .catch(() => {{
                // Fallback: just reload to login page
                window.location.href = window.location.origin;
            }});
    }}
    </script>
    """
    
    st.markdown(navbar_html, unsafe_allow_html=True)

# Primary Streamlit-native navbar (recommended for reliability)
def show_streamlit_navbar():
    """Show navbar using pure Streamlit components"""
    load_navbar_css()
    
    # Create top section with logo and user info
    with st.container():
        col1, col2, col3 = st.columns([3, 6, 3])
        
        with col1:
            st.markdown("### 🏥 MediAssess")
        
        with col3:
            username = st.session_state.get('username', 'User')
            user_role = st.session_state.get('user_role', 'patient')
            st.markdown(f"**👤 {username}** ({user_role.title()})")
    
    # Navigation buttons
    current_page = get_current_page()
    previous_page = get_previous_page(current_page)
    is_admin = st.session_state.get('user_role') in ['admin', 'doctor']
    
    # Navigation columns
    nav_cols = st.columns([1, 1, 1, 1, 1, 1, 1] if is_admin else [1, 1, 1, 1, 1, 1])
    
    with nav_cols[0]:
        if previous_page:
            if st.button(f"← {get_page_display_name(previous_page)}", key="nav_back", use_container_width=True):
                if previous_page == 'streamlit_app':
                    st.switch_page('streamlit_app.py')
                else:
                    st.switch_page(f'pages/{previous_page}.py')
    
    with nav_cols[1]:
        home_style = "primary" if current_page == '01_🏠_Home' else "secondary"
        if st.button("🏠 Home", key="nav_home", type=home_style, use_container_width=True):
            st.switch_page('pages/01_🏠_Home.py')
    
    with nav_cols[2]:
        eye_style = "primary" if current_page == '02_👁️_Eye_Assessment' else "secondary"
        if st.button("👁️ Eye Test", key="nav_eye", type=eye_style, use_container_width=True):
            st.switch_page('pages/02_👁️_Eye_Assessment.py')
    
    with nav_cols[3]:
        hearing_style = "primary" if current_page == '03_👂_Hearing_Assessment' else "secondary"
        if st.button("👂 Hearing", key="nav_hearing", type=hearing_style, use_container_width=True):
            st.switch_page('pages/03_👂_Hearing_Assessment.py')
    
    with nav_cols[4]:
        results_style = "primary" if current_page == '04_📊_Results_History' else "secondary"
        if st.button("📊 Results", key="nav_results", type=results_style, use_container_width=True):
            st.switch_page('pages/04_📊_Results_History.py')
    
    if is_admin:
        with nav_cols[5]:
            admin_style = "primary" if current_page == '05_👨‍💼_Admin_Dashboard' else "secondary"
            if st.button("👨‍💼 Admin", key="nav_admin", type=admin_style, use_container_width=True):
                st.switch_page('pages/05_👨‍💼_Admin_Dashboard.py')
        
        with nav_cols[6]:
            col_profile, col_logout = st.columns(2)
            with col_profile:
                profile_style = "primary" if current_page == '06_👤_Profile' else "secondary"
                if st.button("👤", key="nav_profile", type=profile_style, use_container_width=True):
                    st.switch_page('pages/06_👤_Profile.py')
            
            with col_logout:
                if st.button("🚪", key="nav_logout", use_container_width=True):
                    # Clear session state for logout
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.switch_page('streamlit_app.py')
    else:
        with nav_cols[5]:
            col_profile, col_logout = st.columns(2)
            with col_profile:
                profile_style = "primary" if current_page == '06_👤_Profile' else "secondary"
                if st.button("👤 Profile", key="nav_profile", type=profile_style, use_container_width=True):
                    st.switch_page('pages/06_👤_Profile.py')
            
            with col_logout:
                if st.button("🚪 Logout", key="nav_logout", use_container_width=True):
                    # Clear session state for logout
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.switch_page('streamlit_app.py')
    
    st.markdown("---")

# Legacy support function
def show_navbar_legacy():
    """Legacy navbar function for backward compatibility"""
    return show_streamlit_navbar()
