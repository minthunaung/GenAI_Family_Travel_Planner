from utils.utils import load_family
from controller.shared_types import HybridState

def fetch_family_agent(dbpath="family_travel_planner.db"):
    def _run(s: HybridState) -> HybridState:
        #dbpath = parent_dir+"/"+DB_PATH
        fam = load_family(dbpath)
        #print(f"Loaded family data: {fam}")
        prefs = {}
        for m in fam:
            for act, liked in m["preferences"].items():
                if liked:
                    prefs[act] = prefs.get(act, 0) + 1
        top = max(prefs, key=prefs.get) if prefs else "beach"
        s.family = fam
        s.selected_activity = top
        return s
    return _run