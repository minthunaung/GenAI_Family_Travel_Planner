import os
import openai
from utils.config import OPENAI_API_KEY
from langchain_core.prompts import ChatPromptTemplate

openai.api_key = OPENAI_API_KEY

def recommend(prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        temperature=0.7
    )
    return resp.choices[0].message.content
