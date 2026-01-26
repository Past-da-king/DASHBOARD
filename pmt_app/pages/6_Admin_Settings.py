import streamlit as st
import database
import auth
import styles
import pandas as pd

# Page Config
st.set_page_config(page_title="PM Tool - System Admin", layout="wide")

def admin_settings_page():
    auth.require_role(['admin'])
    styles.global_css()
    
    st.title("🛡️ System Administration")
    st.markdown("Manage user access, approvals, and system lifecycle.")
    
    tab1, tab2, tab3 = st.tabs(["👥 Users & Approvals", "🔐 Project Access", "⚙️ Logs"])
    
    with tab1:
        st.subheader("Account Requests")
        users = database.get_all_users()
        if users.empty: st.info("No users found."); return

        # 1. Pending Approvals
        pending = users[users['status'] == 'pending']
        if not pending.empty:
            st.warning(f"{len(pending)} pending request(s).")
            for _, u in pending.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 1, 1])
                    c1.markdown(f"**{u['full_name']}** (@{u['username']}) - {u['role'].upper()}")
                    if c2.button("Approve", key=f"app_{u['user_id']}", type="primary", use_container_width=True):
                        database.update_user_status(u['user_id'], 'approved')
                        st.success("Approved!"); st.rerun()
                    if c3.button("Reject", key=f"rej_{u['user_id']}", use_container_width=True):
                        database.delete_user(u['user_id'])
                        st.rerun()
        else:
            st.success("No pending approvals.")

        st.divider()

        # 2. Active User Directory (Refactored for Visibility)
        st.subheader("Active User Directory")
        active = users[users['status'] != 'pending']
        
        # Table Header
        h1, h2, h3, h4 = st.columns([3, 2, 2, 2])
        h1.caption("User Details")
        h2.caption("Role")
        h3.caption("Status")
        h4.caption("Actions")
        
        for _, u in active.iterrows():
            with st.container():
                c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
                c1.markdown(f"**{u['full_name']}**\n@{u['username']}")
                
                # Inline Edit - Role
                current_role_idx = 0
                roles = ["pm", "executive", "recorder", "admin"]
                if u['role'] in roles:
                    current_role_idx = roles.index(u['role'])
                    
                new_role = c2.selectbox("Role", roles, 
                                      index=current_role_idx, 
                                      key=f"role_{u['user_id']}", label_visibility="collapsed")
                
                if new_role != u['role']:
                    # Prevent self-demotion if you are the only one? No, just prevent current user demotion
                    if u['username'] == auth.get_current_user()['username'] and new_role != 'admin':
                         st.toast("⚠️ You cannot revoke your own admin rights!", icon="⚠️")
                    else:
                        database.update_user_role(u['user_id'], new_role)
                        st.toast(f"Updated role for {u['username']}"); st.rerun()
                
                c3.markdown(f"`{u['status'].upper()}`")
                
                # DANGER ZONE BUTTON INLINE
                if c4.button("🗑️ Delete", key=f"del_u_{u['user_id']}", type="primary", use_container_width=True):
                    if u['username'] == 'admin':
                        st.error("Root Admin protected.")
                    else:
                        database.delete_user(u['user_id'])
                        st.warning(f"Deleted {u['username']}")
                        st.rerun()
                st.divider()

    with tab2:
        st.subheader("Manage Project Team Assignments")
        projects = database.get_projects(pm_id=None) # Get All
        if projects.empty: st.info("No projects created yet."); st.stop()
        
        # Select Project
        proj_map = {f"{r['project_number']} - {r['project_name']} (PM: {r['pm_user_id']})": r for _, r in projects.iterrows()}
        sel_p_str = st.selectbox("Select Project to Manage", list(proj_map.keys()))
        target_p = proj_map[sel_p_str]
        p_id = target_p['project_id']
        
        st.markdown(f"**Editing Access for:** {target_p['project_name']}")
        
        # 1. Change Lead PM
        pm_users = database.get_df("SELECT user_id, full_name FROM users WHERE role IN ('pm', 'admin')")
        pm_idx = 0
        pm_ids = pm_users['user_id'].tolist()
        
        current_pm_id = target_p['pm_user_id']
        if current_pm_id in pm_ids:
            pm_idx = pm_ids.index(current_pm_id)
            
        new_pm_id = st.selectbox("Lead Project Manager", pm_users['user_id'].tolist(), 
                               format_func=lambda x: pm_users[pm_users['user_id']==x]['full_name'].values[0],
                               index=pm_idx)
                               
        if new_pm_id != current_pm_id:
            if st.button("Update Lead PM", type="primary"):
                database.update_project_pm(p_id, new_pm_id, auth.get_current_user()['id'])
                st.success("Project Manager updated successfully.")
                st.rerun()
        
        st.divider()
        
        # 2. Manage Team
        st.markdown("### Team Members (Recorders/Assistants)")
        # Get current assignments
        current_assigns = database.get_project_assignments(p_id)
        # Filter for non-PM roles only
        current_team_ids = current_assigns[current_assigns['assigned_role'] != 'pm']['user_id'].tolist()
        
        all_users = database.get_df("SELECT user_id, full_name, role FROM users WHERE status='approved'")
        # Exclude the CURRENT Lead PM from the team list
        avail_team = all_users[all_users['user_id'] != new_pm_id]
        
        user_map = {row['user_id']: f"{row['full_name']} ({row['role']})" for _, row in avail_team.iterrows()}
        
        # Multiselect with defaults
        # Filter defaults to ensure they exist in user_map
        valid_defaults = [uid for uid in current_team_ids if uid in user_map]
        
        new_team = st.multiselect("Assigned Staff", options=list(user_map.keys()), 
                                format_func=lambda x: user_map[x],
                                default=valid_defaults)
                                
        if st.button("Update Project Team"):
            # Update logic: Clear old team, set new team
            database.execute_query("DELETE FROM project_assignments WHERE project_id = ? AND assigned_role != 'pm'", (p_id,), commit=True)
            for uid in new_team:
                database.assign_user_to_project(p_id, uid, 'recorder', auth.get_current_user()['id'])
            st.success("Team assignments updated!")
            st.rerun()

    with tab3:
        st.subheader("System Access Logs")
        logs = database.get_df("SELECT * FROM audit_log ORDER BY changed_at DESC LIMIT 50")
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)
        else:
            st.info("No system logs recorded yet.")

if __name__ == "__main__":
    admin_settings_page()
