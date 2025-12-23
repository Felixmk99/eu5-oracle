import requests
from bs4 import BeautifulSoup
from pathlib import Path
import logging
import re
from datetime import datetime
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Core Knowledge Sources ---
# Hardcoded Wiki Sources

CORE_WIKI_URLS = [
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki",
    "https://eu5.paradoxwikis.com/Europa_Universalis_V",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:Work_needed",
    "https://eu5.paradoxwikis.com/Beginner%27s_guide",
    "https://eu5.paradoxwikis.com/Game_rules",
    "https://eu5.paradoxwikis.com/Console_commands",
    "https://eu5.paradoxwikis.com/User_interface",
    "https://eu5.paradoxwikis.com/Map_modes",
    "https://eu5.paradoxwikis.com/Country",
    "https://eu5.paradoxwikis.com/Government",
    "https://eu5.paradoxwikis.com/Parliament",
    "https://eu5.paradoxwikis.com/Estate",
    "https://eu5.paradoxwikis.com/Reforms",
    "https://eu5.paradoxwikis.com/Laws",
    "https://eu5.paradoxwikis.com/Characters",
    "https://eu5.paradoxwikis.com/Missions",
    "https://eu5.paradoxwikis.com/Economy",
    "https://eu5.paradoxwikis.com/Goods",
    "https://eu5.paradoxwikis.com/R.G.O.",
    "https://eu5.paradoxwikis.com/Market",
    "https://eu5.paradoxwikis.com/Buildings",
    "https://eu5.paradoxwikis.com/Population",
    "https://eu5.paradoxwikis.com/Advances",
    "https://eu5.paradoxwikis.com/Diplomacy",
    "https://eu5.paradoxwikis.com/Subjects",
    "https://eu5.paradoxwikis.com/International_organization",
    "https://eu5.paradoxwikis.com/Warfare",
    "https://eu5.paradoxwikis.com/Combat",
    "https://eu5.paradoxwikis.com/Military",
    "https://eu5.paradoxwikis.com/Location",
    "https://eu5.paradoxwikis.com/Culture",
    "https://eu5.paradoxwikis.com/Religion",
    "https://eu5.paradoxwikis.com/Language",
    "https://eu5.paradoxwikis.com/Exploration",
    "https://eu5.paradoxwikis.com/Situations",
    "https://eu5.paradoxwikis.com/Disasters",
    "https://eu5.paradoxwikis.com/Diseases",
    "https://eu5.paradoxwikis.com/Modding",
    "https://eu5.paradoxwikis.com/Mods",
    "https://eu5.paradoxwikis.com/Communities",
    "https://eu5.paradoxwikis.com/Jargon",
    "https://eu5.paradoxwikis.com/Developer_diaries",
    "https://eu5.paradoxwikis.com/Patches",
    "https://eu5.paradoxwikis.com/Downloadable_content",
    "https://eu5.paradoxwikis.com/Achievements",
    "https://eu5.paradoxwikis.com/Formable_countries",
    "https://eu5.paradoxwikis.com/Succession_laws",
    "https://eu5.paradoxwikis.com/Holy_sites",
    "https://eu5.paradoxwikis.com/Starting_countries",
    "https://eu5.paradoxwikis.com/Religious_laws",
    "https://eu5.paradoxwikis.com/Military_laws",
    "https://eu5.paradoxwikis.com/Administrative_laws",
    "https://eu5.paradoxwikis.com/Socioeconomic_laws",
    "https://eu5.paradoxwikis.com/Estate_laws",
    "https://eu5.paradoxwikis.com/International_organization_laws",
    "https://eu5.paradoxwikis.com/Albania",
    "https://eu5.paradoxwikis.com/Aquitaine",
    "https://eu5.paradoxwikis.com/Aragon",
    "https://eu5.paradoxwikis.com/Arianiti",
    "https://eu5.paradoxwikis.com/Austria",
    "https://eu5.paradoxwikis.com/Bohemia",
    "https://eu5.paradoxwikis.com/Byzantium",
    "https://eu5.paradoxwikis.com/Cahokia",
    "https://eu5.paradoxwikis.com/Castile",
    "https://eu5.paradoxwikis.com/Ch%C5%ABzan",
    "https://eu5.paradoxwikis.com/Croatia",
    "https://eu5.paradoxwikis.com/Delhi",
    "https://eu5.paradoxwikis.com/Denmark",
    "https://eu5.paradoxwikis.com/Dithmarschen",
    "https://eu5.paradoxwikis.com/England",
    "https://eu5.paradoxwikis.com/Epirus",
    "https://eu5.paradoxwikis.com/Ethiopia",
    "https://eu5.paradoxwikis.com/Florence",
    "https://eu5.paradoxwikis.com/France",
    "https://eu5.paradoxwikis.com/Georgia",
    "https://eu5.paradoxwikis.com/Granada",
    "https://eu5.paradoxwikis.com/Guelders",
    "https://eu5.paradoxwikis.com/Hokuzan",
    "https://eu5.paradoxwikis.com/Holland",
    "https://eu5.paradoxwikis.com/Hungary",
    "https://eu5.paradoxwikis.com/Iceland",
    "https://eu5.paradoxwikis.com/Japan",
    "https://eu5.paradoxwikis.com/Kyiv",
    "https://eu5.paradoxwikis.com/Lithuania",
    "https://eu5.paradoxwikis.com/Majapahit",
    "https://eu5.paradoxwikis.com/Mataranga",
    "https://eu5.paradoxwikis.com/Milan",
    "https://eu5.paradoxwikis.com/Moravia",
    "https://eu5.paradoxwikis.com/Morocco",
    "https://eu5.paradoxwikis.com/Mughal",
    "https://eu5.paradoxwikis.com/Muscovy",
    "https://eu5.paradoxwikis.com/Muzaka",
    "https://eu5.paradoxwikis.com/M%C3%ADng",
    "https://eu5.paradoxwikis.com/Nanzan",
    "https://eu5.paradoxwikis.com/Naples",
    "https://eu5.paradoxwikis.com/Navarre",
    "https://eu5.paradoxwikis.com/Norway",
    "https://eu5.paradoxwikis.com/Oman",
    "https://eu5.paradoxwikis.com/Ottomans",
    "https://eu5.paradoxwikis.com/Papal_States",
    "https://eu5.paradoxwikis.com/Poland",
    "https://eu5.paradoxwikis.com/Portugal",
    "https://eu5.paradoxwikis.com/Ry%C5%ABky%C5%AB",
    "https://eu5.paradoxwikis.com/Scotland",
    "https://eu5.paradoxwikis.com/Serbia",
    "https://eu5.paradoxwikis.com/Sicily",
    "https://eu5.paradoxwikis.com/Spain",
    "https://eu5.paradoxwikis.com/Sweden",
    "https://eu5.paradoxwikis.com/Thopia",
    "https://eu5.paradoxwikis.com/Timurid",
    "https://eu5.paradoxwikis.com/Valencia",
    "https://eu5.paradoxwikis.com/Venice",
    "https://eu5.paradoxwikis.com/Wales",
    "https://eu5.paradoxwikis.com/Yemen",
    "https://eu5.paradoxwikis.com/Yu%C3%A1n",
    "https://eu5.paradoxwikis.com/Category:Countries",
    "https://eu5.paradoxwikis.com/Category:Lists",
    "https://eu5.paradoxwikis.com/Template:Countries_navbox",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:Style/Country",
]

