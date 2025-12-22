import streamlit as st

import warnings
import importlib.metadata
import socket
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv

# Compatibility fix for Python < 3.10
try:
    if not hasattr(importlib.metadata, 'packages_distributions'):
        import importlib_metadata
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
except ImportError:
    pass

# Suppress Pydantic and LlamaIndex noise
warnings.filterwarnings("ignore", module="pydantic")
warnings.filterwarnings("ignore", module="llama_index")

from llm_factory import get_llm_model
from rag_engine import get_cached_chat_engine
from ingestion import DataIngestor
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="EU5 Oracle",
    page_icon="🌍",
    layout="wide"
)

# --- Constants ---
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = str(ROOT_DIR / "data")
CHROMA_DIR = str(ROOT_DIR / "chroma_db")
OLLAMA_MODEL = "llama3.1:8b"

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

if "llm_instance" not in st.session_state:
    st.session_state.llm_instance = None

# --- Helper Functions ---

@st.cache_resource
def ensure_ollama_server():
    """Checks if Ollama is running locally, and auto-starts it if dead."""
    def is_port_open(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            return s.connect_ex(('localhost', port)) == 0

    if is_port_open(11434):
        return True, "Ollama is already running."

    # Attempts to start Ollama
    try:
        # Run in background, suppress output
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for it to spin up (max 10s)
        for _ in range(20): 
            if is_port_open(11434):
                return True, "Ollama auto-started successfully 🦙"
            time.sleep(0.5)
        
        return False, "Ollama command ran but server didn't respond (Timeout)."
    except FileNotFoundError:
        return False, "Ollama not found! Please download it from ollama.com"
    except Exception as e:
        return False, f"Failed to start Ollama: {e}"

def initialize_brain():
    """Sets up the LLM and RAG engine in session state."""
    try:
        # 1. Initialize the LLM & Embeddings (Local-First)
        import torch
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            device=device,
            embed_batch_size=32  # Optimization: Increase batch size for faster processing
        )
        llm = get_llm_model(model_name=OLLAMA_MODEL)
        st.session_state.llm_instance = llm
        
        # 2. Ingest Core Knowledge Sources
        # This will skip if files already exist, so it's fast
        ingestor = DataIngestor(DATA_DIR)
        ingestor.ingest_core_knowledge()
        
        # 3. Get the Chat Engine
        st.session_state.chat_engine = get_cached_chat_engine(
            DATA_DIR, CHROMA_DIR, st.session_state.llm_instance
        )
        return True, "Brain initialized successfully!"
    except Exception as e:
        return False, f"Initialization failed: {e}"

# --- AUTO-INITIALIZATION ---
if st.session_state.chat_engine is None:
    # 1. Ensure Ollama is running
    server_running, status_msg = ensure_ollama_server()
    
    if not server_running:
        st.error(f"❌ {status_msg}")
        st.info("⚠️ Action Required: Please verify Ollama is installed.")
    else:
        if "auto-started" in status_msg:
            st.toast(status_msg, icon="🦙")

        # 2. Initialize Brain
        with st.spinner(f"Connecting to Local Brain ({OLLAMA_MODEL})..."):
            success, message = initialize_brain()
            if success:
                st.toast("Ready to chat!", icon="🟢")
            else:
                st.error(message)

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Status")
    
    if st.session_state.chat_engine:
        st.success("🟢 Oracle Online")
        st.caption(f"Model: Local {OLLAMA_MODEL}")
    else:
        st.error("🔴 Oracle Offline")
        if st.button("Retry Connection"):
            st.rerun()


# --- Main Interface ---
st.title("🌍 EU5 Oracle")
st.markdown("*Your private, local expert on Europa Universalis V.*")

# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about Europa Universalis V..."):
    if not st.session_state.chat_engine:
        st.warning("Oracle is offline. Please check Ollama.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_engine.chat(prompt)
                    response_text = str(response)
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Error: {e}")
