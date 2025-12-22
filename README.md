# EU5 Oracle 📜

A local-first RAG (Retrieval-Augmented Generation) chatbot for **Europa Universalis 5** (Project Caesar). Built with LlamaIndex, ChromaDB, and Streamlit.

## 🚀 Features
- **Multi-LLM Support**: Switch between OpenAI, Anthropic, and local Ollama.
- **Persistent Memory**: Uses ChromaDB to store and retrieve indexed dev diaries.
- **Beginner Friendly**: Clean, modular code designed for learning.

## 🛠️ Setup Instructions

### 1. Environment Configuration
Create a `.env` file in the root directory and add your API keys:
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
streamlit run src/ui.py
```

## 📁 Project Structure
- `data/`: Raw `.txt` files for ingestion.
- `chroma_db/`: Local vector database storage.
- `src/`:
  - `llm_factory.py`: Handles model instantiation.
  - `ingestion.py`: Scrapes and loads documents.
  - `rag_engine.py`: Core LlamaIndex logic.
  - `ui.py`: Streamlit frontend.
