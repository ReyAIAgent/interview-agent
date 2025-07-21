#from langchain.document_loaders import UnstructuredFileLoader
from langchain.document_loaders import PyPDFLoader, TextLoader
import os

def parse_document(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")
    
    pages = loader.load()
    return "\n".join(page.page_content for page in pages)


