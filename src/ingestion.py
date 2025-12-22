import pathlib
from typing import List
from llama_index.core import Document, SimpleDirectoryReader
import requests
from bs4 import BeautifulSoup

def scrape_url_to_file(url: str, output_path: pathlib.Path) -> None:
    """
    Scrapes a static URL and saves the text content to a local file.
    Always saves to data/ before processing to ensure a backup exists.

    Args:
        url: The URL to scrape.
        output_path: The filesystem path where the text should be saved.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Simple extraction logic - can be refined based on EU5 dev diary structure
        text = soup.get_text(separator='\n', strip=True)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")

def load_documents_from_dir(data_dir: str) -> List[Document]:
    """
    Loads documents from the specified directory using SimpleDirectoryReader.

    Args:
        data_dir: Path to the directory containing raw .txt files.

    Returns:
        A list of LlamaIndex Document objects.
    """
    reader = SimpleDirectoryReader(input_dir=data_dir)
    return reader.load_data()
