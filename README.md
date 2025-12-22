# EU5 Oracle 🌍
### Your Private, Local Expert on Project Caesar

The **EU5 Oracle** is a 100% local, offline-capable RAG (Retrieval-Augmented Generation) chatbot designed to help you explore and understand information about **Project Caesar** (Europa Universalis 5).

Built for the Paradox community, it ingests developer diaries, wiki pages, and YouTube transcripts to create a searchable index of all known information, powered entirely by your local machine.

## 🌟 Features

*   **100% Local & Private**: Powered by [Ollama](https://ollama.com/) and local embeddings. No API keys, no clouds, no data leaves your PC.
*   **Smart Ingestion**: Automatically scrapes and cleans text from the EU5 Wiki and YouTube transcripts.
*   **Vector Search**: Uses ChromaDB to find the exact paragraphs relevant to your question.
*   **Instant Context**: Answers questions like *"How does the population system work?"* with cited sources.

## 🛠 Prerequisites

1.  **Python 3.9+** installed.
2.  **[Ollama](https://ollama.com/)** installed and running.
    *   You must have the `llama3.1` model pulled:
        ```bash
        ollama pull llama3.1
        ```

## 🚀 Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/eu5-oracle.git
    cd eu5-oracle
    ```

2.  **Set up a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: This project uses specific pinned versions of LlamaIndex and Torch to ensure stability.*

## 💬 How to Run

1.  **Start the App**:
    ```bash
    streamlit run src/ui.py
    ```

2.  **Auto-Initialization**:
    *   The app will automatically check if Ollama is running (and try to start it if not).
    *   It will connect to your local `llama3.1` model.
    *   It will check your `data/` folder and build the brain if needed.

3.  **Chat**:
    *   Simply type your question! e.g., *"What are the mechanics for diplomacy?"*

## 📥 Adding Knowledge

To make the Oracle smarter:
1.  **Wiki/Forum**: Paste a URL into the "Knowledge Base" field in the sidebar and click **Ingest**.
2.  **Manual Files**: Drop any `.txt` file (e.g., transcripts) into the `manual_sources/` folder and restart the app.

## 🧪 How to Test

This project includes a comprehensive test suite using `pytest`.

1.  **Run all tests**:
    ```bash
    pytest tests/ -v
    ```

---
*Disclaimer: This is a fan-made tool. "Europa Universalis 5" and "Project Caesar" are trademarks of Paradox Interactive.*
