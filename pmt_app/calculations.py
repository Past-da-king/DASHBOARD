import database
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_project_metrics(project_id):
    """
    Calculates all metrics for a single project.
    Ensures safe data access with explicit checks for empty results.
    """
    try:
        # 1. Load Data
        project_df = database.get_df("SELECT * FROM projects WHERE project_id = ?", (project_id,))
        if project_df is None or project_df.empty:
            logger.warning(f"Project with ID {project_id} not found.")
            return None
        
        project = project_df.iloc[0]
        
        # Load associated data
        baseline = database.get_df("SELECT * FROM baseline_schedule WHERE project_id = ?", (project_id,))
        expenditures = database.get_df("SELECT * FROM expenditure_log WHERE project_id = ?", (project_id,))
        
        # Activity log with joined activity names
        logs = database.get_df('''
            SELECT al.*, bs.activity_name, bs.budgeted_cost 
            FROM activity_log al 
            JOIN baseline_schedule bs ON al.activity_id = bs.activity_id 
            WHERE bs.project_id = ?
        ''', (project_id,))

        # 2. Financial Metrics
        total_budget = float(project['total_budget']) if pd.notna(project['total_budget']) else 0.0
        total_spent = 0.0
        if expenditures is not None and not expenditures.empty:
            total_spent = float(expenditures['amount'].sum())
        
        remaining = total_budget - total_spent
        
        # 3. % Completion (Based on Budget Weight of 'Complete' status)
        pct_complete = 0.0
        earned_value = 0.0
        total_planned = baseline['budgeted_cost'].sum() if not baseline.empty else 0.0
        
        if not baseline.empty and total_planned > 0:
            completed_budget = baseline[baseline['status'] == 'Complete']['budgeted_cost'].sum()
            pct_complete = (completed_budget / total_planned * 100)
            earned_value = completed_budget
        
        # 4. Forecast (Estimate at Completion - EAC)
        # Standard EVM: EAC = AC + (BAC - EV)
        # This assumes remaining work is done at planned rate
        forecast = total_spent + (total_budget - earned_value)
        
        # CPI = Cost Performance Index
        cpi = (earned_value / total_spent) if total_spent > 0 else 1.0
            
        # 5. Status Indicators (Earned Value Logic)
        budget_health = 'Green'
        
        # Proactive alerting: If prediction exceeds budget, turn Red
        if forecast > total_budget * 1.05 and total_budget > 0:
            budget_health = 'Red'
        elif forecast > total_budget and total_budget > 0:
            budget_health = 'Yellow'
        elif cpi < 0.85 and total_spent > 0:
            budget_health = 'Red' # High burn rate
        elif cpi < 0.95 and total_spent > 0:
            budget_health = 'Yellow'
        
        schedule_health = 'Green'
        # Simple schedule check: If we have activities but none are finished past their planned end date
        if not baseline.empty:
            baseline['planned_finish'] = pd.to_datetime(baseline['planned_finish'])
            today = pd.Timestamp.now()
            overdue = baseline[(baseline['planned_finish'] < today) & (baseline['status'] != 'Complete')]
            if not overdue.empty:
                schedule_health = 'Red'
        
        # 6. Financial Utilization
        budget_used_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0.0
        
        return {
            'project_id': project_id,
            'project_name': str(project['project_name']),
            'project_number': str(project['project_number']),
            'total_budget': total_budget,
            'total_spent': total_spent,
            'remaining': remaining,
            'pct_complete': min(pct_complete, 100.0),
            'budget_used_pct': budget_used_pct,
            'forecast': forecast,
            'budget_health': budget_health,
            'schedule_health': schedule_health,
            'actual_status': str(project.get('status', 'Planning'))
        }
    except Exception as e:
        logger.error(f"Error calculating metrics for project {project_id}: {e}")
        return None

def get_all_projects_summary():
    """
    Returns a summary dataframe for all projects.
    """
    try:
        projects = database.get_projects()
        if projects is None or projects.empty:
            return pd.DataFrame()
            
        summary = []
        for _, p in projects.iterrows():
            metrics = get_project_metrics(p['project_id'])
            if metrics:
                summary.append(metrics)
        
        return pd.DataFrame(summary)
    except Exception as e:
        logger.error(f"Error generating projects summary: {e}")
        return pd.DataFrame()
