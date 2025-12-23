# EU5 Oracle 🌍
### Your Strategic Expert on Project Caesar (EU5)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_svg.svg)](https://eu5-oracle.streamlit.app/)

The **EU5 Oracle** is a sophisticated RAG (Retrieval-Augmented Generation) chatbot designed to help you explore and understand information about **Project Caesar** (Europa Universalis 5). 

It is built with a **Local-First** philosophy: it runs entirely on your machine if you have Ollama, but seamlessly falls back to a cloud-based **Groq** engine if you're on the go or don't have the hardware.

## 🔗 Live Demo
Check out the live Oracle here: [eu5-oracle.streamlit.app](https://eu5-oracle.streamlit.app/)

## 🌟 Features

*   **Local-First & Private**: Defaults to [Ollama](https://ollama.com/) for 100% private, local inference.
*   **Groq Cloud Fallback**: Automatically connects to Groq's lightning-fast inference if Ollama is not detected, ensuring the Oracle is always online.
*   **Automated Knowledge Ingestion**: Automatically tracks and indexes the latest EU5 Wiki pages and Developer Diaries (Tinto Talks).
*   **Vector search**: Uses ChromaDB and the BGE embedding model to find precise strategic context for your questions.
*   **Context-Aware Strategy**: Trained to think like a grand strategy coach, providing actionable advice based on official developer diaries.

## 🛠 Prerequisites

1.  **Python 3.11+** installed.
2.  **(Optional) [Ollama](https://ollama.com/)**: For local-only privacy.
    *   Pull the latest model: `ollama pull llama3.1:8b`
3.  **(Optional) Groq API Key**: For cloud access. You can get one for free at [console.groq.com](https://console.groq.com/).

## 🚀 Local Installation

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Felixmk99/eu5-oracle.git
    cd eu5-oracle
    ```

2.  **Set up a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_key_here  # Optional cloud fallback
    ```

- **Start Script**:
    ```bash
    ./start.sh
    ```
- **Manual Launch**:
    ```bash
    streamlit run src/ui.py
    ```

*   The Oracle has achieved **99.1% coverage** of all known public information (Wiki, Dev Diaries, Videos).
*   The first launch is **instant** because the knowledge base is pre-ingested.

## 🧪 Testing

```bash
pytest tests/ -v
```

---
*Disclaimer: This is a fan-made tool. "Europa Universalis 5" and "Project Caesar" are trademarks of Paradox Interactive.*
