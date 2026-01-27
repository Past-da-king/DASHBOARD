import pandas as pd
import os
import warnings

warnings.filterwarnings('ignore')

def search_risks():
    files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~$')]
    print(f"Searching {len(files)} files for 'Risk'...")
    
    for f in files:
        print(f"\n--- {f} ---")
        try:
            xl = pd.ExcelFile(f)
            for sheet_name in xl.sheet_names:
                df = pd.read_excel(f, sheet_name=sheet_name, header=None)
                # Search for 'risk' or 'issue' in any cell
                mask = df.stack().astype(str).str.contains('risk|issue', case=False, na=False).unstack()
                matches = mask.any(axis=1)
                if matches.any():
                    print(f"  FOUND in Sheet: {sheet_name}")
                    # Print matching rows
                    matching_rows = df[matches]
                    for idx, row in matching_rows.iterrows():
                        print(f"    Row {idx}: {row.dropna().tolist()}")
        except Exception as e:
            print(f"  Error reading {f}: {e}")

if __name__ == "__main__":
    search_risks()
