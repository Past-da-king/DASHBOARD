import streamlit as st
import auth
import database
import pandas as pd
from datetime import datetime
import styles

# Page Config
st.set_page_config(page_title="PM Tool - Record Activity", layout="wide")

def record_activity_page():
    auth.require_role(['recorder', 'pm', 'admin'])
    styles.global_css()
    st.title("Activity Status Management")
    st.markdown("Update the current progress of project phases. *Strict dependency rules apply.*")
    
    # 1. Fetch Projects (RBAC)
    current_user = auth.get_current_user()
    is_global_role = current_user['role'] in ['admin', 'executive', 'recorder']
    pm_id_filter = None if is_global_role else current_user['id']
    projects = database.get_projects(pm_id=pm_id_filter)
    
    if projects.empty:
        st.info("No projects assigned to you found.")
        st.stop()
        
    project_map = {f"{row['project_number']} - {row['project_name']}": row['project_id'] 
                   for _, row in projects.iterrows()}
    project_list = list(project_map.keys())
    
    selected_project_str = st.selectbox("Select Project", project_list)
    project_id = project_map[selected_project_str]
    
    # 2. Fetch Activities for selected project with CURRENT STATUS
    activities = database.get_df("SELECT * FROM baseline_schedule WHERE project_id = ?", (project_id,))
    
    if activities is None or activities.empty:
        st.warning("⚠️ This project has no schedule activities defined.")
        st.stop()
        
    st.divider()
    
    st.divider()

    st.subheader("Current Operational Status")
    
    # Sort by planned start
    activities['planned_start'] = pd.to_datetime(activities['planned_start'])
    activities = activities.sort_values('planned_start')
    
    for _, row in activities.iterrows():
        with st.container(border=True):
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.markdown(f"**{row['activity_name']}**")
                st.caption(f"Planned: {row['planned_start'].strftime('%d %b')} - {row['planned_finish']}")
            
            with c2:
                # Color code status
                status = row['status'] or 'Not Started'
                s_color = "black" if status == "Complete" else ("green" if status == "Active" else "#666")
                st.markdown(f"Status: <span style='color:{s_color}; font-weight:bold;'>{status}</span>", unsafe_allow_html=True)
            
            with c3:
                # Logic for status progression
                if status == "Not Started":
                    target = "Active"
                    btn_label = "Start Phase"
                elif status == "Active":
                    target = "Complete"
                    btn_label = "Finish Phase"
                else:
                    target = None
                    btn_label = "Already Done"
                
                if target:
                    if st.button(btn_label, key=f"btn_{row['activity_id']}", use_container_width=True):
                        success, msg = database.update_activity_status(row['activity_id'], target, auth.get_current_user()['id'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.button(btn_label, disabled=True, key=f"btn_{row['activity_id']}", use_container_width=True)

    # 4. View Audit Log (Optional/Hidden in expander)
    with st.expander("View Activity Audit Log (History)"):
        logs = database.get_df('''
            SELECT al.event_type, al.event_date, bs.activity_name, u.full_name as recorded_by
            FROM activity_log al
            JOIN baseline_schedule bs ON al.activity_id = bs.activity_id
            JOIN users u ON al.recorded_by = u.user_id
            WHERE bs.project_id = ?
            ORDER BY al.log_id DESC
        ''', (project_id,))
        if not logs.empty:
            st.dataframe(logs, use_container_width=True)

if __name__ == "__main__":
    record_activity_page()
