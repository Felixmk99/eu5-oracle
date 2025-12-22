import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from pathlib import Path
from typing import List, Optional
import logging
import re
from datetime import datetime

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Core Knowledge Sources ---
# Add your hardcoded YouTube URLs here
CORE_YOUTUBE_URLS = [
    "https://youtu.be/gJjNtlK2XJM?si=0ltK_KTXp5El-tAS",
    "https://youtu.be/iA0cMW6QjDY?si=y6riu4f6T7_ZGcDr",
    "https://youtu.be/CcQaUI9n9FE?si=nAW9y5I92NoywNz2",
    "https://youtu.be/f5eh3yCicto?si=iV62uEChJCQGBgiF",
    "https://youtu.be/UiFufnxIugU?si=BxX6ykm3YsdHE3un",
    "https://youtu.be/U4J-oYJbADU?si=BT1u4DnxeHvQDW3b",
    "https://youtu.be/sFvDcUiukZ8?si=8VsyNNiP0qbnUFVl",
    "https://youtu.be/Yv9enZYQV_Y?si=mlUKQH4mgdZS7PoP",
    "https://youtu.be/X9Qqxi50UFA?si=8sk6p2NmQLICHA5T",
    "https://youtu.be/qP0a4iAm5nU?si=LqthlZ1PVaYkUnfQ",
    "https://youtu.be/K9kXW-Cdjl8?si=42wlpf3Hk5X9GFdu"
]

