import sqlite3
import json
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import DB_PATH

def seed_family():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM family_members;")

    family = [
        ("Husband", 42, {"museums": True, "food": True}),
        ("Wife",    42, {"beach": True,   "shopping": True}),
        ("Son",     11, {"theme_parks": True, "video_games": True}),
        ("Daughter",10, {"animals": True,  "beach": True})
    ]

    for role, age, prefs in family:
        cursor.execute(
            "INSERT INTO family_members (role, age, preferences) VALUES (?, ?, ?);",
            (role, age, json.dumps(prefs))
        )

    conn.commit()
    conn.close()
    print("✅ Family data seeded.")

if __name__ == "__main__":
    seed_family()
