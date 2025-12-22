import streamlit as st
import os
import warnings
import importlib.metadata
try:
    if not hasattr(importlib.metadata, 'packages_distributions'):
        import importlib_metadata
        importlib.metadata.packages_distributions = importlib_metadata.packages_distributions
except ImportError:
    pass

from pathlib import Path
from dotenv import load_dotenv

# Suppress Pydantic and LlamaIndex noise (Cosmetic fix)
warnings.filterwarnings("ignore", module="pydantic")
warnings.filterwarnings("ignore", module="llama_index")
from llm_factory import get_llm_model
from rag_engine import get_cached_chat_engine
from ingestion import DataIngestor

# Load environment variables (Security First)
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="EU5 Oracle",
    page_icon="🌍",
    layout="wide"
)

# --- Constants (Robust Absolute Paths) ---
ROOT_DIR = Path(__file__).parent.parent.absolute()
DATA_DIR = str(ROOT_DIR / "data")
CHROMA_DIR = str(ROOT_DIR / "chroma_db")

# --- Session State Management ---
# Memory to stop the bot from resetting every rerun
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_engine" not in st.session_state:
    st.session_state.chat_engine = None

if "llm_instance" not in st.session_state:
    st.session_state.llm_instance = None

import socket
import subprocess
import time

# --- Reusable Initialization Logic ---
@st.cache_resource
def ensure_ollama_server():
    """Checks if Ollama is running, locally, and auto-starts it if dead."""
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
        return False, "Ollama not found. Is it installed?"
    except Exception as e:
        return False, f"Failed to start Ollama: {e}"

def initialize_brain(provider, api_key, model_name, base_url=None):
    """Sets up the LLM and RAG engine in session state."""
    try:
        # 1. Initialize the LLM via Factory
        llm = get_llm_model(provider, api_key, model_name, base_url)
        st.session_state.llm_instance = llm
        
        # 2. Ingest Core Knowledge Sources (Background)
        ingestor = DataIngestor(DATA_DIR)
        ingestor.ingest_core_knowledge()
        
        # 3. Get the Chat Engine (Cached for performance)
        st.session_state.chat_engine = get_cached_chat_engine(
            DATA_DIR, CHROMA_DIR, st.session_state.llm_instance
        )
        return True, f"{provider} Brain initialized successfully!"
    except ValueError as ve:
        return False, str(ve)
    except Exception as e:
        return False, f"Initialization failed: {e}"

# --- AUTO-INITIALIZATION (The Quality of Life Fix) ---
if st.session_state.chat_engine is None:
    # Logic: Attempt to wake up the Oracle automatically
    # Check if we have any cloud keys first
    cloud_keys = [os.getenv("OPENAI_API_KEY"), os.getenv("GEMINI_API_KEY"), os.getenv("ANTHROPIC_API_KEY")]
    
    if not any(cloud_keys):
        # If no cloud keys, default to Local Ollama (with Auto-Start!)
        server_running, status_msg = ensure_ollama_server()
        if not server_running:
            st.error(status_msg)
        else:
            if "auto-started" in status_msg:
                st.toast(status_msg, icon="🦙")
                
            with st.spinner("Oracle is waking up (Local Ollama)..."):
                success, message = initialize_brain("Local (Ollama)", None, "llama3.1")
                if success: st.toast(message, icon="🧠")
    else:
        # Check cloud keys in order of preference
        potential_providers = [
            ("OPENAI_API_KEY", "OpenAI", "gpt-4o"),
            ("GEMINI_API_KEY", "Gemini", "gemini-1.5-pro"),
            ("ANTHROPIC_API_KEY", "Anthropic", "claude-3-5-sonnet")
        ]
        for env_var, prov_name, def_model in potential_providers:
            key = os.getenv(env_var)
            if key:
                with st.spinner(f"Oracle is waking up ({prov_name})..."):
                    success, message = initialize_brain(prov_name, key, def_model)
                    if success: 
                        st.toast(message, icon="🧠")
                        break

# --- Sidebar Configuration (Control Panel) ---
with st.sidebar:
    st.title("⚙️ Control Panel")
    
    # Status Indicator
    if st.session_state.chat_engine:
        st.success("🟢 Oracle Online")
    else:
        st.warning("🔴 Oracle Offline")

    provider = st.selectbox(
        "Choose AI Provider", 
        [
            "Local (Ollama)",
            "OpenAI", 
            "Anthropic", 
            "Gemini", 
            "Mistral", 
            "Groq", 
            "Custom (OpenAI-Compatible)"
        ]
    )
    
    # Only show API key input for cloud/custom providers
    api_key = ""
    env_var_name = f"{provider.split(' ')[0].upper()}_API_KEY"
    env_key = os.getenv(env_var_name, "")
    
    if provider not in ["Local (Ollama)"]:
        api_key = st.text_input(
            f"{provider} API Key", 
            type="password",
            value=env_key
        )
    
    # Custom Base URL for OpenAI-compatible APIs (like Groq, Together, etc.)
    base_url = None
    if provider == "Custom (OpenAI-Compatible)":
        base_url = st.text_input("Base URL", placeholder="https://api.yourprovider.com/v1")
    
    # Set dynamic defaults for Model Name
    model_defaults = {
        "Local (Ollama)": "llama3.1",
        "OpenAI": "gpt-4o",
        "Anthropic": "claude-3-5-sonnet",
        "Gemini": "gemini-1.5-pro",
        "Mistral": "mistral-large-latest",
        "Groq": "llama-3.1-70b-versatile",
        "Custom (OpenAI-Compatible)": "custom-model"
    }
    
    model_name = st.text_input("Model Name", value=model_defaults.get(provider, ""))
    
    if st.button("Initialize Brain"):
        success, message = initialize_brain(provider, api_key, model_name, base_url)
        if success:
            st.success(message)
        else:
            st.error(message)

    st.divider()
    
    st.title("📥 Additional Knowledge")
    st.caption("Use this to feed specific files or videos to the Oracle.")
    source_url = st.text_input("Enter URL (Forum or YouTube)")
    if st.button("Ingest Additional Knowledge"):
        ingestor = DataIngestor(DATA_DIR)
        with st.spinner("Writing to memory..."):
            success = False
            if "youtube.com" in source_url or "youtu.be" in source_url:
                success = ingestor.get_youtube_transcript(source_url)
            else:
                success = ingestor.scrape_url(source_url)
            
            if success:
                st.success("Knowledge stored! Reset the app to re-index new data.")
            else:
                st.error("Failed to ingest knowledge.")

# --- Main Chat Interface ---
st.title("🌍 EU5 Oracle")
st.markdown("*Your senior-grade guide to Project Caesar (Europa Universalis 5)*")

# 1. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Get User Input
if prompt := st.chat_input("Ask about Project Caesar..."):
    if not st.session_state.chat_engine:
        st.warning("Please initialize the brain in the sidebar first!")
    else:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 3. Generate Response
        with st.chat_message("assistant"):
            with st.spinner("Consulting the archives..."):
                try:
                    # Pass text to chat_engine.chat()
                    response = st.session_state.chat_engine.chat(prompt)
                    response_text = str(response)
                    st.markdown(response_text)
                    
                    # Store assistant message in history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                except Exception as e:
                    st.error(f"Chat error: {e}")

# --- Footer ---
st.divider()
st.caption("EU5 Oracle | Powered by LlamaIndex, ChromaDB, and Streamlit.")
