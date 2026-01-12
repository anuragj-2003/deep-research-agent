import os
import shutil
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

from utils.config import EMBEDDINGS_MODEL, VECTOR_STORE_PATH

def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDINGS_MODEL)

def init_vector_store():
    """
    Initializes (or loads) the vector store.
    """
    embeddings = get_embeddings()
    if os.path.exists(VECTOR_STORE_PATH):
        try:
            return FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
        except:
             return FAISS.from_documents([Document(page_content="Initial")], embeddings)
    else:
        # Create empty or dummy
        return FAISS.from_documents([Document(page_content="Initial")], embeddings)

def add_to_vector_store(text_data: list[str], metadatas: list[dict] = None):
    """
    Adds texts to the vector store and saves it.
    """
    embeddings = get_embeddings()
    
    # Check if exists
    if os.path.exists(VECTOR_STORE_PATH):
         vectorstore = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
         vectorstore.add_texts(text_data, metadatas=metadatas)
    else:
         vectorstore = FAISS.from_texts(text_data, embeddings, metadatas=metadatas)
    
    vectorstore.save_local(VECTOR_STORE_PATH)

def query_vector_store(query: str, k: int = 5) -> str:
    """
    Queries the vector store and returns combined content.
    """
    if not os.path.exists(VECTOR_STORE_PATH):
        return ""
        
    embeddings = get_embeddings()
    vectorstore = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
    
    docs = vectorstore.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in docs])

def clear_vector_store():
    """
    Deletes the vector store directory.
    """
    if os.path.exists(VECTOR_STORE_PATH):
        shutil.rmtree(VECTOR_STORE_PATH)
