import pytest
from pathlib import Path
import sys
import os

# Add src to python path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ingestion import CORE_WIKI_URLS, DataIngestor

def test_core_knowledge_completeness():
    """
    Integration Test: Checks if all URLs defined in CORE_WIKI_URLS 
    have a corresponding .txt file in the data/ directory.
    """
    # Assuming the test is running from the project root or tests/ dir
    # We locate the actual real data directory relative to this test file
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    # We use the actual Ingram class just to access the helper method
    ingestor = DataIngestor(str(data_dir))
    
    missing_files = []
    
    for url in CORE_WIKI_URLS:
        slug = url.split("/")[-1].split("?")[0]
        if not slug or slug == "index.php":
            slug = "wiki_index" # matching logic in ingestion.py
            
        expected_filename = ingestor._sanitize_filename(slug) + ".txt"
        expected_path = data_dir / expected_filename
        
        if not expected_path.exists():
            missing_files.append(f"{url} -> {expected_filename}")
            
    # Assert
    assert len(missing_files) == 0, f"Found {len(missing_files)} missing data files:\n" + "\n".join(missing_files[:10]) + "\n...(truncated)"
