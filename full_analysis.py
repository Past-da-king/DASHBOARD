"""
Comprehensive Excel Analysis Script
Extracts and displays ALL sheet data for complete understanding.
"""
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

file_path = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\Fibre Relocation - Liberty Towers.xlsx'

print("="*100)
print("COMPREHENSIVE EXCEL FILE ANALYSIS")
print("File: Fibre Relocation - Liberty Towers.xlsx")
print("="*100)

xl = pd.ExcelFile(file_path)

print(f"\n📊 SHEETS FOUND: {xl.sheet_names}")
print(f"📊 TOTAL SHEETS: {len(xl.sheet_names)}")

# Store all dataframes for analysis
all_sheets = {}

for sheet_name in xl.sheet_names:
    print(f"\n\n{'#'*100}")
    print(f"## SHEET: {sheet_name}")
    print(f"{'#'*100}")
    
    # Read with different header options to find the real data
    df_raw = pd.read_excel(xl, sheet_name=sheet_name, header=None)
    
    print(f"\n📐 RAW DIMENSIONS: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    
    print(f"\n📋 COMPLETE RAW DATA (first 20 rows):")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 50)
    print(df_raw.head(20).to_string())
    
    print(f"\n📋 COMPLETE RAW DATA (last 10 rows):")
    print(df_raw.tail(10).to_string())
    
    # Find the likely header row (first row with most non-null values)
    non_null_counts = df_raw.apply(lambda x: x.notna().sum(), axis=1)
    likely_header_row = non_null_counts.idxmax()
    
    print(f"\n🔍 Likely header row index: {likely_header_row}")
    print(f"🔍 Header row content: {list(df_raw.iloc[likely_header_row])}")
    
    all_sheets[sheet_name] = df_raw

print("\n\n" + "="*100)
print("SUMMARY OF ALL SHEETS")
print("="*100)

for name, df in all_sheets.items():
    print(f"\n• {name}: {df.shape[0]} rows × {df.shape[1]} columns")
