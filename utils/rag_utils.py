import os
import pickle
import faiss
import numpy as np

from langchain_community.document_loaders import PyPDFLoader, UnstructuredURLLoader
#from langchain_community.text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.config import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

def ingest_documents(sources, index_path="family_travel_rag.index"):
    docs = []
    for src in sources:
        if src["type"] == "pdf":
            loader = PyPDFLoader(src["path"])
        else:
            loader = UnstructuredURLLoader([src["url"]])
        raw = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs.extend(splitter.split_documents(raw))

    embedder = OpenAIEmbeddings()
    vectors = embedder.embed_documents([d.page_content for d in docs])

    dim = len(vectors[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(vectors).astype("float32"))

    with open(index_path, "wb") as f:
        pickle.dump((index, docs), f)

def load_rag_index(index_path="family_travel_rag.index"):
    with open(index_path, "rb") as f:
        return pickle.load(f)  # returns (index, docs)
