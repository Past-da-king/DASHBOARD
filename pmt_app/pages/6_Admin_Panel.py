import streamlit as st
import auth
import database
import pandas as pd
import styles

# Page Config
st.set_page_config(page_title="PM Tool - Admin Panel", layout="wide")

def admin_panel():
    auth.require_role(['admin'])
    styles.global_css()
    st.title("Admin Panel")
    
    t1, t2 = st.tabs(["User Management", "Audit Logs"])
    
    with t1:
        st.subheader("Current Users")
        users = database.get_df("SELECT user_id, username, role, full_name FROM users")
        st.dataframe(users, use_container_width=True)
        
        st.divider()
        st.subheader("Add New User")
        with st.form("add_user_form"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["executive", "pm", "recorder"])
            new_name = st.text_input("Full Name")
            
            if st.form_submit_button("Add User"):
                from werkzeug.security import generate_password_hash
                try:
                    database.execute_query(
                        "INSERT INTO users (username, password_hash, role, full_name) VALUES (?, ?, ?, ?)",
                        (new_user, generate_password_hash(new_pass), new_role, new_name),
                        commit=True
                    )
                    st.success(f"User {new_user} created.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")

    with t2:
        st.subheader("System Audit Log")
        logs = database.get_df('''
            SELECT al.*, u.username 
            FROM audit_log al 
            LEFT JOIN users u ON al.changed_by = u.user_id 
            ORDER BY changed_at DESC
        ''')
        st.dataframe(logs, use_container_width=True)

if __name__ == "__main__":
    admin_panel()
