"""
Project Status Dashboard - Streamlit Application
Replicates the visual style of the reference Project Status Report
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import os

# Page Config
st.set_page_config(
    page_title="Project Status Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CONFIGURATION ---
DATA_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data'

# Brand Colors (from reference)
COLORS = {
    'blue_header': '#2c5aa0',
    'blue_bar': '#5fa2e8',
    'blue_bg': '#e6f0fa',
    'green': '#4caf50',
    'yellow': '#ffc107',
    'red': '#f44336',
    'text': '#333333',
    'subtext': '#666666',
    'card_bg': '#ffffff'
}

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Global Font & Theme Enforcement */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        color: #333333 !important;
        background-color: #ffffff !important;
    }
    
    /* Main Streamlit container background */
    .stApp {
        background-color: #ffffff !important;
    }
    
    /* Header Styling */
    .report-header {
        background-color: #2c5aa0;
        color: white !important;
        padding: 2rem;
        border-radius: 5px;
        margin-bottom: 2rem;
    }
    .report-title {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        color: white !important;
    }
    .report-date {
        font-size: 1rem;
        opacity: 0.8;
        color: white !important;
    }
    
    /* Section Headers */
    h3 {
        font-size: 1.2rem;
        font-weight: bold;
        color: #333333 !important;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* KPI Cards */
    .kpi-card {
        background-color: #f8f9fa;
        border-left: 4px solid #2c5aa0;
        padding: 1rem;
        border-radius: 4px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        text-align: center;
    }
    .kpi-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c5aa0 !important;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #666666 !important;
    }
    
    /* Remove streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_data():
    try:
        kpis = pd.read_csv(os.path.join(DATA_DIR, 'project_kpis.csv'))
        costs = pd.read_csv(os.path.join(DATA_DIR, 'cost_breakdown.csv'))
        status = pd.read_csv(os.path.join(DATA_DIR, 'project_status.csv'))
        return kpis, costs, status
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None, None

kpis, costs, status_df = load_data()

# Process Data
budget = 240100.82
actual = 89033.86
if kpis is not None:
    try:
        budget = float(kpis[kpis['KPI_NAME'] == 'Contract Value']['VALUE'].values[0])
        actual = float(kpis[kpis['KPI_NAME'] == 'Total Costs']['VALUE'].values[0])
    except:
        pass
forecast = budget 

pct_complete = min((actual / budget) * 100, 100)
pct_progress = 30 
pct_not_started = max(100 - pct_complete - pct_progress, 0)


# --- LAYOUT ---

# 1. HEADER
st.markdown(f"""
<div class="report-header">
    <div class="report-title">PROJECT STATUS REPORT</div>
    <div class="report-date">Liberty Towers Fibre Relocation | {pd.Timestamp.now().strftime('%B %d, %Y')}</div>