# --- Tinto Talks (Developer Explanations) ---
TINTO_TALKS_URLS = [
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-1-february-28th-2024.1625360/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-2-march-6th-2024.1626415/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-3-march-13th-2024.1630154/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-4-march-20th-2024.1636860/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-5-march-27th-2024.1647775/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-6-april-3rd-2024.1657435/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-7-10th-of-april.1662356/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-8-17th-of-april-2024.1666167/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-9-24th-of-april-2024.1670510/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-10-1st-of-may-2024.1673745/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-11-8th-of-may-2024.1675078/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-12-15th-of-may.1677441/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-13-22nd-of-may-2024.1680927/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-14-29th-of-may-2024.1682450/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-15-june-5th-2024.1685161/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-16-12th-of-june-2024.1687571/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-17-19th-of-june-2024.1689183/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-18-26th-of-june-2024.1689850/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-19-3rd-of-july-2024.1693447/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-20-10th-of-july-2024.1694744/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-21-17th-of-july-2024.1695632/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-22-24th-of-july.1696537/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-23-31st-of-july.1697510/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-24-7th-of-august-2024.1698427/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-25-14th-of-august-2024.1699250/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-26-21st-of-august-2024.1700025/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-28-28th-of-august-2024.1701189/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-28-4th-of-september-2024.1702099/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-29-18th-of-september-2024.1704098/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-30-25th-september-2024.1705317/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-31-2nd-of-october-2024.1706918/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-32-9th-of-october-2024.1708363/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-33-16th-of-october-2024.1709991/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-34-23rd-of-october-2024.1711421/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-35-30th-of-october.1712624/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-36-6th-of-november.1713610/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-37-13th-of-november-2024.1714711/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-38-20th-of-november-2024.1716232/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-39-27th-of-november-2024.1717971/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-40-4th-of-december-2024.1719416/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-41-11th-of-december-2024.1720391/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-42-18th-of-december-2024.1721548/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-43-25th-of-december-2025.1723027/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-44-1st-of-january-2025.1724420/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-45-8th-of-january-2025.1725373/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-46-15th-of-january-2025.1726045/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-47-22nd-of-january-2025.1726704/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-48-29th-of-january-2025.1727342/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-49-5th-february-2025.1728019/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-50-12th-february-2025.1728609/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-51-19th-of-february-2025.1729243/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-52-26th-of-feburary-2025.1729927/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-53-5th-of-march-2025.1730443/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-54-12th-of-march-2025.1731164/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-55-19th-of-march-2025.1732147/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-56-26th-of-march-2025.1733172/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-57-2nd-of-april-2025.1734057/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-58-9th-of-april-2025.1734944/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-59-16th-of-april-2025.1735622/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-60-23rd-of-april-2025.1736924/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-61-30th-of-april-2025.1738380/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-62-7th-of-may-2025.1741825/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-63-14th-of-may-2025.1747262/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-64-21st-of-may-2025.1756210/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-65-28th-of-may-2025.1760717/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-66-4th-of-june-2025.1766139/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-67-11th-of-june-2025-shinto-and-shogunate.1771463/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-68-18th-of-june-2025.1788518/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-69-25th-of-june-2025.1806956/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-70-2nd-of-july-2025.1823383/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-71-9th-of-july-2025.1835118/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-72-16th-of-july-2025.1846292/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-73-23th-of-july-2025-middle-kingdom.1851155/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-74-30th-of-july-2025.1852937/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-75-6th-of-august-2025.1854212/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-75-13th-of-august-2025.1855048/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-77-20th-of-august-2025.1856053/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-78-27th-of-august-2025.1857065/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-79-3rd-of-september-2025.1857843/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-80-10th-of-september-2025.1858519/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-81-24th-of-september.1860037/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-82-1st-of-october-2025.1861246/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-83-8th-of-october-2025.1862270/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-84-15th-of-october-2025-onboarding-systems.1863138/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-85-22nd-of-october-modding.1864004/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-86-29nd-of-october-loading-screens-achievements.1865038/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-87-5th-of-november.1867301/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-88-12th-of-november-2025.1872401/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-89-19th-of-november-2025.1876786/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-90-3rd-of-december-2025.1884467/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-91-10th-of-december-2025.1887357/",
    "https://forum.paradoxplaza.com/forum/developer-diary/patch-1-0-10-is-live-now-tinto-talk-92.1889614/"
]

