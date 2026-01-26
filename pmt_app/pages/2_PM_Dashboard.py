import streamlit as st
import auth
import database
import calculations
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os
import styles

# Page Config
st.set_page_config(
    page_title="PM Tool - Project Dashboard", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def pm_dashboard():
    auth.require_role(['pm', 'admin', 'executive'])
    
    # Apply Global Styles (Fixes header issue)
    styles.global_css()
    
    # --- BRAND COLORS (Perfectly Differentiated Palettes) ---
    COLORS = {
        # 1. Project Status Mapping (User Standard)
        'status_not_started': '#ffc107', # Yellow
        'status_active': '#4caf50',      # Green
        'status_complete': '#2c5aa0',    # Blue
        'status_critical': '#f44336',    # Red (Warnings only)

        # 2. Financial Overview (Professional Primary Tones)
        'fin_budget': '#334155',   # Deep Slate
        'fin_actual': '#0891b2',   # Clear Cyan
        'fin_forecast': '#7c3aed', # Deep Violet

        # 3. Cost Categories (Vibrant Secondary Tones - No Overlap)
        'cat_labour': '#db2777',   # Rose/Pink
        'cat_material': '#4f46e5', # Indigo
        'cat_vehicle': '#ea580c',  # Burnt Orange
        'cat_diesel': '#059669',   # Lush Green
        'cat_other': '#94a3b8',    # Cool Gray
        
        'text': '#1a1a1a',
        'subtext': '#64748b',
        'card_bg': '#ffffff'
    }

    # --- CUSTOM CSS INJECTION (Overrides/Additions to Global) ---
    st.markdown("""
    <style>
        /* Header Styling */
        .report-header {
            background-color: var(--primary-color);
            color: white !important;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(44, 90, 160, 0.2);
        }
        .report-title { 
            font-size: 2.2rem; 
            font-weight: 700; 
            margin: 0; 
            color: white !important;
            letter-spacing: -0.5px;
        }
        .report-date { 
            font-size: 0.95rem; 
            opacity: 0.9; 
            color: white !important; 
            margin-top: 0.5rem;
        }
        
        /* Section Headers */
        h3 {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-color) !important;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
            border-bottom: none;
        }
        
        /* KPI Cards */
        .kpi-card {
            background-color: var(--card-bg);
            border-left: 5px solid var(--primary-color);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.2s ease;
        }
        .kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        }
        .kpi-value { font-size: 1.8rem; font-weight: 700; color: var(--primary-color) !important; }
        .kpi-label { font-size: 0.9rem; color: var(--subtext-color) !important; text-transform: uppercase; letter-spacing: 0.5px; }
        
        /* Executive Summary Box */
        .summary-box {
            background-color: var(--card-bg);
            color: var(--text-color);
            padding: 2rem;
            border-radius: 12px;
            border: 1px solid #eee;
            margin-bottom: 1rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
            line-height: 1.8;
            min-height: 140px;
        }

        /* Health Indicators */
        .health-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 2rem 0;
            background: white;
            border-radius: 12px;
            border: 1px solid #eee;
            box-shadow: 0 4px 10px rgba(0,0,0,0.03);
            min-height: 160px;
        }
    </style>
    """, unsafe_allow_html=True)

    # --- PROJECT SELECTION (RBAC) ---
    current_user = auth.get_current_user()
    is_global_role = current_user['role'] in ['admin', 'executive']
    
    # Filter projects: PMs only see their own
    pm_id_filter = None if is_global_role else current_user['id']
    projects = database.get_projects(pm_id=pm_id_filter)
    
    if projects.empty:
        st.info("No projects assigned to you found.")
        st.stop()
        
    project_map = {f"{row['project_number']} - {row['project_name']}": row['project_id'] 
                   for _, row in projects.iterrows()}
    project_list = list(project_map.keys())
    
    selected_num = st.session_state.get('selected_project')
    default_idx = 0
    if selected_num:
        matches = [i for i, s in enumerate(project_list) if selected_num in s]
        if matches: default_idx = matches[0]

    # Sidebar for project selection
    with st.sidebar:
        st.header("Dashboard Controls")
        if st.button("Refresh Data", use_container_width=True, type="primary"):
            st.rerun()
        
        st.markdown("---")
        selected_project_str = st.selectbox("Select Project", project_list, index=default_idx)
    
    project_id = project_map[selected_project_str]
    
    # 1. Metrics Calculation
    m = calculations.get_project_metrics(project_id)
    if not m:
        st.error("Project details could not be retrieved.")
        st.stop()

    # --- REPORT LAYOUT ---

    # 1. HEADER
    st.markdown(f"""
    <div class="report-header">
        <div class="report-title">PROJECT STATUS REPORT</div>
        <div class="report-date">{m['project_name']} ({m['project_number']}) | {pd.Timestamp.now().strftime('%B %d, %Y')}</div>
    </div>
    """, unsafe_allow_html=True)

    # 2. EXECUTIVE SUMMARY & HEALTH
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Executive Summary")
        status_text = "exceeding budget" if m['forecast'] > m['total_budget'] else "well within budget"
        
        # Pre-format to avoid SyntaxError in specific Python/Streamlit combos
        formatted_pct = "{:.1f}%".format(m['pct_complete'])
        formatted_cost = "R {:,.2f}".format(m['forecast'])
        
        summary_html = f"""
        <div class="summary-box">
        The project <b>{m['project_name']}</b> is currently in <b>{m['actual_status']}</b> status. 
        Physical completion is estimated at <b>{formatted_pct}</b>. 
        Financial performance shows we are <b>{status_text}</b> with a forecasted completion cost of <b>{formatted_cost}</b>.
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

    with col2:
        st.markdown("### Project Health")
        
        health_data = [
            ('Scope', COLORS['status_active'], '✓'),
            ('Schedule', 
             COLORS['status_active'] if m['schedule_health'] == 'Green' else COLORS['status_not_started'], 
             '✓' if m['schedule_health'] == 'Green' else '!'),
            ('Budget', 
             COLORS['status_active'] if m['budget_health'] == 'Green' else (COLORS['status_not_started'] if m['budget_health'] == 'Yellow' else COLORS['status_critical']), 
             '✓' if m['budget_health'] == 'Green' else '!'),
            ('Resources', COLORS['status_active'], '✓')
        ]
        
        health_html = '<div class="health-container">'
        for label, hex_color, icon in health_data:
            # Logic: If it's solid, use color bg and white text. If it's warning, use border.
            is_active = (hex_color == COLORS['status_active'] or hex_color == COLORS['status_complete'])
            text_color = "white" if is_active else hex_color
            border = "none" if is_active else f"3px solid {hex_color}"
            inner_bg = hex_color if is_active else "white"
            
            health_html += f"""<div class="health-item"><div class="health-icon" style="background-color: {inner_bg}; color: {text_color}; border: {border};">{icon}</div><div class="health-label">{label}</div></div>"""
        health_html += '</div>'
        st.markdown(health_html, unsafe_allow_html=True)

    st.markdown("---")

    # --- DIALOGS (Full Screen Views) ---
    @st.dialog("Project Plan Details", width="large")
    def show_full_timeline(project_id, activities):
        if activities.empty:
            st.info("No activities to display.")
            return
            
        st.markdown("### Extended Project Schedule")
        
        activities['planned_start'] = pd.to_datetime(activities['planned_start'])
        activities['planned_finish'] = pd.to_datetime(activities['planned_finish'])
        activities = activities.sort_values('planned_start', ascending=False) # Latest -> Earliest for bottom-up plot
        
        fig = px.timeline(activities, x_start="planned_start", x_end="planned_finish", y="activity_name", 
                          color="status_mapped", 
                          color_discrete_map={
                              'Not Started': COLORS['status_not_started'], 
                              'Active': COLORS['status_active'], 
                              'Complete': COLORS['status_complete']
                          },
                          hover_data=["planned_start", "planned_finish", "budgeted_cost"])
        
        fig.update_yaxes(title="") # Default bottom-up will put earliest (last in df) at top
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", y=-0.1),
            xaxis_title="",
            yaxis_title="",
            height=max(400, len(activities)*40),
            margin=dict(l=10, r=10, t=10, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis=dict(showgrid=True, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig, use_container_width=True)

    @st.dialog("Detailed Financials & Drill-down", width="large")
    def show_full_financials(project_id):
        # 1. Fetch Granular Data
        df = database.get_df('''
            SELECT spend_date, category, amount, reference_id, description 
            FROM expenditure_log WHERE project_id = ? ORDER BY spend_date DESC
        ''', (project_id,))
        
        if df.empty:
            st.info("No expenditure recorded for this project yet.")
            return

        st.markdown("### Transaction Explorer")
        
        # DRILL-DOWN FILTER
        categories = ["All"] + sorted(df['category'].unique().tolist())
        selected_cat = st.selectbox("Drill-down by Category:", categories)
        
        filtered_df = df if selected_cat == "All" else df[df['category'] == selected_cat]
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown(f"#### {selected_cat} Transactions")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        with c2:
            st.markdown("#### Summary Stats")
            cat_sum = filtered_df.groupby('category')['amount'].sum().reset_index()
            st.dataframe(cat_sum, use_container_width=True, hide_index=True)
            st.metric("Total in View", f"R {filtered_df['amount'].sum():,.2f}")

        st.divider()
        st.markdown("### Category Distribution")
        
        overall_cat = df.groupby('category')['amount'].sum().reset_index()
        fig_cat = px.bar(overall_cat, x='category', y='amount', 
                        color='category',
                        color_discrete_map={
                            'Labour': COLORS['cat_labour'],
                            'Material': COLORS['cat_material'],
                            'Vehicle': COLORS['cat_vehicle'],
                            'Diesel': COLORS['cat_diesel'],
                            'Other': COLORS['cat_other']
                        },
                        text_auto='.2s')
        
        fig_cat.update_layout(
            xaxis_title="", yaxis_title="Total Spend (R)",
            showlegend=False, height=350, 
            plot_bgcolor='white'
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    @st.dialog("Milestones Tracker", width="large")
    def show_full_milestones(milestones_df):
        st.markdown("### Project Phases & Milestones")
        st.dataframe(
            milestones_df[['activity_name', 'planned_start', 'planned_finish', 'status']], 
            use_container_width=True, 
            hide_index=True,
            column_config={
                "status": st.column_config.SelectboxColumn("Status", options=["Not Started", "Active", "Complete"])
            }
        )

    # --- ROW 1: SCHEDULE & KEY METRICS ---
    r1_col1, r1_col2 = st.columns([1, 1])
    
    with r1_col1:
        st.markdown("### Project Schedule")
        comp = m['pct_complete']
        prog = 30 if comp < 70 else (100 - comp) / 2
        not_s = max(0, 100 - comp - prog)
        
        sched_fig = go.Figure()
        stages = [
            ('Not started', not_s, COLORS['status_not_started']), 
            ('In progress', prog, COLORS['status_active']), 
            ('Complete', comp, COLORS['status_complete'])
        ]
        
        y_pos = 0
        for label, val, color in stages:
            sched_fig.add_shape(type="rect", x0=0, y0=y_pos+0.1, x1=100, y1=y_pos+0.6, fillcolor="#f5f7fa", line=dict(width=0), layer='below')
            sched_fig.add_shape(type="rect", x0=0, y0=y_pos+0.1, x1=val, y1=y_pos+0.6, fillcolor=color, line=dict(width=0), layer='above')
            sched_fig.add_annotation(x=-2, y=y_pos+0.35, text=label, xanchor="right", showarrow=False, font=dict(color="#555", size=13))
            y_pos += 1.0

        sched_fig.update_layout(xaxis=dict(range=[-25, 105], visible=False), yaxis=dict(range=[-0.2, 3], visible=False), 
                                margin=dict(l=0, r=0, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(sched_fig, use_container_width=True, config={'displayModeBar': False})

    with r1_col2:
        st.markdown("### Key Metrics")
        k_col1, k_col2 = st.columns(2)
        with k_col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-value">R {m["total_budget"]:,.0f}</div><div class="kpi-label">Contract Budget</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-card" style="border-left-color: {COLORS["fin_forecast"]};"><div class="kpi-value">{m["budget_used_pct"]:.1f}%</div><div class="kpi-label">Budget Used</div></div>', unsafe_allow_html=True)
        with k_col2:
            st.markdown(f'<div class="kpi-card" style="border-left-color: {COLORS["fin_actual"]};"><div class="kpi-value">R {m["total_spent"]:,.0f}</div><div class="kpi-label">Actual Costs</div></div>', unsafe_allow_html=True)
            st.markdown('<div style="height:15px"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-card" style="border-left-color: {COLORS["status_active"]};"><div class="kpi-value">R {m["remaining"]:,.0f}</div><div class="kpi-label">Remaining</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)

    # --- ROW 2: FINANCIALS & COST BREAKDOWN ---
    r2_col1, r2_col2 = st.columns([1, 1])
    
    with r2_col1:
        col_fin_h, col_fin_b = st.columns([3, 1])
        with col_fin_h: st.markdown("### Financials")
        with col_fin_b: 
            if st.button("Full View", key="btn_full_fin", use_container_width=True): show_full_financials(project_id)

        fin_fig = go.Figure()
        # Using Financial palette (distinguished from categories)
        fin_items = [
            ('Forecast', m['forecast'], COLORS['fin_forecast']), 
            ('Actual', m['total_spent'], COLORS['fin_actual']), 
            ('Budget', m['total_budget'], COLORS['fin_budget'])
        ]
        max_v = max(m['total_budget'], m['forecast']) * 1.1 if max(m['total_budget'], m['forecast']) > 0 else 1000
        
        for i, (label, val, color) in enumerate(fin_items):
            fin_fig.add_trace(go.Bar(
                x=[val], y=[label], orientation='h', 
                marker=dict(color=color, cornerradius=4),
                text=[f"R {val:,.0f}"], textposition="auto", 
                textfont=dict(color='white', size=11),
                hovertemplate=f"<b>{label}</b>: R %{{x:,.0f}}<extra></extra>"
            ))
        
        fin_fig.update_layout(
            xaxis=dict(visible=False, range=[0, max_v*1.2]), 
            yaxis=dict(showgrid=False, tickfont=dict(family="Segoe UI", size=12)),
            margin=dict(l=0, r=0, t=0, b=0), 
            height=200, 
            paper_bgcolor='rgba(0,0,0,0)', 
            showlegend=False, 
            bargap=0.3
        )
        st.plotly_chart(fin_fig, use_container_width=True, config={'displayModeBar': False})

    with r2_col2:
        st.markdown("### Cost Breakdown")
        exp_df = database.get_df("SELECT category, SUM(amount) as total FROM expenditure_log WHERE project_id = ? GROUP BY category", (project_id,))
        if not exp_df.empty:
            # Using Cost Category palette (no-overlap with financials)
            cost_fig = px.pie(exp_df, values='total', names='category', hole=0.7,
                             color='category',
                             color_discrete_map={
                                'Labour': COLORS['cat_labour'],
                                'Material': COLORS['cat_material'],
                                'Vehicle': COLORS['cat_vehicle'],
                                'Diesel': COLORS['cat_diesel'],
                                'Other': COLORS['cat_other']
                             })
            cost_fig.update_traces(textinfo='none')
            cost_fig.update_layout(
                showlegend=True, 
                legend=dict(orientation="h", y=-0.1), 
                margin=dict(l=0, r=0, t=10, b=0), 
                height=240,
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(cost_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No expenditure recorded.")

    st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)

    # Fetch Activities for Timeline & Milestones
    all_activities = database.get_df('''
        SELECT *, 
               (CASE WHEN status = 'Complete' THEN 'Complete' 
                     WHEN status = 'Active' THEN 'Active' 
                     ELSE 'Not Started' END) as status_mapped,
               (CASE WHEN status = 'Complete' THEN 1 ELSE 0 END) as is_finished,
               (CASE WHEN status IN ('Active', 'Complete') THEN 1 ELSE 0 END) as is_started
        FROM baseline_schedule WHERE project_id = ? ORDER BY planned_start
    ''', (project_id,))

    # --- ROW 3: TIMELINE & MILESTONES ---
    r3_col1, r3_col2 = st.columns([1, 1])

    with r3_col1:
        col_tl_h, col_tl_b = st.columns([3, 1])
        with col_tl_h: st.markdown("### Project Timeline")
        with col_tl_b:
            if st.button("View Details", key="btn_full_tl", use_container_width=True): show_full_timeline(project_id, all_activities)
        
        if not all_activities.empty:
            dash_filter = all_activities[all_activities['status_mapped'].isin(['Active', 'Not Started'])]
            dash_filter['planned_start'] = pd.to_datetime(dash_filter['planned_start'])
            dash_view = dash_filter.sort_values('planned_start', ascending=False).tail(4) 
            dash_view = dash_view.sort_values('planned_start', ascending=False)
            
            tl_fig = px.timeline(dash_view, x_start="planned_start", x_end="planned_finish", y="activity_name",
                                color="status_mapped", 
                                color_discrete_map={
                                    'Not Started': COLORS['status_not_started'], 
                                    'Active': COLORS['status_active'],
                                    'Complete': COLORS['status_complete']
                                },
                                category_orders={"status_mapped": ["Not Started", "Active", "Complete"]})
            
            tl_fig.update_yaxes(title="") 
            tl_fig.update_xaxes(title="", visible=False)
            tl_fig.update_layout(
                showlegend=False, 
                height=220, 
                margin=dict(l=0, r=0, t=10, b=0),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(tl_fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("No activities defined.")

    with r3_col2:
        col_ms_h, col_ms_b = st.columns([3, 1])
        with col_ms_h: st.markdown("### Major Milestones")
        
        if not all_activities.empty:
            milestones = all_activities.sort_values('planned_start')
            with col_ms_b:
                if st.button("All Stages", key="btn_full_ms", use_container_width=True): show_full_milestones(milestones)
            
            # Show top 4 in a unified container to avoid visual glitches
            ms_html = '<div style="background-color: white; padding: 15px; border-radius: 12px; border: 1px solid #eee; box-shadow: 0 2px 5px rgba(0,0,0,0.02); min-height: 220px;">'
            for _, row in milestones.head(4).iterrows():
                status_label = row['status_mapped']
                status_color = COLORS['status_complete'] if status_label == 'Complete' else (COLORS['status_active'] if status_label == 'Active' else COLORS['status_not_started'])
                icon = "✓" if status_label == 'Complete' else ("▶" if status_label == 'Active' else "○")
                
                ms_html += f'<div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f0f0f0; padding:12px 0;"><span style="font-weight:500; font-size:0.9rem; color:{COLORS["text"]};">{row["activity_name"]}</span><div style="text-align:right;"><span style="display:block; font-size:0.75rem; color:{COLORS["subtext"]};">{row["planned_finish"]}</span><span style="display:block; font-size:0.8rem; color:{status_color}; font-weight:600;">{icon} {status_label}</span></div></div>'
            ms_html += '</div>'
            st.markdown(ms_html, unsafe_allow_html=True)
        else:
            st.info("No milestones defined.")

if __name__ == "__main__":
    pm_dashboard()
