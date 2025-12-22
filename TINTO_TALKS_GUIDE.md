# 📥 How to Add Tinto Talks to EU5 Oracle

## ⚠️ Important: Paradox Forum Requires Manual Input

The Paradox forum uses Cloudflare protection and JavaScript rendering, making automatic scraping impossible. 

**Solution: Manual Copy-Paste (Takes 2 min per talk)**

---

## 🚀 Quick Start Guide

### Step 1: Create manual_sources folder
```bash
mkdir -p manual_sources
```

### Step 2: For Each Tinto Talks URL:

1. **Open the URL in your browser**
   - Example: https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-5-march-27th-2024.1647775/

2. **Select All Text (Cmd+A / Ctrl+A)**

3. **Copy (Cmd+C / Ctrl+C)**

4. **Create a new file in `manual_sources/`**
   - Name it: `tinto_talks_5.txt` (or any descriptive name)

5. **Paste the content**

6. **Save the file**

### Step 3: Restart the App

```bash
# Delete the old brain to rebuild with new knowledge
rm -rf chroma_db

# Restart
python3 src/ui.py
```

The app will automatically:
- ✅ Detect new files in `manual_sources/`
- ✅ Add metadata headers
- ✅ Ingest into the RAG system
- ✅ Make the knowledge searchable

---

## 📋 Example File Format

Your pasted `.txt` file should look like:

```
Tinto Talks #5 - March 27th, 2024

[Developer Post]
Hello everyone! Today we're discussing...

[Community Question]
How does the economy work?

[Developer Response]
Great question! The economy in EU5...
```

**The app handles all formatting automatically!**

---

## ✅ Testing

### Test Wiki Scraping (Auto-Works):
```bash
python3 -c "
from src.ingestion import DataIngestor
ingestor = DataIngestor('data')
result = ingestor.scrape_url('https://eu5.paradoxwikis.com/Economy')
print('Wiki scraping:', 'SUCCESS' if result else 'FAILED')
"
```

### Test Manual Ingestion:
1. Add a test file to `manual_sources/test.txt`
2. Run app - check `data/manual_test.txt` was created

---

## 🎯 Pro Tips

- **File Naming**: Use descriptive names like `tinto_talks_economy.txt`
- **Batch Process**: Open all talks in browser tabs, copy-paste all at once
- **Update Knowledge**: When new Tinto Talks release, just add new files and restart

---

## 📊 Verification

Check ingestion worked:
```bash
ls data/manual_*.txt
```

You should see your Tinto Talks files prefixed with `manual_`.

The Oracle will give them recency priority in answers!
