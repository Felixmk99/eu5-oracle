from typing import Optional, Dict, Any
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama
from llama_index.llms.gemini import Gemini
from llama_index.llms.mistralai import MistralAI
from llama_index.llms.groq import Groq
import streamlit as st

def get_llm_model(
    provider: str, 
    api_key: Optional[str] = None, 
    model_name: Optional[str] = None,
    base_url: Optional[str] = None
) -> LLM:
    """
    Factory function to generate LLM instances based on the selected provider.
    This pattern allows the application to be truly model-agnostic.

    Args:
        provider (str): The AI provider ('OpenAI', 'Anthropic', 'Gemini', 'Mistral', 'Groq', 'Local (Ollama)', 'Custom').
        api_key (str, optional): The API key for the provider.
        model_name (str, optional): The specific model name to use.
        base_url (str, optional): Custom endpoint for OpenAI-compatible APIs.

    Returns:
        LLM: An instance of a LlamaIndex LLM class.
    """
    # Helper to validate common keys
    def validate_key(key: Optional[str]):
        if not key or key.strip() == "":
            raise ValueError(f"API Key is required for provider: {provider}")

    if provider == "OpenAI":
        validate_key(api_key)
        return OpenAI(model=model_name or "gpt-4o", api_key=api_key)
    
    elif provider == "Anthropic":
        validate_key(api_key)
        return Anthropic(model=model_name or "claude-3-5-sonnet", api_key=api_key)
    
    elif provider == "Gemini":
        validate_key(api_key)
        return Gemini(model=f"models/{model_name or 'gemini-1.5-pro'}", api_key=api_key)

    elif provider == "Mistral":
        validate_key(api_key)
        return MistralAI(model=model_name or "mistral-large-latest", api_key=api_key)

    elif provider == "Groq":
        validate_key(api_key)
        return Groq(model=model_name or "llama-3.1-70b-versatile", api_key=api_key)
    
    elif provider == "Local (Ollama)":
        return Ollama(model=model_name or "llama3.1", request_timeout=60.0)
    
    elif provider == "Custom (OpenAI-Compatible)":
        validate_key(api_key)
        if not base_url:
            raise ValueError("Base URL is required for Custom OpenAI-compatible provider.")
        return OpenAI(model=model_name or "custom-model", api_key=api_key, api_base=base_url)
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")
