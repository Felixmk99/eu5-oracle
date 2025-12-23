import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ingestion import CORE_WIKI_URLS, TINTO_TALKS_URLS, DataIngestor

def verify_ingestion():
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    manual_dir = root_dir / "manual_sources"
    
    ingestor = DataIngestor(str(data_dir))
    
    print("--- RAG Ingestion Verification ---")
    
    # 1. Check Wiki URLs
    missing_wiki = []
    for url in CORE_WIKI_URLS:
        slug = url.split("/")[-1].split("?")[0]
        if not slug or slug == "index.php":
            slug = "wiki_index"
        filename = ingestor._sanitize_filename(slug) + ".txt"
        if not (data_dir / filename).exists():
            missing_wiki.append(url)
    
    print(f"Wiki Pages: {len(CORE_WIKI_URLS) - len(missing_wiki)}/{len(CORE_WIKI_URLS)} ingested.")
    if missing_wiki:
        print(f"⚠️ Missing Wiki URLs: {len(missing_wiki)}")
        for url in missing_wiki[:5]:
            print(f"  - {url}")
        if len(missing_wiki) > 5:
            print("  - ...")

    # 2. Check Tinto Talks
    missing_tinto = []
    for url in TINTO_TALKS_URLS:
        slug = url.split("/")[-1].split("?")[0]
        if not slug:
            slug = "tinto_talk"
        filename = "tinto_" + ingestor._sanitize_filename(slug) + ".txt"
        if not (data_dir / filename).exists():
            missing_tinto.append(url)
            
    print(f"Tinto Talks: {len(TINTO_TALKS_URLS) - len(missing_tinto)}/{len(TINTO_TALKS_URLS)} ingested.")
    if missing_tinto:
        print(f"⚠️ Missing Tinto Talks: {len(missing_tinto)}")
        for url in missing_tinto[:5]:
            print(f"  - {url}")
        if len(missing_tinto) > 5:
            print("  - ...")

    # 3. Check Manual Sources (YouTube transcripts, etc.)
    manual_files = list(manual_dir.glob("*.txt"))
    missing_manual = []
    for f in manual_files:
        dest_filename = f"manual_{f.name}"
        if not (data_dir / dest_filename).exists():
            missing_manual.append(f.name)
            
    print(f"Manual Sources: {len(manual_files) - len(missing_manual)}/{len(manual_files)} ingested.")
    if missing_manual:
        print(f"⚠️ Missing Manual Files: {len(missing_manual)}")
        for f in missing_manual[:5]:
            print(f"  - {f}")

    print("\nTotal Files in data/ directory:", len(list(data_dir.glob("*.txt"))))

if __name__ == "__main__":
    verify_ingestion()
