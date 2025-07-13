import numpy as np
from langchain.embeddings.openai import OpenAIEmbeddings
import openai
from openai import ChatCompletion
from utils.rag_utils import load_rag_index
from utils.config import OPENAI_API_KEY
from controller.shared_types import HybridState

import os
from langchain_core.prompts import ChatPromptTemplate # Import ChatPromptTemplate

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def rag_retrieval_agent(index_path="family_travel_rag.index", k=5):
    #index_path = parent_dir+"/"+index_path
    index, docs = load_rag_index(index_path)

    embedder = OpenAIEmbeddings()

    def _run(state: HybridState) -> HybridState:
        query = state.selected_activity
        q_vec = np.array(embedder.embed_query(query)).astype("float32")
        distances, I = index.search(q_vec.reshape(1, -1), k)
        state.rag_context = [docs[i].page_content for i in I[0]]
        return state
    return _run
    
def rag_recommendation_agent():
    def _run(state: HybridState) -> HybridState:
        ctx = "\n\n".join(state.rag_context or [])
        prompt = (
            f"Based on these documents:\n{ctx}\n\n"
            f"Recommend 1 family-friendly destinations or activities "
            f"related to '{state.selected_activity}'."
        )

        # Explicitly use openai.ChatCompletion
        openai.api_key = OPENAI_API_KEY
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role":"user","content":prompt}],
            temperature=0.7
        )

        state.recommendations = resp.choices[0].message.content
        return state

    return _run
