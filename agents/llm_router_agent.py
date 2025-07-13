import os
import openai
from langchain_core.prompts import ChatPromptTemplate # Import ChatPromptTemplate
from utils.config import OPENAI_API_KEY
from controller.shared_types import HybridState
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI 

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# --- LLM Router Agent ---
def llm_router_agent():
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
          You are a router. Given the user’s input, reply with exactly one of:
            - seed_data      → to update family members data to database
            - create_rag     → to upload trip pdf or html link                
            - fetch_family   → to start trip planning
            - extract_location  → to check weather
            - photo_memory   → to generate photo ideas
            - summarize      → for a fallback or summary
          Do not output anything else.
          """),
        ("user", "{input}")
    ])

    router_chain = prompt | llm | StrOutputParser()

    def _run(state: HybridState) -> HybridState:
        decision = router_chain.invoke({"input": state.input}).strip().lower()
        # write the decision back into your state
        state.next = decision
        return state
    return _run