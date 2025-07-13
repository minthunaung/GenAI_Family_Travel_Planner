from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter

def create_retriever(doc_texts: list) -> FAISS:
    embedding = OpenAIEmbeddings()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = [chunk for doc in doc_texts for chunk in splitter.split_text(doc)]
    return FAISS.from_texts(chunks, embedding)
