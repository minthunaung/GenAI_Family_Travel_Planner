import re
import numpy as np
import replicate
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_openai import OpenAIEmbeddings # Import from langchain_openai
import openai # Import the openai library

# Assuming these imports are necessary and the files exist in the mounted drive
from utils.utils import load_family
from utils.config import DB_PATH, RAG_INDEX_PATH, WEATHER_API_KEY,OPENAI_API_KEY

# Assuming these imports are necessary and the files exist in the mounted drive
from agents.rag_agents import rag_retrieval_agent, rag_recommendation_agent
from agents.weather_agent import weather_check_agent, get_weather # Need get_weather for weather_check_agent
from agents.photo_memory_agent import photo_memory_agent
from agents.photo_generation_agent import photo_generation_agent
from utils.rag_utils import load_rag_index
from openai import OpenAI

from pydantic import ValidationError


class HybridState(BaseModel):
    input: str # Still need input for initial state, though router is removed
    next: Optional[
        Literal[
            "travel_planner",
            "weather_tool",
            "sql_tool",
            "recommender_tool"
        ]
    ] = None
    output: Optional[str] = None # Still need output for final result
    history: List[str] = [] # Still need history

    family: Optional[List[Dict[str, Any]]] = None
    selected_activity: Optional[str] = None
    rag_context: Optional[List[str]] = None
    recommendations: Optional[str] = None
    location: Optional[str] = None
    weather_ok: Optional[bool] = None
    weather_info: Optional[str] = None
    photo_idea: Optional[str] = None
    photo_url: Optional[str] = None
    memory_log: Optional[List[str]] = []


# Reuse necessary agent function definitions from previous cells
# Assuming fetch_family_agent, rag_retrieval_agent, rag_recommendation_agent,
# weather_check_agent, photo_memory_agent, photo_generation_agent, summarize_agent
# are defined and work correctly based on previous debugging.
# Copying definitions here for clarity in this isolated graph:

def fetch_family_agent():
    def _run(s: HybridState) -> HybridState:
        print(f"--- Inside fetch_family_agent ---")
        print(f"State on entry: {s}")
        dbpath = parent_dir+"/"+DB_PATH
        print("DB_PATH",dbpath)
        fam = load_family(dbpath)
        print(f"Loaded family data: {fam}")
        prefs = {}
        for m in fam:
            for act, liked in m["preferences"].items():
                if liked:
                    prefs[act] = prefs.get(act, 0) + 1
        top = max(prefs, key=prefs.get) if prefs else "beach"
        s.family = fam
        s.selected_activity = top
        print(f"State before returning from fetch_family_agent: {s}")
        print(f"--- Exiting fetch_family_agent ---")
        return s
    return _run

def rag_retrieval_agent(index_path="family_travel_rag.index", k=5):
    index, docs = load_rag_index(index_path)
    embedder = OpenAIEmbeddings()

    def _run(state):
        print(f"--- Inside rag_retrieval_agent ---")
        print(f"State on entry: {state}")
        query = state.selected_activity
        q_vec = np.array(embedder.embed_query(query)).astype("float32")
        # Corrected search method call to include distances and labels
        distances, I = index.search(q_vec.reshape(1, -1), k)
        state.rag_context = [docs[i].page_content for i in I[0]]
        print(f"State before returning from rag_retrieval_agent: {state}")
        print(f"--- Exiting rag_retrieval_agent ---")
        return state

    return _run

def rag_recommendation_agent():
    def _run(state):
        print(f"--- Inside rag_recommendation_agent ---")
        print(f"State on entry: {state}")
        ctx = "\n\n".join(state.rag_context or [])
        prompt = (
            f"Based on these documents:\n{ctx}\n\n"
            f"Recommend 3 family-friendly destinations or activities "
            f"related to '{state.selected_activity}'."
        )
        # Explicitly use openai.ChatCompletion
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )
        state.recommendations = resp.choices[0].message.content
        print(f"State before returning from rag_recommendation_agent: {state}")
        print(f"--- Exiting rag_recommendation_agent ---")
        return state

    return _run

def extract_location_agent():
    def _run(state):       
        # 1) Try regex for lines like "1. **Place Name**:"
        print(f"--- Inside extract_location_agent ---")
        print(f"State on entry: {state}")
        print(f"state.recommendations: {state.recommendations}")
        rec = state.recommendations #state.get("recommendations", "")
        m = re.search(r"\d+\.\s*\*\*(.*?)\*\*", rec)
        if m:
            place = m.group(1).strip()
        else:
            # 2) Fallback: take first non-empty line
            for line in rec.splitlines():
                if line.strip():
                    place = line.strip()
                    break
            else:
                place = ""
        
        # 3) If no comma but multiple words, assume first token is the place
        if place and "," not in place and len(place.split()) > 1:
            place = place.split()[0]
        state.location  = place                    
        print(f"Extracted location: {place}")
        print(f"State before returning from extract_location_agent: {state}")
        print(f"--- Exiting extract_location_agent ---") 
        return state       
    return _run

def weather_check_agent():
    def _run(state):
        print(f"--- Inside weather_check_agent ---")
        print(f"State on entry: {state}")
        # Assuming state.selected_activity can be used to determine a location
        # In a real scenario, you might need a location extraction step
        info = get_weather(state.location) # Call the imported get_weather function
        state.weather_info = info
        print(f"Weather info: {info}")
        #state.weather_ok = info.split(",")[0] in ("Clear","Clouds") #enable later to check weather is clear
        state.weather_ok = True
        print(f"State before returning from weather_check_agent: {state}")
        print(f"--- Exiting weather_check_agent ---")
        return state
    return _run

