import sys
import os
import pytest
from pathlib import Path

# Add src to python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def temp_data_dir(tmp_path):
    """Fixture that provides a temporary directory for data storage."""
    d = tmp_path / "data"
    d.mkdir()
    return d

@pytest.fixture
def temp_chroma_dir(tmp_path):
    """Fixture that provides a temporary directory for chroma db."""
    d = tmp_path / "chroma_db"
    d.mkdir()
    return d
