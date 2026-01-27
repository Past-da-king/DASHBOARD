import pandas as pd
import database
from datetime import datetime

def import_project(file, user_id):
    """
    Parses the Project Template Excel and inserts data into the DB.
    """
    # Load Excel
    xl = pd.ExcelFile(file)
    
    # 1. Parse Project Info (from Project_Schedule sheet headers)
    # Using openpyxl directly for non-tabular data is better but for speed we'll use pandas read_excel with specific ranges if possible
    # For now, let's assume a slightly more robust way:
    df_info = pd.read_excel(xl, "Project_Schedule", header=None)
    
    project_data = {
        'project_name': df_info.iloc[4, 2],    # C5
        'project_number': str(df_info.iloc[5, 2]),# C6
        'client': df_info.iloc[6, 2],          # C7
        'total_budget': float(df_info.iloc[4, 5]) if pd.notna(df_info.iloc[4, 5]) else 0.0, # F5
        'start_date': str(df_info.iloc[5, 5])[:10] if pd.notna(df_info.iloc[5, 5]) else None, # F6
        'target_end_date': str(df_info.iloc[6, 5])[:10] if pd.notna(df_info.iloc[6, 5]) else None, # F7
        'pm_user_id': user_id
    }
    
    # Create Project in DB
    project_id = database.create_project(project_data, user_id)
    
    # 2. Parse Baseline Schedule (Row 11 is Header)
    df_schedule = pd.read_excel(xl, "Project_Schedule", skiprows=10)
    df_schedule = df_schedule.dropna(subset=['Activity Name'])
    
    for _, row in df_schedule.iterrows():
        activity_name = row['Activity Name']
        p_start = str(row['Planned Start'])[:10] if pd.notna(row['Planned Start']) else None
        p_end = str(row['Planned End'])[:10] if pd.notna(row['Planned End']) else None
        budget = float(row['Budgeted Cost (R)']) if pd.notna(row['Budgeted Cost (R)']) else 0.0
        depends = row['Depends On'] if pd.notna(row['Depends On']) and row['Depends On'] != '-' else None
        
        # Derive Status
        status = 'Not Started'
        if pd.notna(row.get('Actual End')):
            status = 'Complete'
        elif pd.notna(row.get('Actual Start')):
            status = 'Active'
            
        # Insert into baseline_schedule (including status)
        query = '''
        INSERT INTO baseline_schedule (project_id, activity_name, planned_start, planned_finish, budgeted_cost, depends_on, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        activity_id = database.execute_query(query, (project_id, activity_name, p_start, p_end, budget, depends, status), commit=True)
        
        # Seed activity log for history
        if status == 'Active':
            database.update_activity_log(activity_id, 'STARTED', str(row['Actual Start'])[:10], user_id)
        elif status == 'Complete':
            # Note: We log both START and FINISH for completed items to maintain valid timeline history
            act_start = str(row['Actual Start'])[:10] if pd.notna(row.get('Actual Start')) else p_start
            database.update_activity_log(activity_id, 'STARTED', act_start, user_id)
            database.update_activity_log(activity_id, 'FINISHED', str(row['Actual End'])[:10], user_id)

    # 3. Parse Expenditure Log
    df_exp = pd.read_excel(xl, "Expenditure_Log", skiprows=3)
    df_exp = df_exp.dropna(subset=['Amount (R)'])
    
    for _, row in df_exp.iterrows():
        data = {
            'project_id': project_id,
            'activity_id': None, # Linking by Activity ID from Excel might need mapping
            'category': row['Category'],
            'description': row['Description'],
            'reference_id': row['Reference (Invoice/PO)'],
            'amount': float(row['Amount (R)']),
            'spend_date': str(row['Date'])[:10]
        }
        database.add_expenditure(data, user_id)
        
    # 4. Parse Risk Register
    if "Risk_Register" in xl.sheet_names:
        df_risk = pd.read_excel(xl, "Risk_Register", skiprows=2)
        # Drop rows where 'Risk/Issue Description' is NaN
        df_risk = df_risk.dropna(subset=['Risk/Issue Description'])
        
        for _, row in df_risk.iterrows():
            risk_data = {
                'project_id': project_id,
                'date_identified': str(row['Date Identified'])[:10] if pd.notna(row['Date Identified']) else None,
                'description': row['Risk/Issue Description'],
                'impact': str(row['Impact (H/M/L)']).upper() if pd.notna(row['Impact (H/M/L)']) else 'M',
                'status': row['Status'] if pd.notna(row['Status']) else 'Open',
                'mitigation_action': row['Mitigation Action'] if pd.notna(row['Mitigation Action']) else None
            }
            database.add_risk(risk_data, user_id)

    return project_id
