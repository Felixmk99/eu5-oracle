from llama_index.llms.ollama import Ollama
from llama_index.llms.groq import Groq
from llama_index.core.llms import LLM
from typing import Optional
import os

def get_llm(provider: str, model_name: str, api_key: Optional[str] = None) -> LLM:
    """
    Simplified factory for EU5 Oracle. Supports Local (Ollama) and Groq.
    
    Args:
        provider: 'Local (Ollama)' or 'Groq'.
        model_name: The model ID to use.
        api_key: Groq API key (optional if set in environment).
    """
    if provider == "Local (Ollama)":
        return Ollama(model=model_name, base_url="http://localhost:11434", request_timeout=300.0)
    
    if provider == "Groq":
        # Prioritize passed key, then env var
        g_key = api_key or os.getenv("GROQ_API_KEY")
        if not g_key:
            raise ValueError("Groq API Key not found in environment or arguments.")
        return Groq(model=model_name, api_key=g_key)
    
    raise ValueError(f"Oracle does not support: {provider}. Use 'Local (Ollama)' or 'Groq'.")
