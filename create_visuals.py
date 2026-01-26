"""
Project Status Report - Visual Components Generator
Creates individual chart images for Power BI import
Based on uploaded reference template
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import os
from datetime import datetime

# Output directory for visuals
OUTPUT_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\visuals'
DATA_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data'

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Set professional style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Segoe UI'
plt.rcParams['font.size'] = 10

# Color palette
COLORS = {
    'blue': '#1E88E5',
    'light_blue': '#64B5F6',
    'yellow': '#FFC107',
    'green': '#43A047',
    'red': '#E53935',
    'orange': '#FB8C00',
    'gray': '#9E9E9E',
    'dark': '#212121',
    'white': '#FFFFFF'
}

print("="*60)
print("PROJECT STATUS REPORT - VISUAL GENERATOR")
print("="*60)

# Load available data
try:
    df_kpis = pd.read_csv(os.path.join(DATA_DIR, 'project_kpis.csv'))
    df_costs = pd.read_csv(os.path.join(DATA_DIR, 'cost_breakdown.csv'))
    df_status = pd.read_csv(os.path.join(DATA_DIR, 'project_status.csv'))
    df_labour = pd.read_csv(os.path.join(DATA_DIR, 'labour_all.csv'))
    df_trend = pd.read_csv(os.path.join(DATA_DIR, 'monthly_trend.csv'))
    print("✅ Data loaded successfully")
except Exception as e:
    print(f"⚠️ Error loading data: {e}")

# ============================================================================
# 1. PROJECT HEALTH INDICATORS
# ============================================================================
print("\n📊 Creating: Project Health Indicators...")

fig, ax = plt.subplots(figsize=(8, 2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 2)
ax.axis('off')

# Health categories with status (green=on track, yellow=at risk, red=critical)
health_items = [
    ('Scope', 'green'),
    ('Schedule', 'yellow'),  
    ('Budget', 'green'),
    ('Resources', 'green')
]

x_positions = [1.5, 3.5, 5.5, 7.5]
for i, (label, status) in enumerate(health_items):
    color = COLORS[status]
    circle = plt.Circle((x_positions[i], 1.2), 0.4, color=color, ec='white', linewidth=2)
    ax.add_patch(circle)
    # Add checkmark for green status
    if status == 'green':
        ax.text(x_positions[i], 1.2, '✓', ha='center', va='center', 
                fontsize=16, color='white', fontweight='bold')
    ax.text(x_positions[i], 0.4, label, ha='center', va='center', 
            fontsize=11, fontweight='bold', color=COLORS['dark'])

ax.text(0.1, 1.8, 'Project Health', fontsize=14, fontweight='bold', color=COLORS['dark'])

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '01_project_health.png'), dpi=150, 
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 01_project_health.png")
print("   ℹ️ NOTE: Status colors are placeholder - update based on actual project status")

# ============================================================================
# 2. FINANCIALS TABLE
# ============================================================================
print("\n📊 Creating: Financials Summary...")

# Get financial data
contract_val = df_kpis[df_kpis['KPI_NAME'] == 'Contract Value']['VALUE'].values[0]
total_costs = df_kpis[df_kpis['KPI_NAME'] == 'Total Costs']['VALUE'].values[0]
remaining = df_kpis[df_kpis['KPI_NAME'] == 'Remaining Budget']['VALUE'].values[0]

fig, ax = plt.subplots(figsize=(6, 3))
ax.axis('off')

# Create table data
table_data = [
    ['Budget', f'R {contract_val:,.0f}'],
    ['Actual', f'R {total_costs:,.0f}'],
    ['Forecast', f'R {contract_val:,.0f}']  # Assuming on-budget forecast
]

# Draw bars for visual comparison
bar_width = 0.6
y_positions = [2.2, 1.4, 0.6]
max_val = contract_val

ax.set_xlim(0, 10)
ax.set_ylim(0, 3)

ax.text(0.1, 2.8, 'Financials', fontsize=14, fontweight='bold', color=COLORS['dark'])

for i, (label, value) in enumerate(table_data):
    # Label
    ax.text(0.1, y_positions[i], label, fontsize=11, va='center', color=COLORS['dark'])
    # Value
    ax.text(2.5, y_positions[i], value, fontsize=11, va='center', fontweight='bold', color=COLORS['dark'])
    
    # Bar
    bar_val = [contract_val, total_costs, contract_val][i]
    bar_len = (bar_val / max_val) * 5
    color = [COLORS['blue'], COLORS['yellow'], COLORS['light_blue']][i]
    rect = mpatches.FancyBboxPatch((4, y_positions[i]-0.15), bar_len, 0.3, 
                                     boxstyle="round,pad=0.02", facecolor=color, edgecolor='none')
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '02_financials.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 02_financials.png")

# ============================================================================
# 3. PROJECT SCHEDULE (Progress Bars)
# ============================================================================
print("\n📊 Creating: Project Schedule...")

fig, ax = plt.subplots(figsize=(6, 3))
ax.axis('off')
ax.set_xlim(0, 10)
ax.set_ylim(0, 4)

ax.text(0.1, 3.5, 'Project Schedule', fontsize=14, fontweight='bold', color=COLORS['dark'])

# Schedule items (estimated based on budget utilization of 37%)
schedule_items = [
    ('Complete', 37, COLORS['blue']),
    ('In progress', 25, COLORS['yellow']),
    ('Not started', 38, COLORS['gray'])
]

y_pos = [2.5, 1.7, 0.9]
for i, (label, pct, color) in enumerate(schedule_items):
    ax.text(0.1, y_pos[i], label, fontsize=10, va='center', color=COLORS['dark'])
    
    # Background bar
    bg_rect = mpatches.FancyBboxPatch((2.5, y_pos[i]-0.15), 7, 0.3,
                                       boxstyle="round,pad=0.02", facecolor='#E0E0E0', edgecolor='none')
    ax.add_patch(bg_rect)
    
    # Progress bar
    bar_len = (pct / 100) * 7
    rect = mpatches.FancyBboxPatch((2.5, y_pos[i]-0.15), bar_len, 0.3,
                                    boxstyle="round,pad=0.02", facecolor=color, edgecolor='none')
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '03_project_schedule.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 03_project_schedule.png")
print("   ℹ️ NOTE: Schedule percentages estimated from budget utilization")

# ============================================================================
# 4. COST BREAKDOWN (Pie Chart)
# ============================================================================
print("\n📊 Creating: Cost Breakdown Pie Chart...")

fig, ax = plt.subplots(figsize=(6, 5))

# Get cost data
categories = df_costs['CATEGORY'].tolist()
amounts = df_costs['AMOUNT'].tolist()
colors = [COLORS['blue'], COLORS['green'], COLORS['orange'], COLORS['yellow']]

# Create pie chart
wedges, texts, autotexts = ax.pie(amounts, labels=categories, autopct='%1.1f%%',
                                   colors=colors, startangle=90,
                                   wedgeprops={'edgecolor': 'white', 'linewidth': 2})

ax.set_title('Cost Breakdown', fontsize=14, fontweight='bold', pad=20)

for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '04_cost_breakdown.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 04_cost_breakdown.png")

# ============================================================================
# 5. PROJECT TIMELINE (Gantt-style)
# ============================================================================
print("\n📊 Creating: Project Timeline...")

fig, ax = plt.subplots(figsize=(8, 3))

# Timeline phases (estimated)
phases = [
    ('Phase 1', 0, 60, COLORS['blue'], 'Complete'),
    ('Phase 2', 40, 80, COLORS['yellow'], 'In Progress')
]

ax.set_xlim(0, 100)
ax.set_ylim(0, len(phases) + 1)

ax.text(0, len(phases) + 0.5, 'Project Timeline', fontsize=14, fontweight='bold', color=COLORS['dark'])

for i, (label, start, end, color, status) in enumerate(phases):
    y = len(phases) - i - 0.5
    
    # Phase bar
    rect = mpatches.FancyBboxPatch((start, y - 0.2), end - start, 0.4,
                                    boxstyle="round,pad=0.02", facecolor=color, edgecolor='none')
    ax.add_patch(rect)
    
    # Label
    ax.text(start - 2, y, label, fontsize=10, va='center', ha='right', color=COLORS['dark'])
    ax.text((start + end) / 2, y, status, fontsize=9, va='center', ha='center', color='white', fontweight='bold')

# Quarter labels
ax.set_xticks([0, 25, 50, 75, 100])
ax.set_xticklabels(['Start', 'Q1', 'Q2', 'Q3', 'Q4'])
ax.set_yticks([])
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '05_timeline.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 05_timeline.png")
print("   ℹ️ NOTE: Timeline phases estimated - update with actual project milestones")

# ============================================================================
# 6. MONTHLY LABOUR TREND (Line Chart)
# ============================================================================
print("\n📊 Creating: Monthly Labour Trend...")

fig, ax = plt.subplots(figsize=(6, 4))

months = df_trend['MONTH'].tolist()
costs = df_trend['LABOUR_COST'].tolist()

ax.plot(months, costs, marker='o', linewidth=2, markersize=8, color=COLORS['blue'])
ax.fill_between(months, costs, alpha=0.3, color=COLORS['blue'])

ax.set_title('Monthly Labour Cost Trend', fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('Cost (ZAR)', fontsize=11)

# Add value labels
for i, (m, c) in enumerate(zip(months, costs)):
    ax.annotate(f'R{c:,.0f}', (m, c), textcoords="offset points", 
                xytext=(0, 10), ha='center', fontsize=9)

ax.set_ylim(0, max(costs) * 1.3)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '06_monthly_trend.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 06_monthly_trend.png")

# ============================================================================
# 7. KPI CARDS
# ============================================================================
print("\n📊 Creating: KPI Cards...")

fig, axes = plt.subplots(1, 4, figsize=(14, 2.5))

kpis = [
    ('Contract Value', f'R {contract_val:,.0f}', COLORS['blue']),
    ('Actual Costs', f'R {total_costs:,.0f}', COLORS['orange']),
    ('Remaining', f'R {remaining:,.0f}', COLORS['green']),
    ('Budget Used', f'{(total_costs/contract_val*100):.1f}%', COLORS['yellow'])
]

for ax, (title, value, color) in zip(axes, kpis):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Background card
    rect = mpatches.FancyBboxPatch((0.5, 0.5), 9, 9,
                                    boxstyle="round,pad=0.1", 
                                    facecolor=color, edgecolor='none', alpha=0.9)
    ax.add_patch(rect)
    
    # Text
    ax.text(5, 6, value, ha='center', va='center', fontsize=18, 
            fontweight='bold', color='white')
    ax.text(5, 3, title, ha='center', va='center', fontsize=11, color='white')

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, '07_kpi_cards.png'), dpi=150,
            bbox_inches='tight', facecolor='white', edgecolor='none')
plt.close()
print("   ✅ 07_kpi_cards.png")

# ============================================================================
# 8. MAJOR MILESTONES TABLE (Save as CSV for Power BI table visual)
# ============================================================================
print("\n📊 Creating: Major Milestones Data...")

# NOTE: This data is MISSING from the source file
milestones_data = pd.DataFrame([
    {'Milestone': 'Project Kickoff', 'Target_Date': '2025-01-15', 'Status': 'Complete'},
    {'Milestone': 'Phase 1 Start', 'Target_Date': '2025-01-20', 'Status': 'Complete'},
    {'Milestone': 'Phase 1 Completion', 'Target_Date': '2025-02-28', 'Status': 'In Progress'},
    {'Milestone': 'Phase 2 Start', 'Target_Date': '2025-03-01', 'Status': 'Not Started'},
    {'Milestone': 'Final Completion', 'Target_Date': '2025-04-30', 'Status': 'Not Started'}
])

milestones_data.to_csv(os.path.join(DATA_DIR, 'milestones.csv'), index=False)
print("   ✅ milestones.csv (data file)")
print("   ⚠️ NOTE: Milestone dates are ESTIMATED - update with actual project milestones")

# ============================================================================
# 9. KEY RISKS & ISSUES (Save as CSV)
# ============================================================================
print("\n📊 Creating: Key Risks & Issues Data...")

# NOTE: This data is MISSING from the source file
risks_data = pd.DataFrame([
    {'Risk_Issue': 'Resource constraint affecting timeline', 'Priority': 'High', 'Status': 'Open'},
    {'Risk_Issue': 'Dependency on third party vendor', 'Priority': 'Medium', 'Status': 'Open'},
    {'Risk_Issue': 'Scope creep identified in phase 2', 'Priority': 'High', 'Status': 'Monitoring'}
])

risks_data.to_csv(os.path.join(DATA_DIR, 'risks_issues.csv'), index=False)
print("   ✅ risks_issues.csv (data file)")
print("   ⚠️ NOTE: Risks are PLACEHOLDER - update with actual project risks")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*60)
print("✅ VISUAL GENERATION COMPLETE")
print("="*60)

print(f"\n📁 Visuals saved to: {OUTPUT_DIR}")
print("\n📊 Created 7 image files:")
print("   1. 01_project_health.png - Status indicators")
print("   2. 02_financials.png - Budget/Actual/Forecast bars")
print("   3. 03_project_schedule.png - Progress bars")
print("   4. 04_cost_breakdown.png - Pie chart")
print("   5. 05_timeline.png - Gantt timeline")
print("   6. 06_monthly_trend.png - Line chart")
print("   7. 07_kpi_cards.png - KPI summary cards")

print("\n📄 Created 2 additional data files:")
print("   - milestones.csv")
print("   - risks_issues.csv")

print("\n" + "="*60)
print("⚠️ MISSING DATA (needs manual input):")
print("="*60)
print("""
The following data was NOT in the original Excel file and has been
estimated or left as placeholders:

1. PROJECT HEALTH STATUS
   - Scope/Schedule/Budget/Resources colors
   - Need: Actual status from project manager

2. MAJOR MILESTONES  
   - Need: Actual milestone dates and names

3. KEY RISKS & ISSUES
   - Need: Actual project risks from risk register

4. PROJECT TIMELINE PHASES
   - Need: Actual phase start/end dates

5. SCHEDULE PERCENTAGES
   - Complete/In Progress/Not Started
   - Currently estimated from budget utilization (37%)
""")
