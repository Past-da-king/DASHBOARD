import streamlit as st
import auth
import database
import styles

# Page Config
st.set_page_config(
    page_title="PM Tool - Login",
    page_icon="🛡️",
    layout="centered"
)

# Custom CSS for Premium Look
# Custom CSS for Premium Look
st.markdown("""
<style>
    /* --- GLOBAL THEME --- */
    :root {
        --primary-color: #2c5aa0;
        --secondary-color: #5fa2e8;
        --bg-color: #f8f9fa;
        --text-color: #333333;
        --card-bg: #ffffff;
    }

    /* Main Container */
    .stApp {
        background-color: var(--bg-color);
        font-family: 'Segoe UI', 'Inter', sans-serif;
    }

    /* --- TYPOGRAPHY --- */
    h1, h2, h3 {
        color: var(--primary-color) !important;
        font-weight: 600 !important;
    }
    
    p, div, span {
        color: var(--text-color);
    }

    /* --- COMPONENTS --- */
    
    /* Buttons (Pill shaped, premium feel) */
    .stButton > button {
        border-radius: 20px;
        background-color: white;
        color: var(--primary-color);
        border: 1px solid var(--primary-color);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: var(--primary-color);
        color: white;
        border-color: var(--primary-color);
        box-shadow: 0 4px 6px rgba(44, 90, 160, 0.2);
    }
    
    /* Primary Action Buttons */
    .stButton > button[kind="primary"] {
        background-color: var(--primary-color);
        color: white;
    }

    /* Cards/Containers */
    .css-1r6slb0, .stContainer { 
        /* Streamlit container targeting is tricky, using custom classes instead */
    }
    
    .login-container {
        background-color: var(--card-bg);
        padding: 3rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        max-width: 450px;
        margin: auto;
    }
    
    .header {
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    auth.init_session()
    
    # Apply Global Styles
    styles.global_css()
    
    if not auth.is_logged_in():
        # --- AUTHENTICATION SCREEN ---
        st.markdown("<h1 class='header'>PROJECT MANAGEMENT PORTAL</h1>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Create Account"])
        
        with tab_login:
            with st.container(border=True):
                l_user = st.text_input("Username", key="l_user")
                l_pass = st.text_input("Password", type="password", key="l_pass")
                
                if st.button("Login to Dashboard", use_container_width=True, type="primary"):
                    if auth.login(l_user, l_pass):
                        st.success("Welcome back!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
            st.info("Test Accounts:\n- admin / admin123\n- pm_user / pm123")

        with tab_signup:
            with st.container(border=True):
                s_name = st.text_input("Full Name")
                s_user = st.text_input("Username", help="Create a unique username")
                s_pass = st.text_input("Password", type="password", key="s_pass")
                s_role = st.selectbox("Your Role", ["Project Manager", "Executive", "Field Recorder"])
                
                role_map = {"Project Manager": "pm", "Executive": "executive", "Field Recorder": "recorder"}
                
                if st.button("Create Account", use_container_width=True):
                    if s_name and s_user and s_pass:
                        success, msg = auth.register(s_user, s_pass, s_name, role_map[s_role])
                        if success:
                            st.success(f"Account created for {s_name}! You can now login.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please fill in all fields.")

    else:
        # --- DYNAMIC NAVIGATION (RBAC) ---
        user = auth.get_current_user()
        role = user['role']
        status = user.get('status', 'pending')
        
        # 1. Define Navigation Targets
        exe_dash = st.Page("pages/1_Executive_Dashboard.py", title="Executive Insights", icon="📊")
        pm_dash = st.Page("pages/2_PM_Dashboard.py", title="Project Dashboard", icon="📈")
        setup = st.Page("pages/3_Project_Setup.py", title="Project Setup", icon="🏗️")
        rec_act = st.Page("pages/4_Record_Activity.py", title="Log Progress", icon="📝")
        rec_exp = st.Page("pages/5_Record_Expenditure.py", title="Log Expenditure", icon="💰")
        
        # Admin Page with Dynamic Title
        pending_count = database.get_pending_users_count() if role == 'admin' else 0
        admin_title = f"System Admin ({pending_count})" if pending_count > 0 else "System Admin"
        admin_page = st.Page("pages/6_Admin_Settings.py", title=admin_title, icon="🛡️")

        # 2. Define Home Page Content
        def show_home():
            st.title(f"Welcome, {user['full_name']}! 👋")
            
            if status == 'approved':
                st.write(f"Logged in as project portal **{role.upper()}**.")
                st.info("Use the sidebar to navigate to your assigned modules.")
                if pending_count > 0:
                    st.warning(f"🔔 **{pending_count}** new account(s) are waiting for your approval. Please visit System Admin.")
            elif status == 'pending':
                st.error("⏳ **ACCOUNT PENDING APPROVAL**")
                st.info("Your account has been created successfully but is currently waiting for System Administrator verification. You will be able to access the dashboards once approved.")
            else:
                st.error(f"🚫 **ACCESS RESTRICTED**")
                st.write(f"This account is currently **{status.upper()}**. Please contact support.")

        home = st.Page(show_home, title="Home", icon="🏠", default=True)

        # 3. Assign Visibility based on Status & Role
        pages = [home]
        
        # Only Approved users see other pages
        if status == 'approved':
            if role == 'admin':
                pages += [exe_dash, pm_dash, setup, admin_page]
            elif role == 'executive':
                pages += [exe_dash, pm_dash]
            elif role == 'pm':
                pages += [pm_dash, setup, rec_act, rec_exp]
            elif role == 'recorder':
                pages += [rec_act, rec_exp]

        # 4. Initialize Navigation
        pg = st.navigation(pages)
        
        # 5. Global Sidebar Footer
        with st.sidebar:
            st.markdown(f"**User**: {user['full_name']}")
            st.caption(f"**Role**: {user['role'].upper()} | **Status**: {status.upper()}")
            st.divider()
            if st.button("🚪 Logout", use_container_width=True):
                auth.logout()

        pg.run()

if __name__ == "__main__":
    main()
