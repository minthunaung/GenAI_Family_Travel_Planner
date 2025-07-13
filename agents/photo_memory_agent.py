# photo_memory_agent.py

import sqlite3
from typing import List, Tuple
from controller.shared_types import HybridState
from utils.config import DB_PATH

def photo_memory_agent(DB_PATH="family_travel_planner.db"):
    """
    Reads the family_members table to get each member’s role and age,
    then crafts a photo idea incorporating those details and the selected activity.
    """
    def _run(state: HybridState) -> HybridState:
        # 1) Fetch roles & ages from SQLite
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT role, age FROM family_members;")
            members: List[Tuple[str, int]] = cursor.fetchall()
        finally:
            conn.close()

        # 2) Format each member as "42-year-old Husband", etc.
        member_descriptions = [
            f"{age}-year-old {role}" for role, age in members
        ]

        # 3) Join with commas and an 'and' before the last member
        if not member_descriptions:
            group_desc = "a family"
        elif len(member_descriptions) == 1:
            group_desc = member_descriptions[0]
        else:
            group_desc = ", ".join(member_descriptions[:-1]) \
                         + " and " + member_descriptions[-1]

        # 4) Build the photo idea
        activity = state.selected_activity or "their favorite activity"
        photo_idea = (
            f"A photo of {group_desc} enjoying {activity} together, "
            "capturing genuine smiles and candid moments."
        )

        # 5) Update state and return
        state.photo_idea = photo_idea
        return state

    return _run