class DataIngestor:
    """
    Handles data collection from web pages and manual files.
    Saves raw text to the data/ directory for RAG processing.
    """

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Removes illegal characters and trailing spaces from filenames."""
        return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

    def _extract_publish_date(self, html_content: str, url: str) -> str:
        """Attempts to extract a publication date from HTML metadata."""
        soup = BeautifulSoup(html_content, 'html.parser')
        meta_date = soup.find("meta", property="article:published_time") or \
                    soup.find("meta", {"name": "dcterms.created"}) or \
                    soup.find("meta", property="og:updated_time")
        
        if meta_date and meta_date.get("content"):
            return meta_date["content"][:10]

        footer = soup.find(id="footer-info-lastmod")
        if footer:
            match = re.search(r'(\d{1,2} \w+ \d{4})', footer.text)
            if match:
                try:
                    return datetime.strptime(match.group(1), "%d %B %Y").strftime("%Y-%m-%d")
                except: pass
        return datetime.now().strftime('%Y-%m-%d')

    def _scrape_with_playwright(self, url: str) -> str:
        """Fallback scraper using Playwright to bypass Cloudflare."""
        try:
            with sync_playwright() as p:
                browser = p.firefox.launch(headless=True)
                # Create a context with a realistic user agent
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0'
                )
                page = context.new_page()
                # Stealth may be Chromium-specific in some versions, skipping for Firefox test
                
                logger.info(f"Attempting Playwright (Firefox) scrape for {url}")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Loop to wait for Cloudflare challenge to pass
                attempts = 0
                while attempts < 10:
                    title = page.title()
                    if "Client Challenge" not in title and "Just a moment..." not in title:
                        break
                    logger.info(f"Cloudflare challenge detected (Title: {title}). Waiting 5s... ({attempts+1}/10)")
                    time.sleep(5)
                    attempts += 1
                
                # Final check for content
                try:
                    page.wait_for_selector(".message-body, .p-body-content", timeout=10000)
                    logger.info(f"Content found after challenge. Title: {page.title()}")
                except:
                    logger.warning(f"Content selector not found. Current Title: {page.title()}")
                
                content = page.content()
                browser.close()
                return content
        except Exception as e:
            logger.error(f"Playwright scraping failed: {e}")
            return ""

    def scrape_url(self, url: str, prefix: str = "") -> bool:
        """Scrapes a static webpage and saves content to a .txt file."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.472.124 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            if "Just a moment..." in response.text or "Client Challenge" in response.text:
                logger.warning(f"Cloudflare block detected for {url}. Attempting Playwright fallback...")
                html_content = self._scrape_with_playwright(url)
                if not html_content or "Just a moment..." in html_content or "Client Challenge" in html_content:
                    logger.error(f"Playwright also failed to bypass Cloudflare for {url}")
                    return False
            else:
                html_content = response.text
                
            pub_date = self._extract_publish_date(html_content, url)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Stricter validation: title check
            if soup.title and ("Client Challenge" in soup.title.string or "Just a moment..." in soup.title.string):
                logger.error(f"Scraped content for {url} still identified as challenge page.")
                return False
            
            if "paradoxwikis.com" in url:
                content_div = soup.find(id="mw-content-text")
                if content_div:
                    for noise in content_div.find_all(['table', 'div'], class_=['infobox', 'navbox', 'toc', 'mw-editsection']):
                        noise.decompose()
                    text = content_div.get_text(separator='\n')
                else: text = soup.get_text(separator='\n')
            elif "forum.paradoxplaza.com" in url:
                content_div = soup.find('div', class_='p-body-content') or soup.find('article', class_='message-body')
                text = content_div.get_text(separator='\n') if content_div else soup.get_text(separator='\n')
            else:
                for script in soup(["script", "style"]): script.decompose()
                text = soup.get_text(separator='\n')
            
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(line for line in lines if line)

            if len(clean_text) < 300: return False

            slug = url.split("/")[-1].split("?")[0]
            if not slug or slug == "index.php": slug = soup.title.string if soup.title else "scraped_content"
            
            filename = prefix + self._sanitize_filename(slug) + ".txt"
            file_path = self.data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {url}\nSource Date: {pub_date}\n\n{clean_text}")
            
            logger.info(f"Successfully scraped {url} to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return False

    def ingest_core_knowledge(self) -> None:
        """Ingests Wiki pages, Tinto Talks, and manual sources."""
        # 1. Manual Sources (Trust these, no length check)
        manual_dir = self.data_dir.parent / "manual_sources"
        if manual_dir.exists():
            for txt_file in manual_dir.glob("*.txt"):
                # Clean filename for destination
                clean_name = self._sanitize_filename(txt_file.stem) + ".txt"
                dest_path = self.data_dir / f"manual_{clean_name}"
                
                if not dest_path.exists():
                    logger.info(f"Ingesting manual source: {txt_file.name}")
                    content = txt_file.read_text(encoding='utf-8')
                    header = f"Source: Manual ({txt_file.name})\nSource Date: {datetime.now().strftime('%Y-%m-%d')}\nURL: local_file\n\n"
                    dest_path.write_text(header + content, encoding='utf-8')

        # 2. Wiki
        for url in CORE_WIKI_URLS:
            slug = url.split("/")[-1].split("?")[0] or "wiki_index"
            filename = self._sanitize_filename(slug) + ".txt"
            if not (self.data_dir / filename).exists():
                self.scrape_url(url)

        # 3. Tinto Talks
        for url in TINTO_TALKS_URLS:
            slug = url.split("/")[-1].split("?")[0] or "tinto_talk"
            filename = "tinto_" + self._sanitize_filename(slug) + ".txt"
            if not (self.data_dir / filename).exists():
                self.scrape_url(url, prefix="tinto_")

if __name__ == "__main__":
    import os
    data_dir = os.path.join(os.getcwd(), "data")
    ingestor = DataIngestor(data_dir)
    print("🌍 Starting ingestion process...")
    ingestor.ingest_core_knowledge()
    print("✅ Ingestion process completed.")
