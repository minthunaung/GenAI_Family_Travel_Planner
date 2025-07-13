#Upload travel brouchers in PDF format and URL format from TripAdviser to rag
import sys
import os
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.rag_utils import ingest_documents

def create_rag():
    sources = [
        {"type": "pdf", "path": '/content/drive/MyDrive/Colab Notebooks/Emeritus_Generative_AI_Fundamentals_to_Advanced_Techniques_March_2025/Week13/family_travel_planner/travelguide/Americas_compressed.pdf'},
        {"type": "html", "url": "https://www.klook.com/en-SG/blog/cheapest-holidays-from-singapore/"}
    ]
    ingest_documents(sources, index_path="family_travel_rag.index")
    print("✅ RAG ingestion complete.")

create_rag()