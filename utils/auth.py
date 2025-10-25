import streamlit as st
import sqlite3
import hashlib
import time
import os


def init_session_state():
    """Initialize session variables"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'user_role' not in st.session_state:
        st.session_state['user_role'] = None
    if 'admin_authenticated' not in st.session_state:
        st.session_state['admin_authenticated'] = False
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'admin_user' not in st.session_state:
        st.session_state['admin_user'] = None
    if 'just_logged_in' not in st.session_state:
        st.session_state['just_logged_in'] = False


def create_user_table():
    """Create users table and default entries"""
    try:
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'patient',
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        c.execute(create_table_sql)
        
        admin_pw = hash_password("admin123")
        doctor_pw = hash_password("doctor123")
        
        c.execute('SELECT * FROM users WHERE username = ?', ("admin",))
        if not c.fetchone():
            c.execute('INSERT INTO users (username, email, password, role, full_name) VALUES (?, ?, ?, ?, ?)',
                      ("admin", "admin@hospital.com", admin_pw, "admin", "System Administrator"))
        
        c.execute('SELECT * FROM users WHERE username = ?', ("doctor",))
        if not c.fetchone():
            c.execute('INSERT INTO users (username, email, password, role, full_name) VALUES (?, ?, ?, ?, ?)',
                      ("doctor", "doctor@hospital.com", doctor_pw, "doctor", "Dr. Smith"))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Database initialization error: {e}")
        st.info("The app will continue with limited functionality.")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_user(username, password):
    try:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        pw_hash = hash_password(password)
        c.execute('SELECT id, username, email, role, full_name FROM users WHERE username=? AND password=?',
                  (username, pw_hash))
        user = c.fetchone()
        conn.close()
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2],
                "role": user[3],
                "full_name": user[4]
            }
        return None
    except Exception as e:
        st.error(f"Authentication failed: {e}")
        return None


def create_user(username, email, password, role="patient", full_name=""):
    try:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        pw_hash = hash_password(password)
        c.execute('INSERT INTO users (username, email, password, role, full_name) VALUES (?, ?, ?, ?, ?)',
                  (username, email, pw_hash, role, full_name))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        st.error(f"User creation failed: {e}")
        return False


def authenticate_user(username, password, admin_only=False):
    user = verify_user(username, password)
    if user:
        if admin_only and user["role"] not in ("admin", "doctor"):
            return False, None
        return True, user
    return False, None


def login_flow(admin_only=False):
    if admin_only:
        st.subheader("Login as Administrator")
    else:
        st.subheader("Login as Patient")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
        
        if submitted:
            success, user = authenticate_user(username, password, admin_only)
            if success:
                st.session_state['authenticated'] = True
                st.session_state['username'] = username
                st.session_state['user_role'] = user['role']
                st.session_state['user_id'] = user['id']
                if user['role'] in ('admin', 'doctor'):
                    st.session_state['admin_authenticated'] = True
                    st.session_state['admin_user'] = user
                st.session_state['just_logged_in'] = True
                st.success(f"Welcome {user['full_name']}")
                
                # Redirect admins directly to admin dashboard
                if user['role'] in ('admin', 'doctor'):
                    st.info("Redirecting to Admin Dashboard...")
                    time.sleep(1)
                    st.switch_page("pages/05_👨‍💼_Admin_Dashboard.py")
                else:
                    time.sleep(2)
                    st.rerun()
            else:
                st.error("Invalid username or password.")


def admin_login():
    login_flow(admin_only=True)


def patient_login():
    login_flow(admin_only=False)


def show_login_signup():
    create_user_table()
    st.title("Medical Assessment Platform")
    st.markdown("---")
    
    choice = st.radio("Login as:", ("Patient", "Admin / Doctor"), horizontal=True)
    if choice == "Admin / Doctor":
        admin_login()
    else:
        tab1, tab2 = st.tabs(("Login", "Sign up"))
        with tab1:
            patient_login()
        with tab2:
            st.subheader("Create new account")
            with st.form("signup_form"):
                full_name = st.text_input("Full Name")
                username = st.text_input("Username")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                confirm_password = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("Sign up")
                
                if submitted:
                    if not full_name or not username or not email or not password:
                        st.error("All fields are required.")
                    elif password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif create_user(username, email, password, role="patient", full_name=full_name):
                        st.success("Account created! Please log in.")
                    else:
                        st.error("Username or email already registered.")


def show_user_profile():
    """Display user profile and allow updates"""
    st.title("User Profile")
    
    if not st.session_state.get('authenticated', False):
        st.error("Please log in to view your profile.")
        return
    
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username')
    
    try:
        conn = sqlite3.connect('data/users.db')
        c = conn.cursor()
        c.execute('SELECT username, email, full_name, role, created_at FROM users WHERE id=?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        if user:
            st.info(f"**Role:** {user[3].title()}")
            st.info(f"**Member since:** {user[4]}")
            
            with st.form("profile_form"):
                st.subheader("Update Profile")
                new_name = st.text_input("Full Name", value=user[2] or "")
                new_email = st.text_input("Email", value=user[1])
                
                st.subheader("Change Password (Optional)")
                current_pw = st.text_input("Current Password", type="password")
                new_pw = st.text_input("New Password", type="password")
                confirm_pw = st.text_input("Confirm New Password", type="password")
                
                submitted = st.form_submit_button("Update Profile")
                
                if submitted:
                    updated = False
                    
                    if new_name != user[2] or new_email != user[1]:
                        try:
                            conn = sqlite3.connect('data/users.db')
                            c = conn.cursor()
                            c.execute('UPDATE users SET full_name=?, email=? WHERE id=?', 
                                     (new_name, new_email, user_id))
                            conn.commit()
                            conn.close()
                            updated = True
                        except sqlite3.IntegrityError:
                            st.error("Email already registered to another account.")
                            return
                        except Exception as e:
                            st.error(f"Failed to update profile: {e}")
                            return
                    
                    if current_pw and new_pw:
                        if new_pw != confirm_pw:
                            st.error("New passwords do not match.")
                            return
                        if len(new_pw) < 6:
                            st.error("New password must be at least 6 characters.")
                            return
                        if verify_user(username, current_pw):
                            try:
                                conn = sqlite3.connect('data/users.db')
                                c = conn.cursor()
                                c.execute('UPDATE users SET password=? WHERE id=?', 
                                         (hash_password(new_pw), user_id))
                                conn.commit()
                                conn.close()
                                updated = True
                            except Exception as e:
                                st.error(f"Failed to update password: {e}")
                                return
                        else:
                            st.error("Current password is incorrect.")
                            return
                    
                    if updated:
                        st.success("Profile updated successfully!")
                        time.sleep(1)
                        st.rerun()  # ← FIXED: Use st.rerun()
        else:
            st.error("User not found.")
            
    except Exception as e:
        st.error(f"Failed to load profile: {e}")


def is_admin():
    return st.session_state.get('user_role') == 'admin'


def is_doctor():
    return st.session_state.get('user_role') == 'doctor'


def is_admin_authenticated():
    return st.session_state.get('admin_authenticated', False)


def get_current_user():
    return st.session_state.get('admin_user', {})


def logout():
    """Log out current user"""
    keys_to_clear = {
        'authenticated', 'username', 'user_role', 
        'admin_authenticated', 'user_id', 'admin_user', 'just_logged_in'
    }
    
    for key in list(st.session_state.keys()):
        if key in keys_to_clear or key.startswith('patient_'):
            del st.session_state[key]


# Initialize session state
init_session_state()
