import sys
import os

# Add the pmt_app directory to the python path
sys.path.append(os.path.join(os.getcwd(), 'pmt_app'))

import init_db
import importer
import database

def verify():
    print("1. Resetting Database...")
    init_db.init_db()
    
    print("\n2. Importing Project Template (Sample v2)...")
    file_path = r'c:\Users\past9\OneDrive\952 starage\Documents\DASHBOARD\Project_Template_Sample_v2.xlsx'
    
    # Using admin user id 1
    try:
        project_id = importer.import_project(file_path, 1)
        print(f"   Project Imported. ID: {project_id}")
        
        print("\n3. Verifying Risks in DB...")
        risks = database.get_project_risks(project_id)
        
        if not risks.empty:
            print(f"   ✅ SUCCESS: Found {len(risks)} risks.")
            print(risks[['date_identified', 'description', 'impact', 'status']].to_string())
        else:
            print("   ❌ FAILURE: No risks found in DB.")
            
    except Exception as e:
        print(f"   ❌ ERROR during import: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
