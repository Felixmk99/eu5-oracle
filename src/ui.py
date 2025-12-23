import streamlit as st
import warnings
import importlib.metadata
import socket
import subprocess
import time
import os
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

# Direct imports to avoid "core_engine" singleton issues
from llm_factory import get_llm
from rag_engine import RAGEngine

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="EU5 Oracle",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Constants ---
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = str(ROOT_DIR / "data")
CHROMA_DIR = str(ROOT_DIR / "chroma_db")

# LLM Options
LLM_MODELS = {
    "Local (Ollama)": ["llama3.1:8b", "llama3.1:latest", "phi3", "mistral-nemo"],
    "Groq": ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768", "llama-3.1-70b-versatile"]
}

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

if "llm_config" not in st.session_state:
    st.session_state.llm_config = {"provider": None, "model": None}

# --- Helper Functions ---

@st.cache_resource(show_spinner="Loading Knowledge Base...")
def get_global_index():
    """
    Loads the RAG index FROM DISK only once.
    This object is shared across all sessions but is read-only safe.
    Does NOT trigger ingestion.
    """
    engine = RAGEngine(DATA_DIR, CHROMA_DIR)
    # This force-loads the index into memory/cache
    index = engine.load_index()
    return engine, index

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

def initialize_chat_session(provider: str, model_name: str, api_key: str = None):
    """
    Creates a user-specific Chat Engine using the globally cached Index + User-selected LLM.
    """
    try:
        # 1. Get the LLM (Fast)
        llm = get_llm(provider, model_name, api_key)
        
        # 2. Get the Cached Index (Instant)
        rag_engine, index = get_global_index()
        
        # 3. Create the Chat Engine (Lightweight)
        # We manually recreate the get_chat_engine logic here or use a helper,
        # but passing the llm into the engine class is cleaner.
        # But `rag_engine.py`'s get_chat_engine calls `load_index` internally, which is fine since it's cached.
        # Let's use the helper method on the engine instance but inject the pre-loaded index if possible?
        # Actually RAGEngine.get_chat_engine just sets Settings.llm and calls load_index().
        # Since load_index check DB count, it should be fast.
        
        st.session_state.chat_engine = rag_engine.get_chat_engine(llm)
        st.session_state.llm_config = {"provider": provider, "model": model_name}
        
        return True, f"Brain activated: {provider} / {model_name}"
    except Exception as e:
        return False, f"Failed to initialize: {e}"

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
    model_opts = LLM_MODELS.get(selected_provider, [])
    selected_model = st.selectbox(
        "Model Version",
        model_opts
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
                st.caption("🔑 Using key from environment")

    # 4. Status and Re-initialization
    st.divider()
    if st.session_state.chat_engine:
        st.success(f"🟢 Oracle Online")
        st.caption(f"Brain: {st.session_state.llm_config['model']}")
    else:
        st.error("🔴 Oracle Offline")
        if not server_running and selected_provider == "Local (Ollama)":
            st.warning(f"Ollama issue: {status_msg}")

    if st.button("Apply / Refresh"):
        if selected_provider != "Local (Ollama)" and not api_key:
            st.error(f"Cannot initialize {selected_provider} without an API key.")
        else:
            with st.spinner(f"Configuring {selected_provider}..."):
                success, msg = initialize_chat_session(selected_provider, selected_model, api_key)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

# --- AUTO-INITIALIZATION ---
# Automatically try to start if we are "offline" but have valid defaults
if st.session_state.chat_engine is None:
    should_auto_init = False
    
    # Auto-start Local if available
    if selected_provider == "Local (Ollama)" and server_running:
        should_auto_init = True
    # Auto-start Groq if Key is present
    elif selected_provider == "Groq" and api_key:
        should_auto_init = True
        
    if should_auto_init:
        # Silent init
        initialize_chat_session(selected_provider, selected_model, api_key)
        st.rerun()

# --- Main Interface ---
st.title("🌍 EU5 Oracle")
st.markdown("*Your strategic advisor for Project Caesar.*")

# Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask about estates, production, or control..."):
    if not st.session_state.chat_engine:
        st.warning("Oracle is offline. Please check configuration.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Consulting the archives..."):
                try:
                    # Stream response if possible (ChatEngine usually supports stream_chat)
                    # For simplicity/safety with current engine, we use .chat()
                    response = st.session_state.chat_engine.chat(prompt)
                    response_text = str(response)
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Error analyzing query: {e}")
