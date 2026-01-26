import streamlit as st
import pandas as pd
from datetime import datetime
import auth
import database
import os
import styles

# Page Config
st.set_page_config(page_title="PM Tool - Project Setup", layout="wide")

def project_setup_page():
    auth.require_role(['pm', 'admin'])
    styles.global_css()
    st.title("Setup New Project")
    
    tab1, tab2 = st.tabs(["Manual Entry", "Excel Import"])
    
    with tab1:
        st.subheader("Enter Project Details")
        with st.form("manual_project_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Project Name *")
                number = st.text_input("Project Number *")
                client = st.text_input("Client Name")
                budget = st.number_input("Total Contract Value (R) *", min_value=0.0)
            
            with col2:
                start_date = st.date_input("Planned Start Date")
                end_date = st.date_input("Target Completion Date")
                
                # PM Assignment (RBAC)
                current_user = auth.get_current_user()
                if current_user['role'] == 'admin':
                    pm_options = database.get_df("SELECT user_id, full_name FROM users WHERE role = 'pm'")
                    pm_map = {row['full_name']: row['user_id'] for _, row in pm_options.iterrows()}
                    selected_pm_name = st.selectbox("Assign Project Manager", list(pm_map.keys()))
                    pm_id = pm_map[selected_pm_name]
                else:
                    pm_id = current_user['id']
                    st.info(f"Project will be assigned to you: **{current_user['full_name']}**")
                
                # Team Assignment (Recorders & Assistant PMs)
                team_options = database.get_df("SELECT user_id, full_name, role FROM users WHERE status = 'approved'")
                # Exclude the assigned PM from the list to avoid redundancy
                team_options = team_options[team_options['user_id'] != pm_id]
                
                team_map = {f"{row['full_name']} ({row['role']})": row['user_id'] for _, row in team_options.iterrows()}
                assigned_team = st.multiselect("Assign Project Team (Recorders/Assistants)", list(team_map.keys()))
            
            submit = st.form_submit_button("Create Project & Plan")
            
            st.markdown("---")
            st.subheader("Project Plan (Baseline Schedule)")
            st.info("Assign budget and dates to project phases/activities.")
            
            # Simple activity editor
            if 'activity_data' not in st.session_state:
                st.session_state.activity_data = [
                    {'activity_name': 'Initial Phase', 'planned_start': start_date, 'planned_finish': start_date, 'budgeted_cost': 0.0},
                    {'activity_name': 'Execution Phase', 'planned_start': start_date, 'planned_finish': end_date, 'budgeted_cost': 0.0}
                ]
            
            plan_df = st.data_editor(
                st.session_state.activity_data,
                num_rows="dynamic",
                use_container_width=True,
                column_config={
                    "activity_name": "Activity/Phase Name",
                    "planned_start": st.column_config.DateColumn("Start Date"),
                    "planned_finish": st.column_config.DateColumn("Finish Date"),
                    "budgeted_cost": st.column_config.NumberColumn("Budget (R)", min_value=0.0)
                }
            )

            if submit:
                if not name or not number or budget <= 0:
                    st.error("Please fill in name, number and contract value.")
                else:
                    data = {
                        'project_name': name,
                        'project_number': number,
                        'client': client,
                        'total_budget': budget,
                        'start_date': start_date.strftime('%Y-%m-%d'),
                        'target_end_date': end_date.strftime('%Y-%m-%d'),
                        'pm_user_id': pm_id
                    }
                    try:
                        creator_id = auth.get_current_user()['id']
                        project_id = database.create_project(data, creator_id)
                        
                        # 1. Assign Lead PM (Explicitly in Assignments Table)
                        database.assign_user_to_project(project_id, pm_id, 'pm', creator_id)
                        
                        # 2. Assign Team Members
                        if assigned_team:
                            for member_id in assigned_team:
                                database.assign_user_to_project(project_id, member_id, 'recorder', creator_id)
                        
                        # 3. Add Baseline Activities
                        for _, row in pd.DataFrame(plan_df).iterrows():
                            # Convert dates to strings
                            database.add_baseline_activity({
                                'project_id': project_id,
                                'activity_name': row['activity_name'],
                                'planned_start': row['planned_start'].strftime('%Y-%m-%d') if hasattr(row['planned_start'], 'strftime') else row['planned_start'],
                                'planned_finish': row['planned_finish'].strftime('%Y-%m-%d') if hasattr(row['planned_finish'], 'strftime') else row['planned_finish'],
                                'budgeted_cost': row['budgeted_cost']
                            })
                        
                        st.success(f"Project and Plan Created Successfully! ID: {project_id}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error creating project: {e}")

    with tab2:
        st.subheader("Import from Excel Template")
        st.info("Download the 'Project_Template.xlsx' and fill it out before uploading.")
        
        uploaded_file = st.file_uploader("Upload Project Excel", type=["xlsx"])
        
        if uploaded_file:
            import importer
            if st.button("Start Import"):
                try:
                    with st.spinner("Processing Excel..."):
                        project_id = importer.import_project(uploaded_file, auth.get_current_user()['id'])
                        st.success(f"Project Imported Successfully! ID: {project_id}")
                except Exception as e:
                    st.error(f"Import Failed: {e}")

if __name__ == "__main__":
    project_setup_page()
