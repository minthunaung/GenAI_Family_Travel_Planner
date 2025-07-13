import os

def load_documents_from_dir(folder_path: str) -> list:
    texts = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") or filename.endswith(".md"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                texts.append(f.read())
    return texts
    
