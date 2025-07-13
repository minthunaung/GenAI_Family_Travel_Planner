import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from utils.config import DB_PATH, RAG_INDEX_PATH, WEATHER_API_KEY, OPENAI_API_KEY
from controller.shared_types import HybridState
from langchain_core.prompts import ChatPromptTemplate 
from langchain_core.output_parsers import StrOutputParser

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def extract_location_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Extract exactly one place name from the user’s query. If none, return an empty string."),
        ("user",   "{input}")
    ])
    chain = prompt | llm | StrOutputParser()
    def _run(s: HybridState) -> HybridState:
        place = chain.invoke({"input": s.recommendations}).strip()
        if not place:
          place =chain.invoke({"input": s.input}).strip()
        s.location= place
        return s
    return _run