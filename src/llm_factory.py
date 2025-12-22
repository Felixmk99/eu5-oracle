from llama_index.llms.ollama import Ollama
from llama_index.core.llms import LLM

def get_llm_model(model_name: str = "llama3.1", base_url: str = "http://localhost:11434") -> LLM:
    """
    Returns the Local Ollama LLM.
    
    Args:
        model_name: The name of the model to use (default: llama3.1)
        base_url: The URL of the Ollama server (default: http://localhost:11434)
    """
    return Ollama(model=model_name, base_url=base_url, request_timeout=300.0)
