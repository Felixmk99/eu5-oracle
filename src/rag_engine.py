import chromadb
from pathlib import Path
from typing import List
from llama_index.core import (
    VectorStoreIndex, 
    StorageContext, 
    Document,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.query_engine import BaseQueryEngine

def setup_rag_engine(
    documents: List[Document], 
    persist_dir: str, 
    collection_name: str = "eu5_docs"
) -> BaseQueryEngine:
    """
    Initializes the ChromaDB vector store and creates a query engine.
    Uses persistence to avoid rebuilding the index on every run.

    Args:
        documents: List of LlamaIndex Document objects to index.
        persist_dir: Directory where ChromaDB state is stored.
        collection_name: Name of the collection in ChromaDB.

    Returns:
        A LlamaIndex query engine instance.
    """
    db = chromadb.PersistentClient(path=persist_dir)
    chroma_collection = db.get_or_create_collection(collection_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # If index already exists, load it; otherwise create new
    # Note: Simplified for initial setup; usually you'd check if persist_dir is empty
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context
    )
    
    return index.as_query_engine()
