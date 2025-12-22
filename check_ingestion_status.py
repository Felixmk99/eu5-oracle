import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup

# --- Copied from ingestion.py ---
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

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_")

def check_status():
    data_dir = Path("data")
    if not data_dir.exists():
        print("Data directory not found!")
        return

    # Check YouTube
    yt_failed = []
    for url in CORE_YOUTUBE_URLS:
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        if match:
            video_id = match.group(1)
            filename = f"yt_{video_id}.txt"
            if not (data_dir / filename).exists():
                yt_failed.append(url)
    
    print(f"FAILED YouTube Videos: {len(yt_failed)}")
    for url in yt_failed:
        print(f" - {url}")

    # Check Wiki
    wiki_failed = []
    # We need to simulate the filename generation from ingestion.py
    # In ingestion.py: title = soup.title.string if soup.title else "scraped_content"
    # But since we don't want to scrape again to get the title, let's look at the filenames we HAVE
    # and try to match them, OR just list the URLs and see if any file *looks* like it.
    # Actually, ingestion.py code I wrote earlier uses:
    # title = soup.title.string ...
    # Wait, the latest edit I made to ingestion.py (Step 495) uses:
    # slug = url.split("/")[-1]
    # filename = self._sanitize_filename(slug) + ".txt"
    # So I can predict the filenames exactly!
    
    for url in CORE_WIKI_URLS:
        slug = url.split("/")[-1]
        expected_filename = sanitize_filename(slug) + ".txt"
        
        # Check if the expected filename exists
        # NOTE: If the previous run used soup.title, and the new code uses slug, 
        # we might have a mismatch if the file was created with the OLD method.
        # But I see files like 'Albania_-_Europa_Universalis_5_Wiki.txt' in the output of ls.
        # This matches `sanitize_filename(soup.title.string)`.
        # The URL '.../Albania' likely has title 'Albania - Europa Universalis 5 Wiki'.
        
        # Let's check if there is ANY file that seems to correspond.
        # Or I can just check the slug-based filename since that's what the CURRENT code expects to use for skipping.
        
        if not (data_dir / expected_filename).exists():
            # Fallback check: maybe it exists with the Title name?
            # We can't easily check that without scraping.
            # But wait, looking at my `ls` output: 'Albania_-_Europa_Universalis_5_Wiki.txt'
            # The slug is 'Albania'. Expected filename: 'Albania.txt'.
            # So the files ON DISK were created with the TITLE method (old code).
            # The NEW code in `ingestion.py` (Step 495) uses the SLUG method for checking existence:
            # filename = self._sanitize_filename(slug) + ".txt"
            # THIS IS A BUG. The ingestion check looks for 'Albania.txt', doesn't find it, and tries to scrape again.
            # And then `scrape_url` uses `soup.title` to save it as 'Albania_-_Europa_Universalis_5_Wiki.txt'.
            # So `ingest_core_knowledge` thinks it's missing, scrapes it, saves it (overwriting or creating duplicate), but checks for the WRONG filename next time?
            
            # Actually, `scrape_url` saves based on `soup.title`.
            # `ingest_core_knowledge` checks `self._sanitize_filename(slug) + ".txt"`.
            # These don't match. So it will ALWAYS re-scrape Wiki pages on startup.
            # That explains the slowness!
            
            wiki_failed.append(url)

    print(f"\nPotential 'Failed' or Re-Scraping Wiki Pages: {len(wiki_failed)}")
    # We will assume they are 'failed' in the sense of the check script, 
    # but likely they exist on disk with a different name.

if __name__ == "__main__":
    check_status()
