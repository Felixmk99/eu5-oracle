import chromadb
from pathlib import Path
from typing import Optional
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    SimpleDirectoryReader,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.postprocessor import FixedRecencyPostprocessor
from llama_index.core.llms import LLM
from datetime import datetime
import streamlit as st

def extract_metadata_from_file(file_path: Path) -> dict:
    """
    Helper function to extract the 'date' from the file content.
    Expects a line 'Ingestion Date: YYYY-MM-DD'
    """
    metadata = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if "Source Date:" in line:
                    date_str = line.split("Source Date:")[1].strip()
                    # Ensure it's stored as an ISO string for LlamaIndex to parse
                    metadata["date"] = date_str
                    break
    except Exception:
        pass
    
    # Fallback to file creation time if no date found
    if "date" not in metadata:
        metadata["date"] = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d')
        
    return metadata

class RAGEngine:
    """
    Manages the RAG pipeline using LlamaIndex and ChromaDB.
    Handles data indexing, persistence, and querying.
    """

    def __init__(self, data_dir: str, chroma_dir: str):
        """
        Initializes the RAG Engine paths.
        """
        self.data_dir = Path(data_dir)
        self.chroma_dir = Path(chroma_dir)
        self._db = chromadb.PersistentClient(path=str(self.chroma_dir))
        self._chroma_collection = self._db.get_or_create_collection("eu5_docs")

    def build_index(self) -> VectorStoreIndex:
        """
        Creates a new VectorStoreIndex from scratch.
        Uses SimpleDirectoryReader to load data and persists it to ChromaDB.
        """
        # 1. Load Documents
        documents = SimpleDirectoryReader(
            str(self.data_dir),
            file_metadata=extract_metadata_from_file
        ).load_data()
        
        # 2. Setup Vector Store & Storage Context
        vector_store = ChromaVectorStore(chroma_collection=self._chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 3. Create and return the index (it persists automatically via Chroma)
        index = VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )
        return index

    def load_index(self) -> VectorStoreIndex:
        """
        Loads the index from ChromaDB.
        OPTIMIZATION: Prioritizes speed. Only reads from disk if DB is empty.
        To force a refresh, the user should clear the DB or we can add a specific sync button later.
        """
        # 1. Setup Storage Context (Points to existing ChromaDB)
        vector_store = ChromaVectorStore(chroma_collection=self._chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # 2. Fast Path: If DB has data, load it directly without reading files
        if self._chroma_collection.count() > 0:
            return VectorStoreIndex.from_vector_store(
                vector_store, storage_context=storage_context
            )

        # 3. Slow Path: First time setup or empty DB
        documents = SimpleDirectoryReader(
            str(self.data_dir),
            file_metadata=extract_metadata_from_file
        ).load_data()
        
        return VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )

    def get_chat_engine(self, llm: LLM) -> any:
        """
        Returns a chat engine powered by the loaded/built index.
        Includes a Recency Postprocessor to prioritize newer information.
        """
        Settings.llm = llm
        index = self.load_index()
        
        # This postprocessor ranks nodes by date and keeps only the most recent N
        # We target the 'date' metadata field which we will populate during ingestion.
        recency_postprocessor = FixedRecencyPostprocessor(
            top_k=3, 
            date_key="date" # We'll ensure this key exists in metadata
        )

        return index.as_chat_engine(
            chat_mode="condense_question", 
            node_postprocessors=[recency_postprocessor],
            verbose=True
        )

@st.cache_resource(show_spinner="Waking up the Oracle...")
def get_cached_chat_engine(data_dir: str, chroma_dir: str, _llm: LLM) -> any:
    """
    Streamlit-friendly wrapper to cache the RAG chat engine.
    """
    engine = RAGEngine(data_dir, chroma_dir)
    return engine.get_chat_engine(_llm)