CORE_WIKI_URLS = [
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki",
    "https://eu5.paradoxwikis.com/Europa_Universalis_V",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:Work_needed",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:Style_guidelines",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:About",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:Privacy_policy",
    "https://eu5.paradoxwikis.com/Europa_Universalis_5_Wiki:General_disclaimer",
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
    "https://eu5.paradoxwikis.com/Settings",
    "https://eu5.paradoxwikis.com/Easter_eggs",
    "https://eu5.paradoxwikis.com/Soundtrack",
    "https://eu5.paradoxwikis.com/List_of_regiments",
    "https://eu5.paradoxwikis.com/List_of_ships",
    "https://eu5.paradoxwikis.com/List_of_casus_belli_and_wargoals",
    "https://eu5.paradoxwikis.com/Levy_types",
    "https://eu5.paradoxwikis.com/Hints",
    "https://eu5.paradoxwikis.com/Works_of_art",
    "https://eu5.paradoxwikis.com/Religious_actions",
    "https://eu5.paradoxwikis.com/Succession_laws",
    "https://eu5.paradoxwikis.com/Diplomatic_actions",
    "https://eu5.paradoxwikis.com/Historical_earthquakes",
    "https://eu5.paradoxwikis.com/Subject_types",
    "https://eu5.paradoxwikis.com/Cabinet_actions",
    "https://eu5.paradoxwikis.com/Religious_aspects",
    "https://eu5.paradoxwikis.com/Religious_schools",
    "https://eu5.paradoxwikis.com/Treaties",
    "https://eu5.paradoxwikis.com/Parliament_agendas",
    "https://eu5.paradoxwikis.com/Holy_sites",
    "https://eu5.paradoxwikis.com/Starting_countries",
    "https://eu5.paradoxwikis.com/Traits",
    "https://eu5.paradoxwikis.com/Religious_laws",
    "https://eu5.paradoxwikis.com/Military_laws",
    "https://eu5.paradoxwikis.com/Administrative_laws",
    "https://eu5.paradoxwikis.com/Socioeconomic_laws",
    "https://eu5.paradoxwikis.com/Estate_laws",
    "https://eu5.paradoxwikis.com/International_organization_laws",
    "https://eu5.paradoxwikis.com/Parliament_issues",
    "https://eu5.paradoxwikis.com/Age_of_Traditions_advances",
    "https://eu5.paradoxwikis.com/Age_of_Renaissance_advances",
    "https://eu5.paradoxwikis.com/Age_of_Discovery_advances",
    "https://eu5.paradoxwikis.com/Age_of_Reformation_advances",
    "https://eu5.paradoxwikis.com/Age_of_Absolutism_advances",
    "https://eu5.paradoxwikis.com/Age_of_Revolutions_advances",
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

    def scrape_url(self, url: str) -> bool:
        """
        Scrapes a static webpage and saves content to a .txt file.

        Args:
            url (str): The URL to scrape.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Get Publication Date
            pub_date = self._extract_publish_date(response.text, url)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 2. Extract content based on site type
            if "paradoxwikis.com" in url:
                # Target the main content area of MediaWiki
                content_div = soup.find(id="mw-content-text")
                if content_div:
                    # Remove elements that introduce noise
                    for noise in content_div.find_all(['table', 'div'], class_=['infobox', 'navbox', 'toc', 'mw-editsection']):
                        noise.decompose()
                    text = content_div.get_text(separator='\n')
                else:
                    text = soup.get_text(separator='\n')
            else:
                # Fallback for other sites: Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text(separator='\n')
            
            # Basic cleaning: break into lines and remove leading/trailing whitespace
            lines = (line.strip() for line in text.splitlines())
            # drop blank lines
            clean_text = '\n'.join(line for line in lines if line)

            # Use URL slug for consistent filename matching (Predictable Naming)
            slug = url.split("/")[-1].split("?")[0] # Remove query params if any
            if not slug or slug == "index.php": 
                # Fallback for root or weird URLs
                slug = soup.title.string if soup.title else "scraped_content"
            
            filename = self._sanitize_filename(slug) + ".txt"
            
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

    def get_youtube_transcript(self, video_url: str) -> bool:
        """
        Fetches transcript from a YouTube video and saves to a .txt file.

        Args:
            video_url (str): The full URL of the YouTube video.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # 1. Get Publication Date from the watch page
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            page_response = requests.get(video_url, headers=headers, timeout=10)
            pub_date = self._extract_publish_date(page_response.text, video_url)

            # 2. Extract video ID and transcript
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
            if not video_id_match:
                raise ValueError("Could not extract Video ID from URL.")
            
            video_id = video_id_match.group(1)
            
            # Using the instance-based API as per version 1.2.3
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            
            # Try to find English, then any available
            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                # Fallback to the first available transcript
                transcript = next(iter(transcript_list))
            
            transcript_data = transcript.fetch()
            transcript_text = "\n".join([item.text for item in transcript_data])
            
            filename = f"yt_{video_id}.txt"
            file_path = self.data_dir / filename
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"Source YouTube: {video_url}\n")
                f.write(f"Source Date: {pub_date}\n\n")
                f.write(transcript_text)
                
            logger.info(f"Successfully saved transcript for video {video_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to get YouTube transcript for {video_url}: {e}")
            return False
    def ingest_core_knowledge(self) -> None:
        """
        Ingests the hardcoded core YouTube transcripts and Wiki pages if they don't exist yet.
        """
        # 1. Ingest YouTube
        for url in CORE_YOUTUBE_URLS:
            video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
            if video_id_match:
                video_id = video_id_match.group(1)
                filename = f"yt_{video_id}.txt"
                if not (self.data_dir / filename).exists():
                    logger.info(f"Ingesting core video: {url}")
                    self.get_youtube_transcript(url)
                else:
                    logger.debug(f"Core video {video_id} already exists, skipping.")

        # 2. Ingest Wiki
        for url in CORE_WIKI_URLS:
            # Create a filename from the URL slug
            slug = url.split("/")[-1]
            filename = self._sanitize_filename(slug) + ".txt"
            if not (self.data_dir / filename).exists():
                logger.info(f"Ingesting core wiki page: {url}")
                self.scrape_url(url)
            else:
                logger.debug(f"Core wiki page {slug} already exists, skipping.")
