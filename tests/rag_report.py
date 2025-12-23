import sys
import os
from pathlib import Path
from collections import defaultdict

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

    # 1. Wiki Check
    for url in CORE_WIKI_URLS:
        slug = url.split("/")[-1].split("?")[0]
        if not slug or slug == "index.php": slug = "wiki_index"
        filename = ingestor._sanitize_filename(slug) + ".txt"
        if (data_dir / filename).exists():
            report["wiki"]["found"] += 1
            found_files.add(filename)
        else:
            report["wiki"]["missing"].append(url)

    # 2. Tinto Talks Check
    for url in TINTO_TALKS_URLS:
        slug = url.split("/")[-1].split("?")[0]
        if not slug: slug = "tinto_talk"
        filename = "tinto_" + ingestor._sanitize_filename(slug) + ".txt"
        if (data_dir / filename).exists():
            report["tinto"]["found"] += 1
            found_files.add(filename)
        else:
            report["tinto"]["missing"].append(url)

    # 3. Manual Check
    manual_files = list(manual_dir.glob("*.txt"))
    report["manual"]["total"] = len(manual_files)
    for f in manual_files:
        dest_filename = f"manual_{f.name}"
        if (data_dir / dest_filename).exists():
            report["manual"]["found"] += 1
            found_files.add(dest_filename)
        else:
            report["manual"]["missing"].append(f.name)

    # 4. Other files
    all_files = [f.name for f in data_dir.glob("*.txt")]
    for f in all_files:
        if f not in found_files:
            report["other"].append(f)

    # Print Report
    print("="*40)
    print("🔍 EU5 ORACLE RAG SYSTEM REPORT")
    print("="*40)
    
    print(f"\n📚 WIKI KNOWLEDGE: {report['wiki']['found']}/{report['wiki']['total']}")
    if report["wiki"]["missing"]:
        print(f"   Missing: {len(report['wiki']['missing'])} (Mostly Categories/Protected pages)")

    print(f"\n✍️ TINTO TALKS (DEV DIARIES): {report['tinto']['found']}/{report['tinto']['total']}")
    if report["tinto"]["missing"]:
        print(f"   ⚠️ ACTION REQUIRED: {len(report['tinto']['missing'])} talks failed to automate.")
        print("     Reason: Paradox Forum Cloudflare protection.")

    print(f"\n📹 MANUAL SOURCES (YOUTUBE): {report['manual']['found']}/{report['manual']['total']}")
    if report["manual"]["missing"]:
        print(f"   ⚠️ Missing: {len(report['manual']['missing'])}")

    print(f"\n📂 UNRECOGNIZED FILES: {len(report['other'])}")
    if report["other"]:
        print("   Example:", report["other"][:3])

    print("\n" + "="*40)
    total_found = report['wiki']['found'] + report['tinto']['found'] + report['manual']['found']
    total_planned = report['wiki']['total'] + report['tinto']['total'] + report['manual']['total']
    print(f"OVERALL COVERAGE: {total_found}/{total_planned} ({ (total_found/max(1,total_planned))*100:.1f}%)")
    print("="*40)

if __name__ == "__main__":
    get_file_report()
