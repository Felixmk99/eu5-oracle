import requests
from src.ingestion import CORE_WIKI_URLS
import time

def check_url(url):
    """Check if a URL returns a valid response."""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, response.status_code
        else:
            # Try GET as some servers don't support HEAD
            response = requests.get(url, timeout=10)
            return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

print(f"Checking {len(CORE_WIKI_URLS)} URLs...\n")

broken_urls = []
working_urls = []

for i, url in enumerate(CORE_WIKI_URLS, 1):
    is_valid, status = check_url(url)
    
    if is_valid:
        working_urls.append(url)
        print(f"✅ [{i}/{len(CORE_WIKI_URLS)}] {url}")
    else:
        broken_urls.append((url, status))
        print(f"❌ [{i}/{len(CORE_WIKI_URLS)}] {url} - Status: {status}")
    
    # Be polite to the server
    time.sleep(0.5)

print(f"\n{'='*80}")
print(f"Summary:")
print(f"Working URLs: {len(working_urls)}")
print(f"Broken URLs: {len(broken_urls)}")

if broken_urls:
    print(f"\n{'='*80}")
    print("Broken URLs to remove:")
    for url, status in broken_urls:
        print(f"  - {url} (Status: {status})")