def photo_memory_agent():
     def _run(state):
        print(f"--- Inside photo_memory_agent ---")
        print(f"State on entry: {state}")
        # Placeholder: Generate a simple photo idea based on selected activity
        photo_idea = f"A family enjoying {state.selected_activity}"
        state.photo_idea = photo_idea
        print(f"State before returning from photo_memory_agent: {state}")
        print(f"--- Exiting photo_memory_agent ---")
        return state
     return _run


# def photo_generation_agent():
#     def _run(state):
#         print(f"--- Inside photo_generation_agent ---")
#         print(f"State on entry: {state}")      
#         prompt = state.photo_idea or "Family at sunset beach"
#         url = replicate.run(
#         "stability-ai/stable-diffusion-3.5-medium",
#         input={ "prompt": prompt, "seed": 42, "steps": 30, "format": "png" }
#         )
#         print(f"Generated photo URL: {url[0]}")
#         state.photo_url = f"{url[0]}"
#         print(f"State before returning from photo_generation_agent: {state}")
#         print(f"--- Exiting photo_generation_agent ---")        
#         return state
#     return _run

def photo_generation_agent():
    def _run(state):
        print(f"--- Inside photo_generation_agent ---")
        print(f"State on entry: {state}")      
        prompt =  state.photo_idea if not None else state.input
        client = OpenAI(api_key=OPENAI_API_KEY)
        url = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
        )
        print(f"Generated photo URL: {url.data[0].url}") 
        state.photo_url = f"{url.data[0].url}"
        print(f"State before returning from photo_generation_agent: {state}")
        print(f"--- Exiting photo_generation_agent ---")        
        return state
    return _run



def summarize_agent():
    def _run(s: HybridState) -> HybridState:
        print(f"--- Inside summarize_agent ---")
        print(f"State on entry: {s}")

        log = s.memory_log or []
        # Modify summarize logic to handle different inputs
        if s.output is not None: # If a tool provided an output, log that
             entry = f"Tool Output → {s.output}"
             s.output = s.output
        elif s.recommendations: # Original travel planner logic
             head = s.recommendations.splitlines()[0] if s.recommendations else ""
             entry = f"{s.selected_activity}→{head}"
             s.output = s.recommendations # Set output from recommendations
        else: # Fallback
             entry = "No specific output or recommendation"
             s.output = entry

        image_url = s.photo_url
        print(f"Image URL: {image_url}")
        # Check if photo_url is not None before displaying
        if image_url:
            display_image_from_url(image_url)
        else:
            print("No photo URL available to display.")

        log.append(entry)
        s.memory_log = log

        print(f"State before returning from summarize_agent: {s}")
        print(f"--- Exiting summarize_agent ---")

        return s
    return _run


# Build the simplified travel planner graph
def build_travel_planner_graph():
    graph = StateGraph(HybridState)

    # Add nodes for the travel planner flow
    graph.add_node("fetch_family", RunnableLambda(fetch_family_agent()))
    RAG_path = parent_dir+"/"+RAG_INDEX_PATH
    graph.add_node("rag_retrieve", RunnableLambda(rag_retrieval_agent(RAG_path)))
    graph.add_node("rag_recommend", RunnableLambda(rag_recommendation_agent()))
    graph.add_node("extract_location", RunnableLambda(extract_location_agent()))
    graph.add_node("weather_check", RunnableLambda(weather_check_agent()))
    graph.add_node("photo_memory", RunnableLambda(photo_memory_agent()))
    graph.add_node("photo_generate", RunnableLambda(photo_generation_agent()))
    graph.add_node("summarize", RunnableLambda(summarize_agent()))

    # Define the flow - sequential edges
    graph.set_entry_point("fetch_family") # Start directly with fetching family data

    graph.add_edge("fetch_family",  "rag_retrieve")
    graph.add_edge("rag_retrieve","rag_recommend")
    graph.add_edge("rag_recommend",  "extract_location")
    graph.add_edge("extract_location","weather_check")
    graph.add_conditional_edges(
        "weather_check",
        # Define the condition based on state.weather_ok
        lambda s: "photo_memory" if s.weather_ok is True else "summarize",
        {"photo_memory": "photo_memory", "summarize": "summarize"}
    )

    # Edges from photo steps
    graph.add_edge("photo_memory","photo_generate")
    graph.add_edge("photo_generate","summarize")

    # Set summarize as the finish point
    graph.set_finish_point("summarize")

    return graph.compile()

# Test the simplified travel planner graph
print("Building simplified travel planner graph...")
travel_planner_graph = build_travel_planner_graph()
print("Simplified travel planner graph built successfully.")

# Invoke the graph with an initial state
# The input might not be directly used by fetch_family, but required by state
test_input_travel = "Plan a family trip"
test_state_travel = HybridState(input=test_input_travel, history=[]) # Provide initial input

print(f"\n--- Invoking simplified travel planner graph with input: '{test_input_travel}' ---")
try:
    travel_planner_result = travel_planner_graph.invoke(test_state_travel)

    print("\n--- Raw Result from travel_planner_graph.invoke ---")
    print(travel_planner_result)
    print("--- End of Raw Result ---")

    # Check and print the output
    if isinstance(travel_planner_result, dict) and 'output' in travel_planner_result and travel_planner_result['output'] is not None:
        print(f"\n🤖 Agent Output: {travel_planner_result['output']}")
    else:
        print("\n🤖 Agent Output: Could not retrieve a specific output.")
        if isinstance(travel_planner_result, dict):
             print(f"Final state keys: {travel_planner_result.keys()}")


except Exception as e:
    print(f"\nAn error occurred during simplified graph invocation: {e}")