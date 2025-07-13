import re
import os
import replicate
import numpy as np
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel,Field
from sentence_transformers import SentenceTransformer, util

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from langchain_openai import OpenAIEmbeddings, ChatOpenAI # Import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate # Import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser # Import StrOutputParser
from openai import OpenAI # Import the openai library
import json # Import json

# Assuming these imports are necessary and the files exist in the mounted drive

from utils.rag_utils import load_rag_index
from utils.config import DB_PATH, RAG_INDEX_PATH, WEATHER_API_KEY, OPENAI_API_KEY # Ensure WEATHER_API_KEY is available
from agents.weather_agent import get_weather,weather_check_agent
from agents.extract_location_agent import extract_location_agent
from agents.fetch_family_agent import fetch_family_agent
from agents.photo_generation_agent import photo_generation_agent
from agents.photo_memory_agent import photo_memory_agent
from agents.rag_agents import rag_retrieval_agent,rag_recommendation_agent
from agents.recommender_agent import recommend
from agents.sql_agent import query_database
from agents.summarize_agent import summarize_agent
from agents.llm_router_agent import llm_router_agent
from controller.shared_types import HybridState

from pydantic import ValidationError
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

SAVE_PATH = "session_state.json"
parent_dir = '/content/drive/MyDrive/Colab Notebooks/Emeritus_Generative_AI_Fundamentals_to_Advanced_Techniques_March_2025/Week13/family_travel_planner'


# Build the travel planner graph with the LLM router
def build_travel_planner_graph_with_router():
    graph = StateGraph(HybridState)

    # 1) Router
    graph.add_node("router", RunnableLambda(llm_router_agent()))

    # 2) Task nodes
    graph.add_node("fetch_family",    RunnableLambda(fetch_family_agent(parent_dir+"/family_travel_planner.db")))
    graph.add_node("rag_retrieve",    RunnableLambda(rag_retrieval_agent(parent_dir+"/family_travel_rag.index")))
    graph.add_node("rag_recommend",   RunnableLambda(rag_recommendation_agent()))
    graph.add_node("extract_location",RunnableLambda(extract_location_agent()))
    graph.add_node("weather_check",   RunnableLambda(weather_check_agent()))
    graph.add_node("photo_memory",    RunnableLambda(photo_memory_agent()))
    graph.add_node("photo_generate",  RunnableLambda(photo_generation_agent()))
    graph.add_node("summarize",       RunnableLambda(summarize_agent()))

    graph.set_entry_point("router")

    #3) Routing: map router → target node names based on state.next
    graph.add_conditional_edges(
      "router",
      # 1) selector: returns the exact branch key
      lambda s: s.next
                if s.next in {
                  "fetch_family", #travel plan
                  "extract_location", #weather
                  "photo_memory", #photo
                  "summarize" #all others
                }
                else "summarize",  # default‐fallback
      # 2) mapping: branch key → node ID
      {
        "fetch_family":  "fetch_family",
        "extract_location":"extract_location",
        "photo_memory":  "photo_memory",
        "summarize":     "summarize"
      }
    )


    # Catch‐all: if none of the above matched, terminate
    #graph.add_edge("router", END)


    graph.add_edge("fetch_family",   "rag_retrieve")
    graph.add_edge("rag_retrieve",   "rag_recommend")
    graph.add_edge("rag_recommend",  "extract_location")
    graph.add_edge("extract_location","weather_check")
    graph.add_conditional_edges(
        "weather_check",
        # Define the condition based on state.weather_ok
        lambda s: "summarize" if "weather" in s.input  else "photo_memory"
    )

    #graph.add_edge("photo_memory",   "photo_generate")
    graph.add_conditional_edges(
    "photo_memory",
    # Define the condition based on state.weather_ok
    lambda s: "photo_generate" if "photo" in s.input  else "summarize"
    )
    #graph.add_edge("photo_generate", "summarize")
    graph.set_finish_point("summarize")
    return graph.compile()

def load_state() -> HybridState:
    """
    Load saved state from disk. If the file does not exist,
    is malformed JSON, or fails validation, return a fresh state.
    """
    if not os.path.exists(SAVE_PATH):
        return HybridState()

    try:
        with open(SAVE_PATH, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        # file corrupt or unreadable
        return HybridState()

    # Ensure we at least have the required keys
    data.setdefault("input", "")
    data.setdefault("history", [])
    data.setdefault("memory_log", [])

    try:
        return HybridState(**data)
    except ValidationError:
        # data doesn’t match the model schema
        return HybridState()

def merge_state(state: HybridState, new_input: str) -> HybridState:
    """
    Append the new user input to history and set it as the current input.
    """
    state.input = new_input
    state.history.append(new_input)
    return state

def save_state(state: HybridState) -> None:
    """
    Persist the entire state back to disk as JSON.
    """
    # Convert to a serializable dict
    payload = state.dict()
    with open(SAVE_PATH, "w") as f:
        json.dump(payload, f, indent=2)