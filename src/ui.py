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

import os
from llm_factory import get_llm
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

# LLM Options
LLM_MODELS = {
    "Local (Ollama)": ["llama3.1:8b", "llama3.1:latest", "phi3"],
    "Groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "llama-3.1-70b-versatile"]
}

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

def initialize_brain(provider: str, model_name: str, api_key: str = None) -> tuple[bool, str]:
    """Sets up the LLM and RAG engine in session state."""
    try:
        # 1. Initialize the LLM & Embeddings
        import torch
        device = "mps" if torch.backends.mps.is_available() else "cpu"
        
        Settings.embed_model = HuggingFaceEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            device=device,
            embed_batch_size=32
        )
        
        # Get the LLM instance from our factory
        llm = get_llm(provider=provider, model_name=model_name, api_key=api_key)
        st.session_state.llm_instance = llm
        
        # 2. Ingest Core Knowledge Sources
        ingestor = DataIngestor(DATA_DIR)
        ingestor.ingest_core_knowledge()
        
        # 3. Get the Chat Engine
        # Note: We pass model_name to it to ensure cache busting when switching models
        st.session_state.chat_engine = get_cached_chat_engine(
            DATA_DIR, CHROMA_DIR, st.session_state.llm_instance, model_name
        )
        return True, f"Brain initialized with {provider} ({model_name})!"
    except Exception as e:
        return False, f"Initialization failed: {e}"

# --- Sidebar ---
server_running, status_msg = ensure_ollama_server()

with st.sidebar:
    st.title("⚙️ Brain Config")
    
    # 1. Provider Selection
    default_provider_index = 0 if server_running else 1 # Fallback to Groq if Ollama is not found
    
    selected_provider = st.selectbox(
        "LLM Provider",
        list(LLM_MODELS.keys()),
        index=default_provider_index,
        help="Local (Ollama) is private. Groq fallback is used if Ollama is not detected."
    )
    
    # 2. Model Selection
    selected_model = st.selectbox(
        "Model Version",
        LLM_MODELS[selected_provider]
    )
    
    # 3. API Key Management (Secure)
    api_key = None
    if selected_provider == "Groq":
        # Check Streamlit Secrets (Cloud) -> Environment Variables (.env) -> User Input
        if "GROQ_API_KEY" in st.secrets:
            api_key = st.secrets["GROQ_API_KEY"]
            st.caption("🔒 Using shared access key from Secrets.")
        else:
            api_key = os.getenv("GROQ_API_KEY")
            
            if not api_key:
                api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq API Key. This is not stored on our server.")
                if not api_key:
                    st.warning("Please enter a Groq API key to use cloud backup.")
            else:
                st.success("using GROQ_API_KEY from .env")

    # 4. Status and Re-initialization
    st.divider()
    if st.session_state.chat_engine:
        st.success(f"🟢 Oracle Online")
        st.caption(f"Provider: {selected_provider}")
        st.caption(f"Model: {selected_model}")
    else:
        st.error("🔴 Oracle Offline")
        if not server_running and selected_provider == "Local (Ollama)":
            st.warning(f"Ollama not detected. {status_msg}")

    if st.button("Apply / Refresh Engine"):
        if selected_provider != "Local (Ollama)" and not api_key:
            st.error(f"Cannot initialize {selected_provider} without an API key.")
        else:
            with st.spinner(f"Configuring {selected_provider}..."):
                success, message = initialize_brain(selected_provider, selected_model, api_key)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

# --- AUTO-INITIALIZATION ---
if st.session_state.chat_engine is None:
    # If Ollama is running OR we have an API key for the default fallback (Groq), try to auto-init
    should_auto_init = False
    init_provider = selected_provider
    init_model = selected_model
    init_key = api_key
    
    if selected_provider == "Local (Ollama)" and server_running:
        should_auto_init = True
    elif selected_provider != "Local (Ollama)" and api_key:
        should_auto_init = True
        
    if should_auto_init:
        with st.spinner(f"Auto-initializing {init_provider}..."):
            success, message = initialize_brain(init_provider, init_model, init_key)
            if success:
                st.toast(f"Switched to {init_provider}!", icon="🚀")
                st.rerun()
            else:
                st.error(message)

    if selected_provider == "Groq" and not api_key:
        st.info("💡 **Tip:** Get a free Groq API key at [console.groq.com](https://console.groq.com/)")


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
