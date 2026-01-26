import streamlit as st
import auth
import database
import calculations
import pandas as pd
import styles

# Page Config
st.set_page_config(page_title="PM Tool - Executive Dashboard", layout="wide")

def exec_dashboard():
    auth.require_role(['executive', 'admin'])
    current_user = auth.get_current_user()
    
    # Apply Global Styles
    styles.global_css()
    
    # --- CUSTOM CSS INJECTION ---
    st.markdown("""
    <style>
        .exec-header {
            background: linear-gradient(90deg, #2c5aa0 0%, #5fa2e8 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .exec-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            letter-spacing: -1px;
        }
        .exec-subtitle {
            font-size: 1rem;
            opacity: 0.9;
            margin-top: 0.5rem;
        }
        
        /* Metric Cards */
        .metric-container {
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #eee;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            text-align: center;
        }
        .metric-label { font-size: 0.9rem; color: #666; text-transform: uppercase; letter-spacing: 0.5px; }
        .metric-value { font-size: 2rem; font-weight: 700; color: #2c5aa0; margin: 0.5rem 0; }
        .metric-delta { font-size: 0.9rem; font-weight: 600; }
        .positive { color: #4caf50; }
        .negative { color: #f44336; }
        
        /* Project Card Overrides */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {
            border: none !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: transform 0.2s ease;
        }
        div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="exec-header">
        <div class="exec-title">Executive Portfolio Dashboard</div>
        <div class="exec-subtitle">Real-time overview of all active projects and financial performance</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 1. Summary Metrics
    summary = calculations.get_all_projects_summary()
    
    if summary.empty:
        st.info("No projects found in the system.")
        st.stop()
        
    # Custom Metric Layout
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Active Projects</div>
            <div class="metric-value">{len(summary)}</div>
        </div>
        """, unsafe_allow_html=True)

    with m2:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Total Portfolio Value</div>
            <div class="metric-value">R {summary['total_budget'].sum()/1e6:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)

    with m3:
        forecast_total = summary['forecast'].sum()
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Forecast Cost</div>
            <div class="metric-value">R {forecast_total/1e6:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)

    with m4:
        total_budget = summary['total_budget'].sum()
        margin = ((total_budget - forecast_total) / total_budget * 100) if total_budget > 0 else 0
        delta_class = "positive" if margin > 0 else "negative"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-label">Net Margin</div>
            <div class="metric-value {delta_class}">{margin:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Active Projects")
    
    # 2. Project Cards
    cols = st.columns(3)
    for i, (_, project) in enumerate(summary.iterrows()):
        with cols[i % 3]:
            # Using standard Streamlit container but styled via CSS above
            with st.container(border=True):
                st.markdown(f"#### {project['project_name']}")
                st.caption(f"Ref: {project['project_number']}")
                
                # Progress Bar
                st.progress(project['pct_complete'] / 100)
                st.caption(f"Progress: {project['pct_complete']:.1f}%")
                
                # Status Tags
                # Aligning with new PM Dashboard standards
                b_status = project['budget_health']
                s_status = project['schedule_health']
                
                b_color = '#4caf50' if b_status == 'Green' else ('#ffc107' if b_status == 'Yellow' else '#f44336')
                s_color = '#4caf50' if s_status == 'Green' else '#ffc107'
                
                st.markdown(f"""
                <div style="display:flex; gap:8px; margin: 10px 0;">
                    <span style="background-color:{b_color}; padding:4px 8px; border-radius:12px; color:white; font-size:10px; font-weight:bold;">BUDGET</span>
                    <span style="background-color:{s_color}; padding:4px 8px; border-radius:12px; color:white; font-size:10px; font-weight:bold;">SCHEDULE</span>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"**Spent:** R {project['total_spent']:,.0f}")
                
                if st.button(f"View Dashboard", key=f"btn_{i}", use_container_width=True):
                    st.session_state['selected_project'] = project['project_number']
                    st.switch_page("pages/2_PM_Dashboard.py")

if __name__ == "__main__":
    exec_dashboard()
