import chromadb
from pathlib import Path
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    SimpleDirectoryReader,
    Settings
)
from llama_index.vector_stores.chroma import ChromaVectorStore
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
        txt_files = list(self.data_dir.glob("*.txt"))
        if not txt_files:
            txt_files = [p for p in self.data_dir.iterdir() if p.is_file() and not p.name.startswith(".")]

        documents = SimpleDirectoryReader(
            input_files=txt_files,
            file_metadata=extract_metadata_from_file
        ).load_data()
        
        return VectorStoreIndex.from_documents(
            documents, storage_context=storage_context
        )

    def get_chat_engine(self, llm: LLM) -> any:
        """
        Returns a chat engine powered by the loaded/built index.
        Uses optimized retrieval settings for better accuracy.
        Includes a Recency Postprocessor to prioritize newer information.
        """
        Settings.llm = llm
        index = self.load_index()
        
        # Recency postprocessor to prioritize recent information
        recency_postprocessor = FixedRecencyPostprocessor(
            top_k=3, 
            date_key="date"
        )

        return index.as_chat_engine(
            chat_mode="context",
            similarity_top_k=7,  # Increased from 5 for better context coverage
            node_postprocessors=[recency_postprocessor],
            system_prompt=(
                "You are the EU5 Oracle - an expert strategic advisor for Europa Universalis 5 (Project Caesar). "
                "Your role is to provide actionable, strategic gameplay advice based on the provided context.\n\n"
                
                "## Core Principles:\n"
                "1. STRATEGY FRAMEWORK: When giving advice, always consider:\n"
                "   - Short-term tactical goals (this war, this economy cycle)\n"
                "   - Long-term empire building (next 50 years of gameplay)\n"
                "   - Risk vs Reward (opportunity cost of decisions)\n"
                "2. EXPLAIN THE WHY: Don't just tell players what to do - explain the strategic reasoning\n"
                "3. TIERED ADVICE: Provide both beginner-friendly basics AND advanced tactics when relevant\n"
                "4. CONCRETE EXAMPLES: Use specific countries, mechanics, or scenarios to illustrate points\n\n"
                
                "## Answer Structure:\n"
                "- Start with a direct answer to the question\n"
                "- Follow with strategic context (why this matters in the bigger picture)\n"
                "- Provide actionable steps when applicable\n"
                "- Mention related mechanics or pitfalls to avoid\n\n"
                
                "## Knowledge Boundaries:\n"
                "- Base answers STRICTLY on the provided context (wiki docs, dev diaries, tutorials)\n"
                "- Prioritize the MOST RECENT information (EU5 is in active development - patch notes matter!)\n"
                "- If context doesn't contain the answer, admit 'I don't have information about X in my knowledge base' "
                "rather than hallucinating mechanics\n"
                "- Never confuse EU4 mechanics with EU5 - they are different games\n\n"
                
                "Remember: You're not just a documentation lookup tool - you're a strategic advisor helping players "
                "make better decisions and understand the deeper systems of EU5. Think like a grand strategy coach."
            ),
            verbose=False
        )

@st.cache_resource(show_spinner="Waking up the Oracle...")
def get_cached_chat_engine(data_dir: str, chroma_dir: str, _llm: LLM) -> any:
    """
    Streamlit-friendly wrapper to cache the RAG chat engine.
    """
    engine = RAGEngine(data_dir, chroma_dir)
    return engine.get_chat_engine(_llm)
