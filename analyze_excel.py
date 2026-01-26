"""
Script to analyze the Excel file structure and content.
"""
import pandas as pd
import os

# File path
file_path = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\Fibre Relocation - Liberty Towers.xlsx'

print("="*80)
print("EXCEL FILE ANALYSIS: Fibre Relocation - Liberty Towers.xlsx")
print("="*80)

# Load the Excel file
xl = pd.ExcelFile(file_path)

print(f"\n📊 Total Number of Sheets: {len(xl.sheet_names)}")
print(f"📋 Sheet Names: {xl.sheet_names}")

print("\n" + "="*80)
print("DETAILED SHEET ANALYSIS")
print("="*80)

for sheet_name in xl.sheet_names:
    print(f"\n{'─'*80}")
    print(f"📑 SHEET: {sheet_name}")
    print(f"{'─'*80}")
    
    # Read the sheet
    df = pd.read_excel(xl, sheet_name=sheet_name)
    
    print(f"\n📐 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"\n📝 Columns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        dtype = df[col].dtype
        non_null = df[col].notna().sum()
        null_pct = (df[col].isna().sum() / len(df) * 100) if len(df) > 0 else 0
        print(f"   {i:2}. {col:<50} | Type: {str(dtype):<15} | Non-Null: {non_null:>5} | Null%: {null_pct:.1f}%")
    
    print(f"\n📊 Data Preview (first 5 rows):")
    print(df.head().to_string())
    
    print(f"\n📈 Data Types Summary:")
    print(df.dtypes.value_counts().to_string())
    
    # Check for unique values in key columns
    print(f"\n🔑 Unique Values in First 5 Columns:")
    for col in df.columns[:5]:
        unique_count = df[col].nunique()
        print(f"   - {col}: {unique_count} unique values")
        if unique_count <= 10:
            unique_vals = df[col].dropna().unique()[:10]
            print(f"     Values: {list(unique_vals)}")

print("\n" + "="*80)
print("ANALYSIS COMPLETE")
print("="*80)
