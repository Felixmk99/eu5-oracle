import sys
import os
from pathlib import Path
from collections import defaultdict
import re

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ingestion import CORE_WIKI_URLS, TINTO_TALKS_URLS, DataIngestor

def get_file_report():
    root_dir = Path(__file__).parent.parent
    data_dir = root_dir / "data"
    manual_dir = root_dir / "manual_sources"
    ingestor = DataIngestor(str(data_dir))
    
    report = {
        "wiki": {"total": len(CORE_WIKI_URLS), "found": 0, "missing": []},
        "tinto": {"total": len(TINTO_TALKS_URLS), "found": 0, "missing": []},
        "manual": {"total": 0, "found": 0, "missing": []},
        "other": []
    }
    
    found_files = set()

    # Create a mapping of found URLs from content of files in data_dir
    url_to_file = {}
    for f in data_dir.glob("*.txt"):
        try:
            with open(f, "r", encoding="utf-8") as file:
                content = file.read(1000) # Read first 1000 chars
                match = re.search(r"Source URL: (https?://\S+)", content)
                if match:
                    url = match.group(1).strip()
                    url_to_file[url] = f.name
        except Exception:
            continue

    # 1. Wiki Check
    for url in CORE_WIKI_URLS:
        clean_url = url.strip()
        if clean_url in url_to_file:
            report["wiki"]["found"] += 1
            found_files.add(url_to_file[clean_url])
        else:
            report["wiki"]["missing"].append(url)

    # 2. Tinto Talks Check
    for url in TINTO_TALKS_URLS:
        clean_url = url.strip()
        # Check if URL directly found
        if clean_url in url_to_file:
            report["tinto"]["found"] += 1
            found_files.add(url_to_file[clean_url])
        else:
            # Fallback check for manual versions in data dir
            slug = clean_url.rstrip("/").split("/")[-1].split("?")[0]
            num_match = re.search(r'tinto-talks?-(\d+)', slug)
            
            manual_match = False
            if num_match:
                num = num_match.group(1)
                # Check for various manual filename patterns
                patterns = [f"manual_tinto_talks_{num}.txt", f"manual_tinto_talk_{num}.txt"]
                for p in patterns:
                    if (data_dir / p).exists():
                        report["tinto"]["found"] += 1
                        found_files.add(p)
                        manual_match = True
                        break
            
            if not manual_match:
                report["tinto"]["missing"].append(url)

    # 3. Manual Check (YouTube)
    # This checks that every file in manual_sources/ has a corresponding "manual_" file in data/
    manual_files = list(manual_dir.glob("*.txt"))
    # We exclude the tinto talks from the "Manual YouTube" count to avoid double counting
    youtube_manuals = [f for f in manual_files if "tinto_talks" not in f.name]
    report["manual"]["total"] = len(youtube_manuals)
    
    for f in youtube_manuals:
        clean_name = ingestor._sanitize_filename(f.stem) + ".txt"
        dest_filename = f"manual_{clean_name}"
        if (data_dir / dest_filename).exists():
            report["manual"]["found"] += 1
            found_files.add(dest_filename)
        else:
            report["manual"]["missing"].append(f.name)

    # 4. Other files
    all_files = [f.name for f in data_dir.glob("*.txt")]
    for f in all_files:
        if f not in found_files:
            # Check if it's one of the known Tinto manual fallbacks if they weren't matched
            if f in ["manual_tinto_talks_1.txt", "manual_tinto_talks_85.txt"]:
                continue
            report["other"].append(f)

    # Print Report
    print("="*40)
    print("🔍 EU5 ORACLE RAG SYSTEM REPORT")
    print("="*40)
    
    print(f"\n📚 WIKI KNOWLEDGE: {report['wiki']['found']}/{report['wiki']['total']}")
    if report["wiki"]["missing"]:
        print(f"   Missing: {len(report['wiki']['missing'])}")
        # Optional: print first 3 missing
        for m in report["wiki"]["missing"][:3]:
            print(f"     - {m}")

    print(f"\n✍️ TINTO TALKS (DEV DIARIES): {report['tinto']['found']}/{report['tinto']['total']}")
    if report["tinto"]["missing"]:
        print(f"   ⚠️ ACTION REQUIRED: {len(report['tinto']['missing'])} talks missing.")
        for m in report["tinto"]["missing"][:3]:
            print(f"     - {m}")

    print(f"\n📹 MANUAL SOURCES (YOUTUBE): {report['manual']['found']}/{report['manual']['total']}")
    if report["manual"]["missing"]:
        print(f"   ⚠️ Missing: {len(report['manual']['missing'])}")

    print(f"\n📂 UNRECOGNIZED/EXTRA FILES: {len(report['other'])}")
    if report["other"]:
        print("   Example:", report["other"][:3])

    print("\n" + "="*40)
    total_found = report['wiki']['found'] + report['tinto']['found'] + report['manual']['found']
    total_planned = report['wiki']['total'] + report['tinto']['total'] + report['manual']['total']
    print(f"OVERALL COVERAGE: {total_found}/{total_planned} ({ (total_found/max(1,total_planned))*100:.1f}%)")
    print("="*40)

if __name__ == "__main__":
    get_file_report()
