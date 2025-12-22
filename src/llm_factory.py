import os
from typing import Optional
from llama_index.core.llms import LLM
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic
from llama_index.llms.ollama import Ollama

def get_llm(provider: str, model_name: str, api_key: Optional[str] = None) -> LLM:
    """
    Factory function to retrieve the requested LLM provider.

    Args:
        provider: The name of the provider ('OpenAI', 'Anthropic', 'Local (Ollama)').
        model_name: The specific model to use (e.g., 'gpt-4', 'claude-3-opus').
        api_key: Optional API key. If not provided, will look for env variables.

    Returns:
        An instance of the requested LLM class.

    Raises:
        ValueError: If the provider is unsupported or missing configuration.
    """
    if provider == "OpenAI":
        return OpenAI(model=model_name, api_key=api_key or os.getenv("OPENAI_API_KEY"))
    elif provider == "Anthropic":
        return Anthropic(model=model_name, api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
    elif provider == "Local (Ollama)":
        return Ollama(model=model_name, base_url="http://localhost:11434")
    else:
        raise ValueError(f"Unsupported provider: {provider}")
