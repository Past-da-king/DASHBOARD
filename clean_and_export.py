"""
Fibre Relocation - Liberty Towers Data Cleaning & Export Script
Cleans all Excel sheets and exports to CSV for Power BI Dashboard
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
INPUT_FILE = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\Fibre Relocation - Liberty Towers.xlsx'
OUTPUT_DIR = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\cleaned_data'

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("="*80)
print("FIBRE RELOCATION - LIBERTY TOWERS")
print("DATA CLEANING & CSV EXPORT")
print("="*80)

xl = pd.ExcelFile(INPUT_FILE)
print(f"\n📊 Processing {len(xl.sheet_names)} sheets: {xl.sheet_names}")

cleaned_files = []

# ============================================================================
# 1. SUMMARY SHEET - Project Financial Overview
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: SUMMARY (Project Financial Overview)")
print("─"*80)

df_summary_raw = pd.read_excel(xl, sheet_name='SUMMARY', header=None)

# Extract key financial metrics from the summary
financial_data = []

# Parse the summary structure - extract key values
for idx, row in df_summary_raw.iterrows():
    for col_idx, val in enumerate(row):
        if pd.notna(val) and isinstance(val, str):
            val_clean = val.strip()
            # Check if this is a label and get the corresponding value
            if 'CONTRACT VALUE' in val_clean.upper():
                # Look for numeric value in same row
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)) and v > 1000:
                        financial_data.append({'Metric': 'Contract Value', 'Value': v})
                        break
            elif 'LABOUR COSTS' in val_clean.upper() or val_clean.upper() == 'LABOUR':
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)) and v > 100:
                        financial_data.append({'Metric': 'Labour Costs', 'Value': v})
                        break
            elif 'MATERIAL' in val_clean.upper() and 'COST' in val_clean.upper():
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)) and v > 100:
                        financial_data.append({'Metric': 'Material Costs', 'Value': v})
                        break
            elif 'VEHICLE COSTS' in val_clean.upper():
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)) and v > 100:
                        financial_data.append({'Metric': 'Vehicle Costs', 'Value': v})
                        break
            elif 'OHC' in val_clean.upper() or 'OVERHEAD' in val_clean.upper():
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)) and v > 100:
                        financial_data.append({'Metric': 'Overhead Costs (OHC)', 'Value': v})
                        break
            elif 'PROFIT' in val_clean.upper() and 'LOSS' in val_clean.upper():
                for v in row:
                    if pd.notna(v) and isinstance(v, (int, float)):
                        financial_data.append({'Metric': 'Indicative Profit/Loss', 'Value': v})
                        break

# Create summary dataframe
df_project_summary = pd.DataFrame(financial_data).drop_duplicates()
df_project_summary['Category'] = 'Financial'
df_project_summary['Project'] = 'Liberty Towers Fibre Relocation'
df_project_summary['Report_Date'] = datetime.now().strftime('%Y-%m-%d')

print(f"   ✅ Extracted {len(df_project_summary)} financial metrics")
df_project_summary.to_csv(os.path.join(OUTPUT_DIR, '01_project_financial_summary.csv'), index=False)
cleaned_files.append('01_project_financial_summary.csv')

# ============================================================================
# 2. LABOUR SHEET - Labour Cost Tracking
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: LABOUR (Labour Cost Tracking)")
print("─"*80)

# Try to find and read LABOUR data from available sheets
labour_records = []

# Check JAN and FEB sheets for labour data
for sheet in ['JAN', 'FEB']:
    df_raw = pd.read_excel(xl, sheet_name=sheet, header=None)
    
    # Find header row with DATE, LABOUR, QUANTITY, RATE, TIME, TOTAL
    header_row = None
    for idx, row in df_raw.iterrows():
        row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
        if 'DATE' in row_str and 'LABOUR' in row_str and 'RATE' in row_str:
            header_row = idx
            break
    
    if header_row is not None:
        # Read with proper header
        df_labour = pd.read_excel(xl, sheet_name=sheet, header=header_row)
        
        # Clean column names
        df_labour.columns = [str(c).strip().upper() if pd.notna(c) else f'UNNAMED_{i}' 
                           for i, c in enumerate(df_labour.columns)]
        
        # Keep only relevant columns
        keep_cols = ['DATE', 'LABOUR', 'QUANTITY', 'RATE', 'TIME', 'TOTAL']
        available_cols = [c for c in keep_cols if c in df_labour.columns]
        
        if available_cols:
            df_labour = df_labour[available_cols].copy()
            
            # Remove rows where all values are NaN or headers
            df_labour = df_labour.dropna(how='all')
            df_labour = df_labour[~df_labour.apply(lambda x: x.astype(str).str.upper().str.contains('DATE|LABOUR|QUANTITY').any(), axis=1)]
            
            # Add month identifier
            df_labour['Month'] = sheet
            df_labour['Year'] = 2025
            
            labour_records.append(df_labour)

if labour_records:
    df_labour_combined = pd.concat(labour_records, ignore_index=True)
    
    # Clean data types
    for col in ['QUANTITY', 'RATE', 'TIME', 'TOTAL']:
        if col in df_labour_combined.columns:
            df_labour_combined[col] = pd.to_numeric(df_labour_combined[col], errors='coerce')
    
    # Remove empty rows
    df_labour_combined = df_labour_combined.dropna(subset=['LABOUR'], how='all')
    df_labour_combined = df_labour_combined[df_labour_combined['LABOUR'].notna()]
    
    print(f"   ✅ Processed {len(df_labour_combined)} labour records")
    df_labour_combined.to_csv(os.path.join(OUTPUT_DIR, '02_labour_costs.csv'), index=False)
    cleaned_files.append('02_labour_costs.csv')
else:
    print("   ⚠️ No labour data found")

# ============================================================================
# 3. VEHICLE SHEET - Vehicle Cost Tracking
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: VEHICLE (Vehicle Costs)")
print("─"*80)

df_vehicle_raw = pd.read_excel(xl, sheet_name='VEHICLE', header=None)

# Find header row
header_row = None
for idx, row in df_vehicle_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'VEHICLE' in row_str and ('COST' in row_str or 'REG' in row_str):
        header_row = idx
        break

if header_row is not None:
    df_vehicle = pd.read_excel(xl, sheet_name='VEHICLE', header=header_row)
    df_vehicle.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                         for i, c in enumerate(df_vehicle.columns)]
    
    # Drop completely empty rows and columns
    df_vehicle = df_vehicle.dropna(how='all')
    df_vehicle = df_vehicle.dropna(axis=1, how='all')
    
    # Remove header-like rows in data
    df_vehicle = df_vehicle[~df_vehicle.apply(lambda x: str(x.iloc[0]).upper() in ['VEHICLE REG', 'NAN'], axis=1)]
    
    print(f"   ✅ Processed {len(df_vehicle)} vehicle records")
    print(f"   Columns: {list(df_vehicle.columns)}")
    df_vehicle.to_csv(os.path.join(OUTPUT_DIR, '03_vehicle_costs.csv'), index=False)
    cleaned_files.append('03_vehicle_costs.csv')
else:
    print("   ⚠️ Could not find vehicle data header")

# ============================================================================
# 4. DIESEL COST SHEET
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: DIESEL COST")
print("─"*80)

df_diesel_raw = pd.read_excel(xl, sheet_name='Diesel Cost', header=None)

# Find the header row with TOTAL COSTS
header_row = None
for idx, row in df_diesel_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'TOTAL COSTS' in row_str or 'TOTAL' in row_str:
        header_row = idx
        break

if header_row is not None:
    df_diesel = pd.read_excel(xl, sheet_name='Diesel Cost', header=header_row)
    df_diesel.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                        for i, c in enumerate(df_diesel.columns)]
    
    # Clean and filter
    df_diesel = df_diesel.dropna(how='all')
    df_diesel = df_diesel.dropna(axis=1, how='all')
    
    # Remove total/header rows
    df_diesel = df_diesel[~df_diesel.iloc[:, 0].astype(str).str.upper().isin(['TOTAL', 'NAN', '', 'DIESEL COSTS'])]
    
    print(f"   ✅ Processed {len(df_diesel)} diesel cost records")
    df_diesel.to_csv(os.path.join(OUTPUT_DIR, '04_diesel_costs.csv'), index=False)
    cleaned_files.append('04_diesel_costs.csv')

# ============================================================================
# 5. MATERIAL SHEET
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: MATERIAL (Inventory/Materials)")
print("─"*80)

df_material_raw = pd.read_excel(xl, sheet_name='MATERIAL', header=None)

# Find header row
header_row = None
for idx, row in df_material_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'DESCRIPTION' in row_str or 'ITEM' in row_str or 'MATERIAL' in row_str:
        header_row = idx
        break

if header_row is not None:
    df_material = pd.read_excel(xl, sheet_name='MATERIAL', header=header_row)
    df_material.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                          for i, c in enumerate(df_material.columns)]
    
    # Clean
    df_material = df_material.dropna(how='all')
    df_material = df_material.dropna(axis=1, how='all')
    
    # Remove rows that are clearly not data
    if len(df_material) > 0:
        first_col = df_material.columns[0]
        df_material = df_material[df_material[first_col].notna()]
        df_material = df_material[~df_material[first_col].astype(str).str.upper().isin(['NAN', '', 'TOTAL', 'ITEM'])]
    
    print(f"   ✅ Processed {len(df_material)} material records")
    df_material.to_csv(os.path.join(OUTPUT_DIR, '05_materials.csv'), index=False)
    cleaned_files.append('05_materials.csv')

# ============================================================================
# 6. TOOLS SHEET
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: TOOLS (Equipment)")
print("─"*80)

df_tools_raw = pd.read_excel(xl, sheet_name='TOOLS', header=None)

# Find header row
header_row = None
for idx, row in df_tools_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'DESCRIPTION' in row_str or 'ITEM' in row_str or 'QUANTITY' in row_str:
        header_row = idx
        break

if header_row is not None:
    df_tools = pd.read_excel(xl, sheet_name='TOOLS', header=header_row)
    df_tools.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                       for i, c in enumerate(df_tools.columns)]
    
    # Clean
    df_tools = df_tools.dropna(how='all')
    df_tools = df_tools.dropna(axis=1, how='all')
    
    print(f"   ✅ Processed {len(df_tools)} tool records")
    df_tools.to_csv(os.path.join(OUTPUT_DIR, '06_tools_equipment.csv'), index=False)
    cleaned_files.append('06_tools_equipment.csv')

# ============================================================================
# 7. TAR SHEET
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: TAR (Tar/Road Costs)")
print("─"*80)

df_tar_raw = pd.read_excel(xl, sheet_name='TAR', header=None)

# Find header row
header_row = None
for idx, row in df_tar_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'ITEM' in row_str or 'DESCRIPTION' in row_str or 'QUANTITY' in row_str:
        header_row = idx
        break

if header_row is not None:
    df_tar = pd.read_excel(xl, sheet_name='TAR', header=header_row)
    df_tar.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                     for i, c in enumerate(df_tar.columns)]
    
    # Clean
    df_tar = df_tar.dropna(how='all')
    df_tar = df_tar.dropna(axis=1, how='all')
    
    print(f"   ✅ Processed {len(df_tar)} tar cost records")
    df_tar.to_csv(os.path.join(OUTPUT_DIR, '07_tar_costs.csv'), index=False)
    cleaned_files.append('07_tar_costs.csv')

# ============================================================================
# 8. PO SHEET (Purchase Orders)
# ============================================================================
print("\n" + "─"*80)
print("📑 Processing: PO (Purchase Orders)")
print("─"*80)

df_po_raw = pd.read_excel(xl, sheet_name='PO', header=None)

# Find header row
header_row = None
for idx, row in df_po_raw.iterrows():
    row_str = ' '.join([str(v).upper() for v in row if pd.notna(v)])
    if 'REFERENCE' in row_str or 'AMOUNT' in row_str or 'PO' in row_str:
        header_row = idx
        break

if header_row is not None:
    df_po = pd.read_excel(xl, sheet_name='PO', header=header_row)
    df_po.columns = [str(c).strip() if pd.notna(c) else f'Unnamed_{i}' 
                    for i, c in enumerate(df_po.columns)]
    
    # Clean
    df_po = df_po.dropna(how='all')
    df_po = df_po.dropna(axis=1, how='all')
    
    # Remove rows with contract value as it's summary
    if len(df_po) > 0:
        first_col = df_po.columns[0]
        df_po = df_po[df_po[first_col].notna()]
    
    print(f"   ✅ Processed {len(df_po)} purchase order records")
    df_po.to_csv(os.path.join(OUTPUT_DIR, '08_purchase_orders.csv'), index=False)
    cleaned_files.append('08_purchase_orders.csv')

# ============================================================================
# 9. CREATE CONSOLIDATED COST BREAKDOWN FOR DASHBOARD
# ============================================================================
print("\n" + "─"*80)
print("📑 Creating: CONSOLIDATED COST BREAKDOWN")
print("─"*80)

# Create a cost breakdown summary for dashboard pie/bar charts
cost_breakdown = []

# Extract costs from summary sheet
summary_raw = pd.read_excel(xl, sheet_name='SUMMARY', header=None)

cost_categories = {
    'Labour': None,
    'Material': None,
    'Vehicle': None,
    'Diesel/Fuel': None,
    'Tools/Equipment': None,
    'Tar/Road Work': None,
    'Overhead (OHC)': None
}

for idx, row in summary_raw.iterrows():
    for col_idx, val in enumerate(row):
        if pd.notna(val):
            val_str = str(val).upper()
            # Check for cost values in subsequent columns
            for next_col in range(col_idx + 1, len(row)):
                next_val = row.iloc[next_col]
                if pd.notna(next_val) and isinstance(next_val, (int, float)) and next_val > 10:
                    if 'LABOUR' in val_str and cost_categories['Labour'] is None:
                        cost_categories['Labour'] = next_val
                    elif 'MATERIAL' in val_str and cost_categories['Material'] is None:
                        cost_categories['Material'] = next_val
                    elif 'VEHICLE' in val_str and cost_categories['Vehicle'] is None:
                        cost_categories['Vehicle'] = next_val
                    elif 'OHC' in val_str and cost_categories['Overhead (OHC)'] is None:
                        cost_categories['Overhead (OHC)'] = next_val
                    break

# Build cost breakdown dataframe
for category, value in cost_categories.items():
    if value is not None:
        cost_breakdown.append({
            'Cost_Category': category,
            'Amount': value,
            'Project': 'Liberty Towers Fibre Relocation',
            'Report_Date': datetime.now().strftime('%Y-%m-%d')
        })

df_cost_breakdown = pd.DataFrame(cost_breakdown)
print(f"   ✅ Created cost breakdown with {len(df_cost_breakdown)} categories")
df_cost_breakdown.to_csv(os.path.join(OUTPUT_DIR, '09_cost_breakdown.csv'), index=False)
cleaned_files.append('09_cost_breakdown.csv')

# ============================================================================
# 10. PROJECT STATUS METRICS
# ============================================================================
print("\n" + "─"*80)
print("📑 Creating: PROJECT STATUS METRICS")
print("─"*80)

# Create project status metrics for KPI cards
project_status = {
    'Project_Name': 'Liberty Towers Fibre Relocation',
    'Status': 'In Progress',
    'Report_Date': datetime.now().strftime('%Y-%m-%d'),
    'Contract_Value': None,
    'Total_Costs_To_Date': None,
    'Indicative_Profit_Loss': None,
    'Profit_Margin_Percent': None,
    'Budget_Utilization_Percent': None
}

# Extract from summary
for idx, row in summary_raw.iterrows():
    for col_idx, val in enumerate(row):
        if pd.notna(val):
            val_str = str(val).upper()
            for next_col in range(col_idx + 1, len(row)):
                next_val = row.iloc[next_col]
                if pd.notna(next_val) and isinstance(next_val, (int, float)):
                    if 'CONTRACT' in val_str and 'VALUE' in val_str:
                        project_status['Contract_Value'] = next_val
                    elif 'PROFIT' in val_str and 'LOSS' in val_str and '%' not in val_str:
                        project_status['Indicative_Profit_Loss'] = next_val
                    elif '%' in val_str and 'PROFIT' in val_str:
                        project_status['Profit_Margin_Percent'] = next_val * 100 if next_val < 1 else next_val
                    break

# Calculate totals if we have cost breakdown
if df_cost_breakdown is not None and len(df_cost_breakdown) > 0:
    project_status['Total_Costs_To_Date'] = df_cost_breakdown['Amount'].sum()

# Calculate budget utilization
if project_status['Contract_Value'] and project_status['Total_Costs_To_Date']:
    project_status['Budget_Utilization_Percent'] = (project_status['Total_Costs_To_Date'] / project_status['Contract_Value']) * 100

df_project_status = pd.DataFrame([project_status])
print(f"   ✅ Created project status metrics")
df_project_status.to_csv(os.path.join(OUTPUT_DIR, '10_project_status.csv'), index=False)
cleaned_files.append('10_project_status.csv')

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ DATA CLEANING COMPLETE")
print("="*80)
print(f"\n📁 Output Directory: {OUTPUT_DIR}")
print(f"\n📄 Created {len(cleaned_files)} CSV files:")
for f in cleaned_files:
    file_path = os.path.join(OUTPUT_DIR, f)
    size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
    print(f"   • {f} ({size:,} bytes)")

print("\n" + "="*80)
print("FILES READY FOR POWER BI DASHBOARD")
print("="*80)
