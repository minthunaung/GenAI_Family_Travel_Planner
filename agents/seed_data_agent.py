# seed_data_agent.py

import sqlite3
import json
import openai
from openai import ChatCompletion
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, List, Dict
from controller.shared_types import HybridState
from utils.config import OPENAI_API_KEY


openai.api_key = OPENAI_API_KEY

def seed_data_agent(DB_PATH="family_travel_planner.db"):
    """
    Agent that:
    1. Reads state.input as free-form text.
    2. Calls OpenAI to extract JSON list of {role, age, preferences}.
    3. Writes the family_members table in SQLite.
    4. Stores the parsed list in state.family and confirmation in state.output.
    5. Eg. I’m 42—into museums and food. My wife is 40, she likes the beach and shopping. Our son is 12, loves video games and drawing. My daughter is 10, like to play at beach and love animals.
    """
    def _run(state: HybridState) -> HybridState:
        # 1) Build the extraction prompt
        prompt = (
            "I have a family trip. From this description:\n"
            f"\"{state.input}\"\n\n"
            "Extract a JSON array of objects with keys:\n"
            "- role: string (e.g. 'Husband', 'Wife', 'Son', 'Daughter')\n"
            "- age: integer\n"
            "- preferences: object of boolean flags (e.g. {'beach': true, 'museums': false})\n\n"
            "Return ONLY the JSON. Example:\n"
            "[{\"role\":\"Wife\",\"age\":42,\"preferences\":{\"beach\":true,\"shopping\":true}}]"
        )

        # 2) Invoke the LLM
        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content": prompt}],
                temperature=0
            )
            text = resp.choices[0].message.content.strip()
            family_data: List[Dict[str, Any]] = json.loads(text)
        except Exception as e:
            state.output = f"❌ Extraction failed: {e}"
            print (state.output)
            return state

        # 3) Seed the database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM family_members;")
        for member in family_data:
            cursor.execute(
                "INSERT INTO family_members (role, age, preferences) VALUES (?, ?, ?);",
                (member["role"], member["age"], json.dumps(member["preferences"]))
            )
        conn.commit()
        conn.close()

        # 4) Update state and confirm
        state.family = family_data
        state.output = f"✅ Registered {len(family_data)} family members."
        print(f"Registered {len(family_data)} family members.")
        return state

    return _run