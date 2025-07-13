import sqlite3
import json
from typing import List, Dict, Any

def load_family(db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, role, age, preferences FROM family_members;")
    rows = cursor.fetchall()
    conn.close()

    family = []
    for id_, role, age, prefs_json in rows:
        prefs = json.loads(prefs_json)
        family.append({
            "id": id_, "role": role, "age": age, "preferences": prefs
        })
    return family
