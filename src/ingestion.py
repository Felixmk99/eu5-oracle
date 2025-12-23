import requests
from bs4 import BeautifulSoup
from pathlib import Path
import logging
import re
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

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
# PASTE YOUR TINTO TALKS URLs HERE (Paradox Forum threads, YouTube videos, etc.)
# These are the developer's own explanations and are extremely valuable!
TINTO_TALKS_URLS = [
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-1-february-28th-2024.1625360/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-2-march-6th-2024.1626415/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-3-march-13th-2024.1630154/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-4-march-20th-2024.1636860/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-5-march-27th-2024.1647775/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-6-april-3rd-2024.1657435/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-7-10th-of-april.1662356/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tinto-talks-8-17th-of-april-2024.1666167/",
    "https://forum.paradoxplaza.com/forum/developer-diary/tintoThe two lists that we have-talks-9-24th-of-april-2024.1670510/",
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
    Handles data collection from web pages and YouTube videos.
    Saves raw text to the data/ directory for RAG processing.
    """

    def __init__(self, data_dir: str):
        """
        Args:
            data_dir (str): Path to save raw text files.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, name: str) -> str:
        """Removes illegal characters from filenames."""
        return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

    def _extract_publish_date(self, html_content: str, url: str) -> str:
        """
        Attempts to extract a publication date from HTML metadata.
        Targeting YouTube JSON-LD and common web meta tags.
        """
        # 1. Check for YouTube uploadDate in JSON-LD
        if "youtube.com" in url or "youtu.be" in url:
            match = re.search(r'"uploadDate":"(\d{4}-\d{2}-\d{2})', html_content)
            if match:
                return match.group(1)

        # 2. Check for common meta tags (Wikitext / Forums)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Meta property (OG)
        meta_date = soup.find("meta", property="article:published_time") or \
                    soup.find("meta", {"name": "dcterms.created"}) or \
                    soup.find("meta", property="og:updated_time")
        
        if meta_date and meta_date.get("content"):
            # Extract just the YYYY-MM-DD part
            return meta_date["content"][:10]

        # 3. Fallback: If it's a Paradox Wiki, look for "last modified" text
        footer = soup.find(id="footer-info-lastmod")
        if footer:
            match = re.search(r'(\d{1,2} \w+ \d{4})', footer.text)
            if match:
                try:
                    return datetime.strptime(match.group(1), "%d %B %Y").strftime("%Y-%m-%d")
                except:
                    pass

        # Global Fallback
        return datetime.now().strftime('%Y-%m-%d')

    def scrape_youtube(self, url: str) -> bool:
        """Extracts transcript from a YouTube video."""
        try:
            video_id = None
            if "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            
            if not video_id:
                return False
                
            # Using the module-level API directly for better compatibility
            import youtube_transcript_api
            try:
                # Try standard get_transcript first
                transcript_data = youtube_transcript_api.YouTubeTranscriptApi.get_transcript(video_id)
            except AttributeError:
                # Fallback to list/fetch if get_transcript is missing in this version
                ts_list = youtube_transcript_api.YouTubeTranscriptApi.list(video_id)
                transcript_data = ts_list.find_transcript(['en']).fetch()

            text = " ".join([t['text'] for t in transcript_data])
            
            filename = f"youtube_{video_id}.txt"
            file_path = self.data_dir / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {url}\n")
                f.write(f"Source Date: {datetime.now().strftime('%Y-%m-%d')}\n\n")
                f.write(text)
                
            logger.info(f"Successfully ingested YouTube transcript: {url}")
            return True
        except Exception as e:
            logger.error(f"Failed to ingest YouTube transcript {url}: {e}")
            return False

    def scrape_url(self, url: str, prefix: str = "") -> bool:
        """
        Scrapes a static webpage or YouTube video and saves content to a .txt file.
        """
        if "youtube.com" in url or "youtu.be" in url:
            return self.scrape_youtube(url)
            
        try:
            # Use a slightly more realistic User-Agent to reduce Cloudflare triggers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            if "Just a moment..." in response.text or "Client Challenge" in response.text:
                logger.warning(f"Cloudflare block detected for {url}. Skipping.")
                return False
                
            # Get Publication Date
            pub_date = self._extract_publish_date(response.text, url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract content based on site type
            if "paradoxwikis.com" in url:
                content_div = soup.find(id="mw-content-text")
                if content_div:
                    for noise in content_div.find_all(['table', 'div'], class_=['infobox', 'navbox', 'toc', 'mw-editsection']):
                        noise.decompose()
                    text = content_div.get_text(separator='\n')
                else:
                    text = soup.get_text(separator='\n')
            
            elif "forum.paradoxplaza.com" in url:
                # Forum thread logic
                content_div = soup.find('div', class_='p-body-content')
                if not content_div:
                    content_div = soup.find('article', class_='message-body')
                
                if content_div:
                    text = content_div.get_text(separator='\n')
                else:
                    text = soup.get_text(separator='\n')
            
            else:
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator='\n')
            
            lines = (line.strip() for line in text.splitlines())
            clean_text = '\n'.join(line for line in lines if line)

            # Prevent saving empty or challenge pages
            if len(clean_text) < 200:
                logger.warning(f"Extracted content too short for {url}. Might be a block page.")
                return False

            slug = url.split("/")[-1].split("?")[0]
            if not slug or slug == "index.php": 
                slug = soup.title.string if soup.title else "scraped_content"
            
            filename = prefix + self._sanitize_filename(slug) + ".txt"
            
            file_path = self.data_dir / filename
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Source URL: {url}\n")
                f.write(f"Source Date: {pub_date}\n\n")
                f.write(clean_text)
            
            logger.info(f"Successfully scraped {url} to {filename}")
            return True

        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return False

    def ingest_core_knowledge(self) -> None:
        """
        Ingests the hardcoded Wiki pages and any manually uploaded transcripts.
        """
        # 1. Ingest Manual Sources (e.g., YouTube Transcripts)
        # We look for a folder at the project root level
        root_dir = self.data_dir.parent
        manual_dir = root_dir / "manual_sources"
        
        if manual_dir.exists():
            for txt_file in manual_dir.glob("*.txt"):
                # Avoid re-processing if the output file already exists
                # We prefix with 'manual_' to keep them organized
                dest_filename = f"manual_{txt_file.name}"
                dest_path = self.data_dir / dest_filename
                
                if not dest_path.exists():
                    logger.info(f"Processing manual source: {txt_file.name}")
                    try:
                        content = txt_file.read_text(encoding='utf-8')
                        
                        # Add Metadata Header for RAG consistency
                        # We use the current date so the RAG engine knows when we learned this
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        final_content = (
                            f"Source: Manual Upload ({txt_file.name})\n"
                            f"Source Date: {current_date}\n"
                            f"URL: local_file\n\n"
                            f"{content}"
                        )
                        
                        with open(dest_path, 'w', encoding='utf-8') as f:
                            f.write(final_content)
                    except Exception as e:
                        logger.error(f"Failed to process {txt_file.name}: {e}")
                else:
                    logger.debug(f"Manual source {txt_file.name} already processed.")

        # 2. Ingest Wiki
        for url in CORE_WIKI_URLS:
            # Use URL slug for consistent filename matching (Predictable Naming)
            slug = url.split("/")[-1].split("?")[0] # Remove query params if any
            if not slug or slug == "index.php": 
                # Fallback for root or weird URLs
                # We can't know the title without scraping, but for the check we need a slug.
                # If we really can't guess, we might skip or force scrape.
                # For the core list, they are all reliable slugs.
                slug = "wiki_index"
            
            filename = self._sanitize_filename(slug) + ".txt"
            if not (self.data_dir / filename).exists():
                logger.info(f"Ingesting core wiki page: {url}")
                self.scrape_url(url)
            else:
                logger.debug(f"Core wiki page {slug} already exists, skipping.")

        # 3. Ingest Tinto Talks (Developer Explanations)
        for url in TINTO_TALKS_URLS:
            # Prefix with "tinto_" to identify these as high-priority developer sources
            slug = url.split("/")[-1].split("?")[0]
            if not slug:
                slug = "tinto_talk"
            
            filename = "tinto_" + self._sanitize_filename(slug) + ".txt"
            if not (self.data_dir / filename).exists():
                logger.info(f"Ingesting Tinto Talk: {url}")
                self.scrape_url(url, prefix="tinto_")
            else:
                logger.debug(f"Tinto Talk {slug} already exists, skipping.")
