import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv
from src.llm_factory import get_llm
from src.rag_engine import setup_rag_engine
from src.ingestion import load_documents_from_dir
from llama_index.core import Settings

# Load environment variables (API Keys)
load_dotenv()

def initialize_ui() -> None:
    """
    Sets up the Streamlit UI layout and session state.
    """
    st.set_page_config(page_title="EU5 Oracle", page_icon="📜")
    st.title("📜 Europa Universalis 5 Oracle")
    st.markdown("Your RAG-powered guide to Project Caesar.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

@st.cache_resource
def get_query_engine(provider: str, model: str, api_key: str):
    """
    Caches the LlamaIndex query engine to avoid redundant initializations.
    """
    # Configure the global settings with the selected LLM
    llm = get_llm(provider, model, api_key)
    Settings.llm = llm
    
    # In a real app, you'd handle loading existing data or triggering ingestion
    data_dir = str(Path(__file__).parent.parent / "data")
    persist_dir = str(Path(__file__).parent.parent / "chroma_db")
    
    # Load docs (placeholder if directory is empty)
    docs = load_documents_from_dir(data_dir)
    
    return setup_rag_engine(docs, persist_dir)

def main():
    initialize_ui()

    # Sidebar for Configuration
    with st.sidebar:
        st.header("Settings")
        provider = st.selectbox("LLM Provider", ["OpenAI", "Anthropic", "Local (Ollama)"])
        model = st.text_input("Model Name", value="gpt-3.5-turbo" if provider == "OpenAI" else "llama3")
        api_key = st.text_input("API Key", type="password") if provider != "Local (Ollama)" else ""
        
        if st.button("Initialize Engine"):
            try:
                engine = get_query_engine(provider, model, api_key)
                st.session_state.query_engine = engine
                st.success("Engine ready!")
            except Exception as e:
                st.error(f"Failed to initialize: {e}")

    # Chat Interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask about EU5..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        if "query_engine" in st.session_state:
            with st.chat_message("assistant"):
                response = st.session_state.query_engine.query(prompt)
                st.markdown(response.response)
                st.session_state.messages.append({"role": "assistant", "content": response.response})
        else:
            st.warning("Please initialize the engine in the sidebar first.")

if __name__ == "__main__":
    main()
