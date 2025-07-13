from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

def build_qa_system(retriever):
    llm = ChatOpenAI(model_name="gpt-4", temperature=0.2)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
    return qa_chain
    
