import streamlit as st
import auth
import database
import pandas as pd
from datetime import datetime
import styles

# Page Config
st.set_page_config(page_title="PM Tool - Risk Register", layout="wide")

def risk_register_page():
    auth.require_role(['recorder', 'pm', 'admin'])
    styles.global_css()
    st.title("Risk Register Management")
    st.markdown("Log new risks and resolve existing ones.")
    
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
    
    selected_project_str = st.selectbox("Select Project to Manage Risks", project_list)
    project_id = project_map[selected_project_str]
    
    st.divider()

    # --- RISK MANAGEMENT LOGIC ---

    # A. Add New Risk Form
    with st.expander("➕ Log New Risk / Issue", expanded=True):
        with st.form("add_risk_form"):
            r_desc = st.text_input("Risk/Issue Description")
            c1, c2 = st.columns(2)
            with c1:
                r_impact = st.selectbox("Impact Level", ["H", "M", "L"])
            with c2:
                r_date = st.date_input("Date Identified", value=datetime.today())
            
            r_mitigation = st.text_area("Mitigation Plan")
            
            submitted = st.form_submit_button("Log Risk")
            if submitted and r_desc:
                new_risk_data = {
                    'project_id': project_id,
                    'description': r_desc,
                    'impact': r_impact,
                    'date_identified': r_date,
                    'mitigation_action': r_mitigation,
                    'status': 'Open'
                }
                database.add_risk(new_risk_data, current_user['id'])
                st.success("Risk logged successfully!")
                st.rerun()

    st.markdown("### Open Risks")
    
    # B. List & Close Risks
    risks = database.get_project_risks(project_id)
    open_risks = risks[risks['status'] == 'Open'] if not risks.empty else pd.DataFrame()
    
    if not open_risks.empty:
        for _, risk in open_risks.iterrows():
            with st.container(border=True):
                rc1, rc2, rc3 = st.columns([4, 1, 1])
                with rc1:
                    st.markdown(f"**{risk['description']}**")
                    st.caption(f"📅 {risk['date_identified']} | Plan: {risk['mitigation_action']}")
                with rc2:
                    color = "red" if risk['impact'] == 'H' else ("orange" if risk['impact'] == 'M' else "blue")
                    st.markdown(f":{color}[**{risk['impact']}-Impact**]")
                with rc3:
                    if st.button("Resolve", key=f"close_risk_{risk['risk_id']}", type="primary"):
                        database.update_risk_status(risk['risk_id'], "Resolved", current_user['id'])
                        st.success("Risk resolved.")
                        st.rerun()
    else:
        st.info("✅ No active open risks.")

    # Show History
    st.divider()
    with st.expander("View Resolved Risks"):
        resolved_risks = risks[risks['status'] != 'Open'] if not risks.empty else pd.DataFrame()
        if not resolved_risks.empty:
            st.dataframe(
                resolved_risks[['date_identified', 'description', 'impact', 'status', 'mitigation_action']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.caption("No resolved risks yet.")

if __name__ == "__main__":
    risk_register_page()
