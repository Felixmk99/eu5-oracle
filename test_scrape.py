import pathlib
from src.ingestion import scrape_url_to_file

def test_single_scrape():
    data_dir = pathlib.Path("./data_test")
    data_dir.mkdir(exist_ok=True)
    
    # Tinto Talk #1
    tinto_url = "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-1-february-28th-2024.1625360/"
    tinto_path = data_dir / "test_tinto.txt"
    
    print(f"Testing Tinto Talk scrape: {tinto_url}")
    success = scrape_url_to_file(tinto_url, tinto_path, selector=".message-main .bbWrapper")
    
    if success:
        with open(tinto_path, 'r') as f:
            content = f.read()
            print(f"Successfully scraped Tinto Talk. Length: {len(content)} chars.")
            print(f"Preview: {content[:100]}...")
    else:
        print("Scrape failed.")

    # Wiki
    wiki_url = "https://eu5.paradoxwikis.com/Project_Caesar"
    wiki_path = data_dir / "test_wiki.txt"
    
    print(f"\nTesting Wiki scrape: {wiki_url}")
    success = scrape_url_to_file(wiki_url, wiki_path, selector=".mw-parser-output")
    
    if success:
        with open(wiki_path, 'r') as f:
            content = f.read()
            print(f"Successfully scraped Wiki. Length: {len(content)} chars.")
            print(f"Preview: {content[:100]}...")
    else:
        print("Scrape failed.")

if __name__ == "__main__":
    test_single_scrape()
