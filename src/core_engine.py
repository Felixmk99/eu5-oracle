import os
import torch
from pathlib import Path
from typing import Optional, Tuple
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llm_factory import get_llm
from rag_engine import RAGEngine
from ingestion import DataIngestor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Constants ---
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = str(ROOT_DIR / "data")
CHROMA_DIR = str(ROOT_DIR / "chroma_db")

class OracleCore:
    """
    Central engine for the EU5 Oracle. 
    Handles LLM initialization and RAG query processing.
    Shared between Streamlit UI and Native Overlay.
    """
    
    def __init__(self):
        self.chat_engine = None
        self.llm_instance = None
        self._initialize_settings()

    def _initialize_settings(self):
        """Initializes global LlamaIndex settings (Embeddings)."""
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            device=device,
            embed_batch_size=32
        )

    def initialize_engine(self, provider: str, model_name: str, api_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Initializes the LLM and the Chat Engine.
        """
        try:
            # 1. Get LLM
            self.llm_instance = get_llm(provider=provider, model_name=model_name, api_key=api_key)
            
            # 2. Ensure data is ingested (fast if already done)
            ingestor = DataIngestor(DATA_DIR)
            ingestor.ingest_core_knowledge()
            
            # 3. Setup RAG Engine
            engine = RAGEngine(DATA_DIR, CHROMA_DIR)
            self.chat_engine = engine.get_chat_engine(self.llm_instance)
            
            return True, f"Oracle initialized with {provider} ({model_name})!"
        except Exception as e:
            return False, f"Engine initialization failed: {e}"

    def query(self, prompt: str) -> str:
        """Sends a query to the Oracle and returns the response text."""
        if not self.chat_engine:
            return "Oracle is not initialized. Please connect a brain first."
        
        try:
            response = self.chat_engine.chat(prompt)
            return str(response)
        except Exception as e:
            return f"Error during query: {e}"

# Singleton instance for consistent use within a process
oracle_core = OracleCore()