</div>
""", unsafe_allow_html=True)

# 2. EXECUTIVE SUMMARY & HEALTH
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### Executive Summary")
    st.markdown(f"""
    <div style="background-color: white; color: #333333; padding: 15px; border-radius: 5px; border: 1px solid #eee;">
    The Liberty Towers Fibre Relocation project is currently in <b>Phase 1</b>. 
    Labour and material procurement are proceeding according to schedule. 
    Budget utilization is at <b>{pct_complete:.1f}%</b> with no major risks identified.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### Project Health")
    
    # Create Health Indicators Plotly Chart
    health_fig = go.Figure()
    
    items = [
        ('Resources', 'green', 8),
        ('Budget', 'green', 6), 
        ('Schedule', 'yellow', 4),
        ('Scope', 'green', 2)
    ]
    
    for label, color, x_pos in items:
        c_hex = COLORS[color]
        
        # Circle
        health_fig.add_shape(type="circle",
            x0=x_pos-0.8, y0=0.2, x1=x_pos+0.8, y1=1.8,
            line=dict(color=c_hex, width=2),
            fillcolor=c_hex if color == 'green' else 'white',
        )
        
        # Checkmark or Inner Circle
        if color == 'green':
            health_fig.add_annotation(x=x_pos, y=1, text="✓", 
                showarrow=False, font=dict(color="white", size=24))
        else:
            # Inner circle for yellow/red
            health_fig.add_shape(type="circle",
                x0=x_pos-0.5, y0=0.5, x1=x_pos+0.5, y1=1.5,
                line=dict(color="white"), fillcolor="white"
            )

        # Label
        health_fig.add_annotation(x=x_pos, y=-0.5, text=label, 
            showarrow=False, font=dict(color="#666", size=12))

    health_fig.update_layout(
        xaxis=dict(range=[0, 10], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[-1, 2.5], showgrid=False, zeroline=False, visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=100,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(health_fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("---")

# 3. MAIN CONTENT GRID
grid_col1, grid_col2 = st.columns([1, 1])

with grid_col1:
    # --- PROJECT SCHEDULE (Progress Bars) ---
    st.markdown("### Project Schedule")
    
    sched_fig = go.Figure()
    
    stages = [
        ('Not started', pct_not_started, COLORS['blue_bar']), 
        ('In progress', pct_progress, COLORS['blue_bar']),
        ('Complete', pct_complete, COLORS['blue_header'])
    ]
    
    y_pos = 0
    for label, val, color in stages:
        # Background bar
        sched_fig.add_shape(type="rect",
            x0=0, y0=y_pos, x1=100, y1=y_pos+0.6,
            line=dict(width=0), fillcolor="#f0f0f0", layer='below'
        )
        # Value bar (Interactivity added via invisible scatter trace on top)
        sched_fig.add_shape(type="rect",
            x0=0, y0=y_pos, x1=val, y1=y_pos+0.6,
            line=dict(width=0), fillcolor=color, layer='above'
        )
        
        # Interactive Trace
        sched_fig.add_trace(go.Bar(
            x=[val], y=[y_pos+0.3], orientation='h',
            marker=dict(color='rgba(0,0,0,0)'), # Invisible
            hoverinfo='text',
            hovertext=f"{label}: {val:.1f}%",
            showlegend=False
        ))
        
        # Label
        sched_fig.add_annotation(x=-5, y=y_pos+0.3, text=label, 
            xanchor="right", showarrow=False, font=dict(color="#333", size=12))
            
        y_pos += 1.2

    sched_fig.update_layout(
        xaxis=dict(range=[-25, 100], showgrid=False, visible=False),
        yaxis=dict(range=[-0.5, 4], showgrid=False, visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    st.plotly_chart(sched_fig, use_container_width=True, config={'displayModeBar': False})

    # --- FINANCIALS ---
    st.markdown("### Financials")
    
    fin_fig = go.Figure()
    
    fin_items = [
        ('Forecast', forecast, COLORS['blue_bar']),
        ('Actual', actual, COLORS['blue_bar']),
        ('Budget', budget, COLORS['blue_header'])
    ]
    
    max_val = max(budget, forecast) * 1.2
    y_pos = 0
    
    for label, val, color in fin_items:
        # Bar with hover
        fin_fig.add_trace(go.Bar(
            x=[val], y=[label], orientation='h',
            marker=dict(color=color, cornerradius=5),
            text=[f"R {val:,.0f}"], textposition="outside",
            textfont=dict(color='#333', size=12),
            hovertemplate=f"<b>{label}</b><br>Amount: R %{{x:,.2f}}<extra></extra>"
        ))
    
    fin_fig.update_layout(
        xaxis=dict(showgrid=False, visible=False, range=[0, max_val*1.3]),
        yaxis=dict(showgrid=False, tickfont=dict(size=12, color='#333')),
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        bargap=0.4
    )
    st.plotly_chart(fin_fig, use_container_width=True, config={'displayModeBar': False})
    
    # --- TIMELINE ---
    st.markdown("### Project Timeline")
    
    tl_fig = go.Figure()
    
    # Q1 Bar (Interactive)
    tl_fig.add_trace(go.Scatter(
        x=[2.25], y=[2.3], mode='text', text=['Q1 Phase 1'], textfont=dict(color='white'),
        hoverinfo='text', hovertext='Phase 1: Jan - Feb 2025'
    ))
    tl_fig.add_shape(type="rect",
        x0=0.5, y0=2, x1=4, y1=2.6,
        line=dict(width=0), fillcolor=COLORS['blue_header'], layer="below"
    )

    # Phase 2 Bar (Interactive)
    tl_fig.add_trace(go.Scatter(
        x=[5], y=[1.3], mode='text', text=['Phase 2'], textfont=dict(color='white'),
        hoverinfo='text', hovertext='Phase 2: Mar - Apr 2025'
    ))
    tl_fig.add_shape(type="rect",
        x0=3.5, y0=1, x1=6.5, y1=1.6,
        line=dict(width=0), fillcolor=COLORS['yellow'], layer="below"
    )

    # Headers
    tl_fig.add_annotation(x=2, y=3, text="Q1", showarrow=False, font=dict(color="#666"))
    tl_fig.add_annotation(x=5, y=3, text="Q2", showarrow=False, font=dict(color="#666"))
    tl_fig.add_annotation(x=8, y=3, text="Q3", showarrow=False, font=dict(color="#666"))
    
    tl_fig.update_layout(
        xaxis=dict(range=[0, 10], showgrid=False, visible=False),
        yaxis=dict(range=[0, 3.5], showgrid=False, visible=False),
        margin=dict(l=0, r=0, t=0, b=0),
        height=150,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )
    st.plotly_chart(tl_fig, use_container_width=True, config={'displayModeBar': False})


with grid_col2:
    # --- KPI CARDS (Right Column) ---
    st.markdown("### Key Metrics")
    
    kpi_col1, kpi_col2 = st.columns(2)
    
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-value">R {budget:,.0f}</div>
            <div class="kpi-label">Contract Value</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ffc107;">
            <div class="kpi-value">{pct_complete:.1f}%</div>
            <div class="kpi-label">Budget Used</div>
        </div>
        """, unsafe_allow_html=True)
        
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #5fa2e8;">
            <div class="kpi-value">R {actual:,.0f}</div>
            <div class="kpi-label">Total Costs</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #4caf50;">
            <div class="kpi-value">R {budget-actual:,.0f}</div>
            <div class="kpi-label">Remaining</div>
        </div>
        """, unsafe_allow_html=True)

    # --- COST BREAKDOWN ---
    st.markdown("### Cost Breakdown")
    
    if costs is not None:
        cost_fig = px.pie(costs, values='AMOUNT', names='CATEGORY', hole=0.6,
                         color_discrete_sequence=[COLORS['blue_header'], COLORS['green'], COLORS['yellow'], COLORS['blue_bar']])
        cost_fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
            margin=dict(l=0, r=0, t=0, b=0),
            height=200
        )
        st.plotly_chart(cost_fig, use_container_width=True)

    # --- MILESTONES ---
    st.markdown("### Major Milestones")
    
    milestones = [
        ("Kickoff", "Feb 10, 2025", "Complete", "black"),
        ("Beta Release", "May 8, 2025", "On Track", "green"),
        ("Project Completion", "Jun 20, 2025", "At Risk", "red")
    ]
    
    for name, date, status, color in milestones:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; border-bottom:1px solid #eee; padding:5px 0;">
            <span style="font-weight:bold;">{name}</span>
            <span style="color:#666;">{date}</span>
            <span style="color:{color}; font-weight:bold;">{status}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Generated by Dashboard AI")
