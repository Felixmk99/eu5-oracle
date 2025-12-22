# EU5 Oracle 🌍

The **EU5 Oracle** is a local-first RAG (Retrieval-Augmented Generation) chatbot designed to help you explore and understand information about **Project Caesar** (Europa Universalis 5). 

Built for the Paradox community, it allows you to ingest developer diaries, forum posts, and YouTube transcripts to create a searchable mathematical index of all known information.

## 🚀 How to Install

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/eu5-oracle.git
   cd eu5-oracle
   ```

2. **Set up a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory for your API keys (optional if using Local models):
   ```env
   OPENAI_API_KEY=your_openai_key
   ANTHROPIC_API_KEY=your_anthropic_key
   ```

## 📥 How to Scrape Data

You can add knowledge to the Oracle directly through the web interface:

1. Launch the app (see below).
2. In the **Knowledge Ingestion** section of the sidebar, paste a URL:
   - **Forums/Wikis**: Paste a link to a dev diary or wiki page.
   - **YouTube**: Paste a link to a Tinto Talk or interview.
3. Click **"Ingest Knowledge"**. The text will be saved to the `data/` folder and indexed.

## 💬 How to Chat

1. **Launch the App**:
   ```bash
   streamlit run src/ui.py
   ```
2. **Configure the Brain**:
   - In the sidebar, select your AI Provider.
   - Click **"Initialize Brain"**.
3. **Ask Away**: Use the chat input at the bottom to ask things like:
   - *"How does the population system work?"*
   - *"What are the mechanics for diplomacy?"*

## 🧠 Supported Models

The EU5 Oracle uses a **Factory Pattern**, allowing you to switch between different "Brains" seamlessly:

- **OpenAI**: Uses `gpt-4o` for high-reasoning capabilities. Requires an API key.
- **Anthropic**: Uses `claude-3-5-sonnet` for nuanced understanding. Requires an API key.
- **Local (Ollama)**: **CRITICAL for local-first privacy.** 
  - Install [Ollama](https://ollama.com/).
  - Run `ollama pull llama3`.
  - Select "Local (Ollama)" in the sidebar and click "Initialize". No internet or API key required!

---
*Disclaimer: This is a fan-made tool. "Europa Universalis 5" and "Project Caesar" are trademarks of Paradox Interactive.*
