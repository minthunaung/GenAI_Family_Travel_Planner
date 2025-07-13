# create_rag_agent.py

import json
import openai
from openai import ChatCompletion
from langchain_core.prompts import ChatPromptTemplate
from typing import Any, Dict, List
from controller.shared_types import HybridState
from utils.config    import OPENAI_API_KEY
from utils.rag_utils import ingest_documents


openai.api_key = OPENAI_API_KEY

def create_rag_agent(RAG_INDEX_PATH="family_travel_rag.index"):
    """
    Agent that:
      • Reads state.input (free-form request to ingest PDF(s) and/or URL(s))
      • Uses ChatCompletion to parse it into a JSON list of sources:
          [{"type":"pdf","path":"/path/to/file.pdf"},
           {"type":"html","url":"https://example.com"}]
      • Calls ingest_documents(...) to build the RAG index
      • Sets state.output to a success/failure message
    """
    def _run(state: HybridState) -> HybridState:
        # 1) Prompt the LLM to extract JSON‐formatted sources
        prompt = (
            "I will give you a free-form instruction to ingest travel brochures.\n"
            f"Instruction:\n\"{state.input}\"\n\n"
            "Extract a JSON array of objects, each with:\n"
            "- type: either \"pdf\" or \"html\"\n"
            "- path: absolute filesystem path if pdf\n"
            "- url: full URL if html\n\n"
            "Return ONLY valid JSON. Example:\n"
            "[{"
            "\"type\":\"pdf\",\"path\":\"/content/docs/guide.pdf\""
            "}, {"
            "\"type\":\"html\",\"url\":\"https://tripadvisor.com/...\""
            "}]"
        )

        try:
            resp = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role":"user","content": prompt}],
                temperature=0
            )
            json_text: str = resp.choices[0].message.content.strip()
            sources: List[Dict[str, Any]] = json.loads(json_text)
        except Exception as e:
            state.output = f"❌ Failed to parse sources: {e}"
            print(state.output)
            return state

        # 2) Call your ingestion util
        try:
            ingest_documents(sources, index_path=RAG_INDEX_PATH)
        except Exception as e:
            state.output = f"❌ RAG ingestion error: {e}"
            print(state.output)
            return state

        # 3) Confirm success
        count = len(sources)
        state.output = f"✅ Ingested {count} source{'s' if count!=1 else ''} into RAG index."
        print(state.output)
        return state

    return _run