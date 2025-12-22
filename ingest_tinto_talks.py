"""
SIMPLIFIED Tinto Talks Ingestion
=================================
Paradox forums use heavy JavaScript, so direct scraping doesn't work well.

EASY SOLUTION:
1. Manually copy-paste the Tinto Talks content from your browser
2. Save as .txt files in the manual_sources/ folder
3. App will auto-ingest them on next startup

OR use this script to try RSS feed extraction (works for some threads)
"""

import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

# ========================================  
# 📋 PASTE YOUR TINTO TALKS URLs HERE
# ========================================
TINTO_TALKS_URLS = [
    # Paste your forum URLs here
    # Example: "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-5-march-27th-2024.1647775/",
    
]

def scrape_forum_rss(url):
    """Try to scrape Paradox forum thread via RSS feed"""
    try:
        # Extract thread slug from URL
        # URL: .../developer-diary/tinto-talks-5-march-27th-2024.1647775/
        # RSS: https://forum.paradoxplaza.com/forum/threads/tinto-talks-5-march-27th-2024.1647775/index.rss
        
        path_parts = url.rstrip('/').split('/')
        thread_slug_id = path_parts[-1]
        
        rss_url = f"https://forum.paradoxplaza.com/forum/threads/{thread_slug_id}/index.rss"
        
        print(f"  📡 Trying RSS: {rss_url}")
        response = requests.get(rss_url, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        if not items:
            return None, "No posts found in RSS feed"
        
        posts = []
        for i, item in enumerate(items, 1):
            description = item.find('description')
            if description:
                desc_soup = BeautifulSoup(description.text, 'html.parser')
                post_text = desc_soup.get_text(separator='\n', strip=True)
                posts.append(f"=== Post {i} ===\n{post_text}")
        
        content = '\n\n---\n\n'.join(posts)
        return content, None
    
    except Exception as e:
        return None, str(e)


if __name__ == "__main__":
    print("🌍 EU5 Oracle - Tinto Talks Ingestion")
    print("=" * 60)
    
    if not TINTO_TALKS_URLS:
        print("\n❌ No URLs provided!")
        print("\nPLEASE DO ONE OF THE FOLLOWING:\n")
        print("Option 1 (RECOMMENDED - Most Reliable):")
        print("  1. Open the Tinto Talks thread in your browser")
        print("  2. Copy-paste all the text")
        print("  3. Save as .txt file in manual_sources/ folder")
        print("  4. Restart the app - it will auto-ingest!")
        print("\nOption 2 (Try RSS Auto-Scraping):")
        print("  1. Paste URLs in TINTO_TALKS_URLS list above")
        print("  2. Run this script again")
        print("  (May not work for all forum threads)")
        exit(1)
    
    print(f"📥 Found {len(TINTO_TALKS_URLS)} URLs to process\n")
    
    manual_dir = Path("manual_sources")
    manual_dir.mkdir(exist_ok=True)
    
    success = 0
    failed = 0
    
    for i, url in enumerate(TINTO_TALKS_URLS, 1):
        print(f"[{i}/{len(TINTO_TALKS_URLS)}] {url}")
        
        content, error = scrape_forum_rss(url)
        
        if content:
            # Save to manual_sources
            filename = f"tinto_talk_{i}.txt"
            filepath = manual_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Source: Tinto Talks (Paradox Forum)\n")
                f.write(f"URL: {url}\n\n")
                f.write(content)
           
            print(f"  ✅ Saved to manual_sources/{filename}")
            success += 1
        else:
            print(f"  ❌ Failed: {error}")
            print(f"  💡 Manual copy-paste recommended")
            failed += 1
        
        time.sleep(1)  # Be polite to server
    
    print(f"\n{'=' * 60}")
    print(f"📊 Summary: ✅ {success} success, ❌ {failed} failed")
    print(f"\n🔄 Next: Delete chroma_db/ and restart app to rebuild index!")
