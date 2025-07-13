import sqlite3
import sys
import os
# Add the parent directory of 'utils' to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print("path",sys.path)
from utils.config import DB_PATH

def create_family_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS family_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        age INTEGER NOT NULL,
        preferences TEXT
    );
    """)

    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {DB_PATH}")

if __name__ == "__main__":
    create_family_db()
