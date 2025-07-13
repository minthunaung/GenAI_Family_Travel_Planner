from controller.shared_types import HybridState

def summarize_agent():
    def _run(s: HybridState) -> HybridState:
        log = s.memory_log or []
        # Modify summarize logic to handle different inputs
        if "plan" in s.input.lower(): #Travel Plan
            s.output = f"✅ {s.recommendations}"
        elif "weather" in s.input.lower():
             s.output = f"✅  {s.weather_info}"
        elif "photo" in s.input.lower():
             s.output = f"✅  {s.photo_idea}"
        else: # Fallback
             s.output  = "❌  No specific output or recommendation"

        print(s.output)
        log.append(s.output)
        s.memory_log = log

        return s
    return _run