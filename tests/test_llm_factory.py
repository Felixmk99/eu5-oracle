import pytest
from unittest.mock import patch, MagicMock
from llm_factory import get_llm_model

def test_get_llm_model_ollama():
    """Test correctly instantiating Ollama model."""
    
    # We patch the class constructor to prevent real network calls/initialization
    with patch('llm_factory.Ollama') as MockOllama:
        llm = get_llm_model(model_name="llama3.1:8b")
        
        MockOllama.assert_called_once()
        # Verify args passed to Ollama constructor
        call_kwargs = MockOllama.call_args.kwargs
        assert call_kwargs['model'] == "llama3.1:8b"
        assert call_kwargs['request_timeout'] == 300.0
