from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

DB_PATH = 'pmt_app/pm_tool.db'

def verify():
    pw = 'admin123'
    h = generate_password_hash(pw)
    print(f"Generated Hash: {h}")
    print(f"Check success: {check_password_hash(h, pw)}")
    
    if os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT password_hash FROM users WHERE username = 'admin'").fetchone()
        if row:
            db_h = row[0]
            print(f"Database Hash: {db_h}")
            print(f"Check DB Hash success: {check_password_hash(db_h, pw)}")
        else:
            print("Admin user not found in DB")
        conn.close()
    else:
        print("Database file not found")

if __name__ == "__main__":
    verify()
