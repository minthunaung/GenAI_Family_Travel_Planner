import os
import sys

from controller.hybrid_controller import build_hybrid_graph, HybridState
from utils.config import DB_PATH, RAG_INDEX_PATH, WEATHER_API_KEY

def main():
    print("🤖 Welcome to Family Travel + Multi-Tool Chat")
    print("Type 'exit' to quit.\n")

    graph = build_hybrid_graph()
    session_history = []

    while True:
        user = input("You: ").strip()
        if user.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        state = HybridState(input=user, history=session_history.copy())
        result = graph.invoke(state)
        session_history = result.history

        if result.next == "travel_planner":
            print(f"\n🎯 Activity: {result.selected_activity}")
            print(f"\n📚 Recommendations:\n{result.recommendations}")
            if result.weather_ok:
                print(f"\n🌤️ Weather OK: {result.weather_info}")
                print(f"\n📸 Photo Idea: {result.photo_idea}")
                print(f"🖼️ Image URL: {result.photo_url}")
            else:
                print(f"\n⚠️ Weather: {result.weather_info}")
            print(f"\n📝 Memory Log: {result.memory_log}\n")
        else:
            print(f"\n🔧 {result.next} → {result.output}\n")

if __name__ == "__main__":
    main()
