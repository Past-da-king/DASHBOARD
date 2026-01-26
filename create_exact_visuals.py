"""
Exact Visuals Generator - Matching Reference Image Style
Final Polish - Fixed Aspect Ratios, Fonts, and Layouts
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

OUTPUT_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\visuals_exact'
DATA_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Exact colors from the reference image
COLORS = {
    'blue_dark': '#2c5aa0',   # Dark blue header/bars
    'blue_light': '#5fa2e8',  # Light blue bars
    'blue_bg': '#e6f0fa',     # Very light blue background bars
    'green': '#4caf50',       # Success green
    'yellow': '#ffc107',      # Warning yellow
    'red': '#f44336',         # Risk red
    'text': '#333333',        # Text dark grey
    'subtext': '#666666',     # Lighter text
    'bg_bar': '#f0f0f0'       # Light grey for empty bar backgrounds
}

# Use san-serif default
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Segoe UI', 'sans-serif']

def load_data():
    try:
        kpis = pd.read_csv(os.path.join(DATA_DIR, 'project_kpis.csv'))
        costs = pd.read_csv(os.path.join(DATA_DIR, 'cost_breakdown.csv'))
        return kpis, costs
    except:
        return None, None

kpis, costs = load_data()

# Extract values or use defaults
budget = 240100.82
actual = 89033.86
if kpis is not None:
    try:
        budget = float(kpis[kpis['KPI_NAME'] == 'Contract Value']['VALUE'].values[0])
        actual = float(kpis[kpis['KPI_NAME'] == 'Total Costs']['VALUE'].values[0])
    except:
        pass
forecast = budget 

# Percentage for schedule
pct_complete = (actual / budget) * 100
pct_progress = 30
pct_not_started = 100 - pct_complete - pct_progress
if pct_not_started < 0: pct_not_started = 0

# ============================================================================
# 1. PROJECT HEALTH
# ============================================================================
def create_project_health():
    # Force fixed size to maintain aspect ratio
    fig = plt.figure(figsize=(8, 3))
    ax = fig.add_axes([0, 0, 1, 1]) # Use full figure
    ax.axis('off')
    
    # Force 1:1 aspect ratio for coordinate system to ensure circles are circles
    ax.set_aspect('equal')
    
    # Set limits explicitly
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3) # Height 3 matches width 10 roughly with figsize 8x3
    
    # Title
    ax.text(0.5, 2.5, 'Project Health', fontsize=14, fontweight='bold', color=COLORS['text'])
    
    items = [
        ('Scope', 'green'),
        ('Schedule', 'yellow'), 
        ('Budget', 'green'),
        ('Resources', 'green')
    ]
    
    # Centers for circles
    centers_x = [2.0, 4.0, 6.0, 8.0]
    y_center = 1.6
    radius = 0.6
    
    for i, (label, status) in enumerate(items):
        x = centers_x[i]
        color = COLORS[status]
        
        if status == 'green':
            # Solid green circle
            circle = mpatches.Circle((x, y_center), radius, color=color, zorder=2)
            ax.add_patch(circle)
            # Checkmark
            ax.text(x, y_center-0.05, '✓', color='white', ha='center', va='center', 
                   fontsize=20, fontweight='bold', fontname='Arial', zorder=3)
        else:
            # Ring (Wedge)
            # Outer wedge
            wedge = mpatches.Wedge((x, y_center), radius, 0, 360, width=0.15, color=color, zorder=2)
            ax.add_patch(wedge)
            
        # Label below
        ax.text(x, y_center - 0.9, label, ha='center', va='top', fontsize=11, color=COLORS['subtext'])
        
    plt.savefig(os.path.join(OUTPUT_DIR, 'project_health.png'), dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# ============================================================================
# 2. PROJECT SCHEDULE
# ============================================================================
def create_project_schedule():
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    
    ax.text(0.5, 4.5, 'Project Schedule', fontsize=14, fontweight='bold', color=COLORS['text'])
    
    items = [
        ('Complete', pct_complete/100, COLORS['blue_dark']),
        ('In progress', pct_progress/100, COLORS['blue_light']),
        ('Not started', pct_not_started/100, COLORS['blue_light'])
    ]
    
    start_y = 3.5
    gap = 1.2
    bar_x = 3.5
    bar_width = 6.0
    bar_height = 0.5
    
    for i, (label, pct, color) in enumerate(items):
        y = start_y - (i * gap)
        
        # Label
        ax.text(0.5, y + bar_height/2, label, fontsize=11, color='black', va='center')
        
        # Background Bar
        bg_bar = mpatches.FancyBboxPatch((bar_x, y), bar_width, bar_height, 
                                       boxstyle="round,pad=0.02", 
                                       facecolor=COLORS['bg_bar'], edgecolor='none')
        ax.add_patch(bg_bar)
        
        # Fill Bar
        if pct > 0:
            fill_w = bar_width * pct
            fill_bar = mpatches.FancyBboxPatch((bar_x, y), fill_w, bar_height, 
                                             boxstyle="round,pad=0.02", 
                                             facecolor=color, edgecolor='none')
            ax.add_patch(fill_bar)
            
    plt.savefig(os.path.join(OUTPUT_DIR, 'project_schedule.png'), dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# ============================================================================
# 3. FINANCIALS
# ============================================================================
def create_financials():
    fig = plt.figure(figsize=(6, 4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    
    ax.text(0.5, 4.5, 'Financials', fontsize=14, fontweight='bold', color=COLORS['text'])
    
    data = [
        ('Budget', budget, COLORS['blue_dark']),
        ('Actual', actual, COLORS['blue_light']),
        ('Forecast', forecast, COLORS['blue_light'])
    ]
    
    start_y = 3.5
    gap = 1.2
    max_val = max(budget, forecast) * 1.15
    bar_width_max = 9.0
    
    for i, (label, val, color) in enumerate(data):
        y = start_y - (i * gap)
        
        # Row Labels and Value
        ax.text(0.5, y + 0.4, label, fontsize=11, color='black', va='bottom')
        val_str = f"R {val:,.0f}"
        ax.text(9.5, y + 0.4, val_str, fontsize=11, color='black', va='bottom', ha='right')
        
        # Bar
        bar_w = (val / max_val) * bar_width_max
        bar = mpatches.FancyBboxPatch((0.5, y), bar_w, 0.25, 
                                    boxstyle="round,pad=0.01", 
                                    facecolor=color, edgecolor='none')
        ax.add_patch(bar)
        
    plt.savefig(os.path.join(OUTPUT_DIR, 'financials.png'), dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

# ============================================================================
# 4. PROJECT TIMELINE
# ============================================================================
def create_project_timeline():
    fig = plt.figure(figsize=(8, 4.5))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    
    ax.text(0.5, 5.5, 'Project Timeline', fontsize=14, fontweight='bold', color=COLORS['text'])
    
    # Column headers - Q1, Q2, Q3 aligned with grid
    # Grid x coords: 0.5 start, 3.5, 6.5, 9.5 end
    # Q1 center: 2.0
    # Q2 center: 5.0
    # Q3 center: 8.0
    
    # Headers
    y_header = 4.8
    ax.text(2.0, y_header, 'Q1', fontsize=11, color=COLORS['subtext'], ha='center')
    ax.text(5.0, y_header, 'Q2', fontsize=11, color=COLORS['subtext'], ha='center')
    ax.text(8.0, y_header, 'Q3', fontsize=11, color=COLORS['subtext'], ha='center')
    
    # Task Rows
    # Row 1: Q1 bar
    y_row1 = 4.0
    ax.text(0.5, y_row1 + 0.15, 'Q1', fontsize=10, color=COLORS['subtext'], va='center')
    
    # Bar spans Q1 (0.5 to 3.5) plus a bit of Q2
    bar1 = mpatches.FancyBboxPatch((1.2, y_row1), 3.5, 0.4, 
                                 boxstyle="round,pad=0.02", facecolor=COLORS['blue_dark'], edgecolor='none')
    ax.add_patch(bar1)
    
    # Row 2: Phase 1 & 2
    y_row2 = 3.0
    ax.text(0.5, y_row2 + 0.15, 'Q2', fontsize=10, color=COLORS['subtext'], va='center')
    
    bar2 = mpatches.FancyBboxPatch((1.2, y_row2), 1.5, 0.4, 
                                 boxstyle="round,pad=0.02", facecolor=COLORS['blue_light'], edgecolor='none')
    ax.add_patch(bar2) # Phase 1 tail
    ax.text(1.95, y_row2+0.2, 'Phase 1', color='white', fontsize=8, ha='center', va='center')
    
    bar3 = mpatches.FancyBboxPatch((2.9, y_row2), 3.0, 0.4, 
                                 boxstyle="round,pad=0.02", facecolor=COLORS['yellow'], edgecolor='none')
    ax.add_patch(bar3) # Phase 2
    ax.text(4.4, y_row2+0.2, 'Phase 2', color='white', fontsize=8, ha='center', va='center')

    # Bottom Timeline Section
    y_bottom = 0.5
    bar_h = 0.6
    
    # Month Labels
    ax.text(0.5, 1.5, 'Mar', ha='center', fontsize=10)
    ax.text(5.0, 1.5, 'Phase 2', ha='center', fontsize=10)
    ax.text(9.5, 1.5, 'Q2', ha='center', fontsize=10)
    
    # Bottom Bars
    # Blue [Q1]
    b1 = mpatches.FancyBboxPatch((0.5, 0.5), 2.5, 0.6, boxstyle="round,pad=0", facecolor=COLORS['blue_light'])
    ax.add_patch(b1)
    ax.text(1.75, 0.8, 'Q1', color='white', fontweight='bold', ha='center', va='center')
    
    # Yellow [Phase]
    b2 = mpatches.FancyBboxPatch((3.1, 0.5), 4.5, 0.6, boxstyle="round,pad=0", facecolor=COLORS['yellow'])
    ax.add_patch(b2)
    
    # Red [End]
    b3 = mpatches.FancyBboxPatch((7.7, 0.5), 1.8, 0.6, boxstyle="round,pad=0", facecolor=COLORS['red'])
    ax.add_patch(b3)

    plt.savefig(os.path.join(OUTPUT_DIR, 'project_timeline.png'), dpi=150, bbox_inches='tight', pad_inches=0.1)
    plt.close()

if __name__ == "__main__":
    create_project_health()
    create_project_schedule()
    create_financials()
    create_project_timeline()
    print("Visuals created in:", OUTPUT_DIR)
