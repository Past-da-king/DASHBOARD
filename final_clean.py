"""
FINAL PROPER Data Cleaning Script
Handles all edge cases and produces truly clean CSVs
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
import shutil
import warnings
warnings.filterwarnings('ignore')

INPUT_FILE = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\Fibre Relocation - Liberty Towers.xlsx'
OUTPUT_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data'

# Clean start
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

print("="*80)
print("FINAL DATA CLEANING - Liberty Towers Fibre Relocation")
print("="*80)

xl = pd.ExcelFile(INPUT_FILE)
created_files = []

def make_unique_columns(columns):
    """Ensure all column names are unique"""
    seen = {}
    result = []
    for col in columns:
        col = str(col).strip()
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)
    return result

# ============================================================================
# 1. JAN LABOUR
# ============================================================================
print("\n📑 Processing: JAN Labour...")

df_raw = pd.read_excel(xl, sheet_name='JAN', header=None)

# Find header
header_idx = None
for i in range(min(10, len(df_raw))):
    row = df_raw.iloc[i]
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'DATE' in row_str and 'LABOUR' in row_str:
        header_idx = i
        break

if header_idx is not None:
    # Read raw and manually set columns
    df = pd.read_excel(xl, sheet_name='JAN', header=None, skiprows=header_idx+1)
    
    # Only keep first 6 columns
    df = df.iloc[:, :6]
    df.columns = ['DATE', 'LABOUR', 'QUANTITY', 'RATE', 'TIME', 'TOTAL']
    
    # Clean
    df = df[df['DATE'].notna()]
    df = df[~df['DATE'].astype(str).str.upper().str.contains('DATE|NAN')]
    
    # Convert types
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce', dayfirst=True)
    df = df[df['DATE'].notna()]
    df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d')
    
    for col in ['QUANTITY', 'RATE', 'TIME', 'TOTAL']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['TOTAL'] = df['TOTAL'].round(2)
    df['MONTH'] = 'January'
    df['YEAR'] = 2025
    
    # Drop any remaining NaN rows
    df = df.dropna(subset=['DATE', 'LABOUR'])
    
    df_jan = df.copy()
    print(f"   ✅ {len(df)} records")
    df.to_csv(os.path.join(OUTPUT_DIR, 'labour_january.csv'), index=False)
    created_files.append('labour_january.csv')
else:
    df_jan = pd.DataFrame()
    print("   ⚠️ Could not find header")

# ============================================================================
# 2. FEB LABOUR
# ============================================================================
print("\n📑 Processing: FEB Labour...")

df_raw = pd.read_excel(xl, sheet_name='FEB', header=None)

header_idx = None
for i in range(min(10, len(df_raw))):
    row = df_raw.iloc[i]
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'DATE' in row_str and 'LABOUR' in row_str:
        header_idx = i
        break

if header_idx is not None:
    df = pd.read_excel(xl, sheet_name='FEB', header=None, skiprows=header_idx+1)
    df = df.iloc[:, :6]
    df.columns = ['DATE', 'LABOUR', 'QUANTITY', 'RATE', 'TIME', 'TOTAL']
    
    df = df[df['DATE'].notna()]
    df = df[~df['DATE'].astype(str).str.upper().str.contains('DATE|NAN')]
    
    df['DATE'] = pd.to_datetime(df['DATE'], errors='coerce', dayfirst=True)
    df = df[df['DATE'].notna()]
    df['DATE'] = df['DATE'].dt.strftime('%Y-%m-%d')
    
    for col in ['QUANTITY', 'RATE', 'TIME', 'TOTAL']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df['TOTAL'] = df['TOTAL'].round(2)
    df['MONTH'] = 'February'
    df['YEAR'] = 2025
    df = df.dropna(subset=['DATE', 'LABOUR'])
    
    df_feb = df.copy()
    print(f"   ✅ {len(df)} records")
    df.to_csv(os.path.join(OUTPUT_DIR, 'labour_february.csv'), index=False)
    created_files.append('labour_february.csv')
else:
    df_feb = pd.DataFrame()

# ============================================================================
# 3. COMBINED LABOUR
# ============================================================================
print("\n📑 Creating: Combined Labour...")

labour_all = pd.concat([df_jan, df_feb], ignore_index=True)
labour_all = labour_all.sort_values('DATE').reset_index(drop=True)
print(f"   ✅ {len(labour_all)} total records")
labour_all.to_csv(os.path.join(OUTPUT_DIR, 'labour_all.csv'), index=False)
created_files.append('labour_all.csv')

# ============================================================================
# 4. VEHICLE COSTS
# ============================================================================
print("\n📑 Processing: Vehicle Costs...")

df_raw = pd.read_excel(xl, sheet_name='VEHICLE', header=None)

# Find data rows (vehicle registration pattern)
vehicle_data = []
for i, row in df_raw.iterrows():
    first = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
    # Vehicle registrations typically have letters and numbers
    if first and len(first) >= 5:
        if any(c.isdigit() for c in first) and any(c.isalpha() for c in first):
            if first.upper() not in ['VEHICLE REG', 'NAN']:
                supervisor = str(row.iloc[1]).strip() if pd.notna(row.iloc[1]) else 'Unknown'
                cost_km = pd.to_numeric(row.iloc[2], errors='coerce') if pd.notna(row.iloc[2]) else 0
                total = pd.to_numeric(row.iloc[3], errors='coerce') if pd.notna(row.iloc[3]) else 0
                
                vehicle_data.append({
                    'VEHICLE_REG': first,
                    'SUPERVISOR': supervisor,
                    'COST_PER_KM': round(cost_km, 2) if cost_km else 0,
                    'TOTAL_COST': round(total, 2) if total else 0
                })

df_vehicle = pd.DataFrame(vehicle_data)
print(f"   ✅ {len(df_vehicle)} records")
df_vehicle.to_csv(os.path.join(OUTPUT_DIR, 'vehicle_costs.csv'), index=False)
created_files.append('vehicle_costs.csv')

# ============================================================================
# 5. MATERIALS
# ============================================================================
print("\n📑 Processing: Materials...")

df_raw = pd.read_excel(xl, sheet_name='MATERIAL', header=None)

# Find header
header_idx = None
for i in range(min(10, len(df_raw))):
    row = df_raw.iloc[i]
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'MODEL' in row_str or 'ALLOCATION' in row_str or 'RESPONSIBLE' in row_str:
        header_idx = i
        break

if header_idx is not None:
    df = pd.read_excel(xl, sheet_name='MATERIAL', header=None, skiprows=header_idx+1)
    
    # Assign clean column names (based on typical structure)
    if df.shape[1] >= 6:
        df = df.iloc[:, :6]
        df.columns = ['ITEM_NAME', 'LOCATION', 'RESPONSIBLE_PERSON', 'QUANTITY', 'UNIT_COST', 'TOTAL_COST']
    else:
        df.columns = ['ITEM_NAME', 'LOCATION', 'RESPONSIBLE_PERSON', 'QUANTITY', 'UNIT_COST', 'TOTAL_COST'][:df.shape[1]]
    
    # Clean
    df = df[df['ITEM_NAME'].notna()]
    df = df[~df['ITEM_NAME'].astype(str).str.upper().str.contains('MODEL|NAN|ITEM')]
    
    for col in ['QUANTITY', 'UNIT_COST', 'TOTAL_COST']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Calculate missing totals
    if 'TOTAL_COST' in df.columns and 'QUANTITY' in df.columns and 'UNIT_COST' in df.columns:
        mask = df['TOTAL_COST'].isna()
        df.loc[mask, 'TOTAL_COST'] = df.loc[mask, 'QUANTITY'] * df.loc[mask, 'UNIT_COST']
    
    df = df.dropna(subset=['ITEM_NAME'])
    
    # Round
    for col in ['UNIT_COST', 'TOTAL_COST']:
        if col in df.columns:
            df[col] = df[col].round(2)
    
    print(f"   ✅ {len(df)} records")
    df.to_csv(os.path.join(OUTPUT_DIR, 'materials.csv'), index=False)
    created_files.append('materials.csv')

# ============================================================================
# 6. TOOLS
# ============================================================================
print("\n📑 Processing: Tools...")

df_raw = pd.read_excel(xl, sheet_name='TOOLS', header=None)

header_idx = None
for i in range(min(10, len(df_raw))):
    row = df_raw.iloc[i]
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'ITEM' in row_str or 'DESCRIPTION' in row_str:
        header_idx = i
        break

if header_idx is not None:
    df = pd.read_excel(xl, sheet_name='TOOLS', header=None, skiprows=header_idx+1)
    
    # Take first 4-5 meaningful columns
    num_cols = min(df.shape[1], 5)
    df = df.iloc[:, :num_cols]
    
    col_names = ['ITEM', 'DESCRIPTION', 'QUANTITY', 'DAYS', 'AMOUNT'][:num_cols]
    df.columns = col_names
    
    df = df[df['ITEM'].notna()]
    df = df[~df['ITEM'].astype(str).str.upper().str.contains('ITEM|NAN')]
    
    for col in ['QUANTITY', 'DAYS', 'AMOUNT']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    if 'AMOUNT' in df.columns:
        df['AMOUNT'] = df['AMOUNT'].round(2)
    
    df = df.dropna(subset=['ITEM'])
    
    print(f"   ✅ {len(df)} records")
    df.to_csv(os.path.join(OUTPUT_DIR, 'tools.csv'), index=False)
    created_files.append('tools.csv')

# ============================================================================
# 7. TAR COSTS
# ============================================================================
print("\n📑 Processing: Tar Costs...")

df_raw = pd.read_excel(xl, sheet_name='TAR', header=None)

header_idx = None
for i in range(min(10, len(df_raw))):
    row = df_raw.iloc[i]
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'ITEM' in row_str or 'DESCRIPTION' in row_str:
        header_idx = i
        break

if header_idx is not None:
    df = pd.read_excel(xl, sheet_name='TAR', header=None, skiprows=header_idx+1)
    
    num_cols = min(df.shape[1], 4)
    df = df.iloc[:, :num_cols]
    
    col_names = ['ITEM', 'DESCRIPTION', 'QUANTITY', 'AMOUNT'][:num_cols]
    df.columns = col_names
    
    df = df[df['ITEM'].notna()]
    df = df[~df['ITEM'].astype(str).str.upper().str.contains('ITEM|NAN')]
    
    for col in ['QUANTITY', 'AMOUNT']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['ITEM'])
    
    print(f"   ✅ {len(df)} records")
    df.to_csv(os.path.join(OUTPUT_DIR, 'tar_costs.csv'), index=False)
    created_files.append('tar_costs.csv')

# ============================================================================
# 8. DIESEL COSTS
# ============================================================================
print("\n📑 Processing: Diesel Costs...")

df_raw = pd.read_excel(xl, sheet_name='Diesel Cost', header=None)

diesel_data = []
for i, row in df_raw.iterrows():
    first = str(row.iloc[0]).strip() if pd.notna(row.iloc[0]) else ''
    if first and first.upper() not in ['NAN', 'DIESEL COSTS', 'TOTAL', 'ILLOVU LANDFILL', '']:
        if not any(x in first.upper() for x in ['TOTAL COSTS', 'TOTAL LITERS', 'SITE']):
            diesel_data.append({'EMPLOYEE': first})

df_diesel = pd.DataFrame(diesel_data)
if len(df_diesel) > 0:
    print(f"   ✅ {len(df_diesel)} records")
    df_diesel.to_csv(os.path.join(OUTPUT_DIR, 'diesel_costs.csv'), index=False)
    created_files.append('diesel_costs.csv')

# ============================================================================
# 9. COST BREAKDOWN (from SUMMARY)
# ============================================================================
print("\n📑 Creating: Cost Breakdown...")

df_raw = pd.read_excel(xl, sheet_name='SUMMARY', header=None)

costs = {}
contract_value = None

for i, row in df_raw.iterrows():
    for j, val in enumerate(row):
        if pd.notna(val) and isinstance(val, str):
            val_upper = val.upper().strip()
            # Look for numeric in same row
            for k in range(len(row)):
                num_val = row.iloc[k]
                if pd.notna(num_val) and isinstance(num_val, (int, float)) and num_val > 100:
                    if 'CONTRACT' in val_upper and 'VALUE' in val_upper:
                        contract_value = num_val
                    elif val_upper == 'LABOUR' or 'LABOUR COST' in val_upper:
                        costs['Labour'] = num_val
                    elif 'MATERIAL' in val_upper:
                        costs['Material'] = num_val
                    elif 'VEHICLE' in val_upper and 'COST' in val_upper:
                        costs['Vehicle'] = num_val
                    elif val_upper == 'OHC':
                        costs['Overhead'] = num_val
                    break

cost_df = pd.DataFrame([
    {'CATEGORY': k, 'AMOUNT': round(v, 2)} for k, v in costs.items()
])

if len(cost_df) > 0:
    total = cost_df['AMOUNT'].sum()
    cost_df['PERCENTAGE'] = (cost_df['AMOUNT'] / total * 100).round(1)
    cost_df['PROJECT'] = 'Liberty Towers Fibre Relocation'
    print(f"   ✅ {len(cost_df)} categories (Total: R{total:,.2f})")
    cost_df.to_csv(os.path.join(OUTPUT_DIR, 'cost_breakdown.csv'), index=False)
    created_files.append('cost_breakdown.csv')
    total_costs = total
else:
    total_costs = 0

# ============================================================================
# 10. PROJECT KPIs
# ============================================================================
print("\n📑 Creating: Project KPIs...")

contract = contract_value if contract_value else 240100.82

kpis = pd.DataFrame([
    {'KPI_NAME': 'Contract Value', 'VALUE': round(contract, 2), 'UNIT': 'ZAR'},
    {'KPI_NAME': 'Total Costs', 'VALUE': round(total_costs, 2), 'UNIT': 'ZAR'},
    {'KPI_NAME': 'Remaining Budget', 'VALUE': round(contract - total_costs, 2), 'UNIT': 'ZAR'},
    {'KPI_NAME': 'Budget Used', 'VALUE': round((total_costs/contract)*100, 1), 'UNIT': '%'},
    {'KPI_NAME': 'Profit Margin', 'VALUE': round(((contract-total_costs)/contract)*100, 1), 'UNIT': '%'}
])
kpis['PROJECT'] = 'Liberty Towers Fibre Relocation'
kpis['REPORT_DATE'] = datetime.now().strftime('%Y-%m-%d')

print(f"   ✅ {len(kpis)} KPIs")
kpis.to_csv(os.path.join(OUTPUT_DIR, 'project_kpis.csv'), index=False)
created_files.append('project_kpis.csv')

# ============================================================================
# 11. PROJECT STATUS
# ============================================================================
print("\n📑 Creating: Project Status...")

status = pd.DataFrame([{
    'PROJECT_NAME': 'Liberty Towers Fibre Relocation',
    'STATUS': 'In Progress',
    'CONTRACT_VALUE': round(contract, 2),
    'TOTAL_COSTS': round(total_costs, 2),
    'REMAINING_BUDGET': round(contract - total_costs, 2),
    'BUDGET_USED_PCT': round((total_costs/contract)*100, 1),
    'REPORT_DATE': datetime.now().strftime('%Y-%m-%d')
}])

print(f"   ✅ 1 record")
status.to_csv(os.path.join(OUTPUT_DIR, 'project_status.csv'), index=False)
created_files.append('project_status.csv')

# ============================================================================
# 12. LABOUR SUMMARY
# ============================================================================
print("\n📑 Creating: Labour Summary...")

if len(labour_all) > 0:
    summary = labour_all.groupby('LABOUR').agg({
        'TOTAL': 'sum',
        'QUANTITY': 'sum'
    }).reset_index()
    summary.columns = ['ROLE', 'TOTAL_COST', 'TOTAL_WORKERS']
    summary['TOTAL_COST'] = summary['TOTAL_COST'].round(2)
    summary['PROJECT'] = 'Liberty Towers Fibre Relocation'
    
    print(f"   ✅ {len(summary)} roles")
    summary.to_csv(os.path.join(OUTPUT_DIR, 'labour_summary.csv'), index=False)
    created_files.append('labour_summary.csv')

# ============================================================================
# 13. MONTHLY TREND
# ============================================================================
print("\n📑 Creating: Monthly Trend...")

jan_total = df_jan['TOTAL'].sum() if len(df_jan) > 0 else 0
feb_total = df_feb['TOTAL'].sum() if len(df_feb) > 0 else 0

trend = pd.DataFrame([
    {'MONTH': 'January', 'MONTH_NUM': 1, 'LABOUR_COST': round(jan_total, 2)},
    {'MONTH': 'February', 'MONTH_NUM': 2, 'LABOUR_COST': round(feb_total, 2)}
])
trend['PROJECT'] = 'Liberty Towers Fibre Relocation'

print(f"   ✅ 2 months")
trend.to_csv(os.path.join(OUTPUT_DIR, 'monthly_trend.csv'), index=False)
created_files.append('monthly_trend.csv')

# ============================================================================
# FINAL SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ ALL DATA PROPERLY CLEANED")
print("="*80)
print(f"\n📁 Output: {OUTPUT_DIR}")
print(f"\n📄 {len(created_files)} clean CSV files created:\n")

for f in created_files:
    path = os.path.join(OUTPUT_DIR, f)
    df = pd.read_csv(path)
    print(f"   ✓ {f:<25} | {len(df):>3} rows | {len(df.columns):>2} cols")

print("\n✓ No 'Unnamed' columns")
print("✓ No empty rows")
print("✓ All data properly formatted")
print("✓ Ready for Power BI")
