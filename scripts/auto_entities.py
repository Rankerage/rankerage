#!/usr/bin/env python3
"""
Rankerage Auto-Entity Script
Monitors hot news, extracts notable people, auto-registers them.
"""
import json
import re
import hashlib
import sys
from datetime import datetime
from pathlib import Path

try:
    import feedparser
except ImportError:
    print("Installing feedparser...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "feedparser", "-q"])
    import feedparser

import requests

# === CONFIG ===
DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
COUNTRIES_FILE = DATA_DIR / "countries.json"
MAX_NEW_PER_RUN = 5  # Don't add too many at once

# === NEWS SOURCES ===
RSS_FEEDS = [
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

# === ENTITY EXTRACTION ===
# Known name patterns (Mr./Dr./President etc followed by capitalized words)
NAME_PATTERNS = [
    re.compile(r'\b(?:President|Prime Minister|CEO|Chairman|Director|Founder|Senator|Governor|Mayor|Minister|Secretary|General|Admiral|King|Queen|Prince|Princess|Pope|Bishop|Cardinal|Archbishop)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'),
    re.compile(r'\b([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:said|announced|reported|confirmed|denied|released|launched|resigned|appointed|elected|won|signed)\b'),
    re.compile(r'\b(?:billionaire|investor|philanthropist|activist|scientist|researcher|professor|doctor|artist|singer|actor|director|author|athlete|player|coach)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b'),
]

# Blacklist: common non-person capitalized phrases
BLACKLIST = {
    "United States", "South Korea", "North Korea", "New York", "Los Angeles",
    "San Francisco", "Hong Kong", "Saudi Arabia", "European Union", "United Nations",
    "White House", "Wall Street", "Silicon Valley", "World Bank", "Red Cross",
    "Human Rights", "Climate Change", "Artificial Intelligence", "Social Media",
    "Supreme Court", "Federal Reserve", "Security Council", "State Department",
    "Health Organization", "Olympic Games", "World Cup", "Premier League",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
}

def extract_people(text):
    """Extract potential person names from text."""
    people = set()
    # Titles to strip
    title_prefixes = ['President ', 'Prime Minister ', 'CEO ', 'Chairman ', 'Director ',
                      'Founder ', 'Senator ', 'Governor ', 'Mayor ', 'Minister ', 'Secretary ',
                      'General ', 'Admiral ', 'King ', 'Queen ', 'Prince ', 'Princess ',
                      'Pope ', 'Bishop ', 'Cardinal ', 'Archbishop ', 'Dr. ', 'Mr. ', 'Mrs. ', 'Ms. ']
    
    for pattern in NAME_PATTERNS:
        for match in pattern.finditer(text):
            name = match.group(1) if match.lastindex else match.group(0)
            # Strip title prefixes
            for title in title_prefixes:
                if name.startswith(title):
                    name = name[len(title):]
                    break
            # Skip blacklisted phrases
            if name in BLACKLIST:
                continue
            # Must be 2-3 words, all starting with capital
            parts = name.split()
            if 2 <= len(parts) <= 3 and all(p[0].isupper() for p in parts):
                people.add(name)
    return people

def fetch_news():
    """Fetch trending news headlines."""
    headlines = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get('title', '')
                summary = entry.get('summary', '')
                text = f"{title}. {summary}"
                headlines.append(text)
        except Exception as e:
            print(f"  ⚠️ Failed to fetch {url[:50]}...: {e}")
    return headlines

def load_existing():
    """Load existing entity names."""
    with open(COUNTRIES_FILE) as f:
        data = json.load(f)
    entities = set()
    for d in data:
        name = d.get('country_name_en', '')
        if name.startswith('**'):
            entities.add(name[2:])  # Strip ** prefix
        elif name.startswith('***'):
            entities.add(name[3:])
        elif name.startswith('*'):
            entities.add(name[1:])
        else:
            entities.add(name)
    return data, entities

def gen_code(name):
    h = hashlib.md5(name.encode()).hexdigest()[:5].upper()
    return f"XX{h}"

def estimate_net_worth(name):
    """Try to estimate net worth (very rough)."""
    # Known billionaires (approximate 2024-2025 net worth in millions)
    known = {
        "Elon Musk": 420000, "Jeff Bezos": 230000, "Bernard Arnault": 235000,
        "Bill Gates": 145000, "Mark Zuckerberg": 200000, "Larry Page": 168000,
        "Sergey Brin": 162000, "Steve Ballmer": 155000, "Warren Buffett": 148000,
        "Michael Bloomberg": 110000, "Michael Dell": 105000, "Jensen Huang": 110000,
        "Larry Ellison": 190000, "Mukesh Ambani": 110000, "Gautam Adani": 85000,
        "Amancio Ortega": 100000, "Jim Walton": 95000, "Rob Walton": 93000,
        "Alice Walton": 90000, "David Thomson": 70000, "Francoise Bettencourt": 95000,
        "Carlos Slim": 90000, "MacKenzie Scott": 40000, "Julia Koch": 65000,
        "Changpeng Zhao": 35000, "Zhang Yiming": 45000, "Ma Huateng": 40000,
        "Jack Ma": 30000, "Colin Huang": 48000, "William Ding": 30000,
        "Donald Trump": 3500, "Joe Biden": 10, "Kamala Harris": 8,
        "Barack Obama": 70, "George Bush": 40, "Bill Clinton": 120,
        "Hillary Clinton": 120, "Nancy Pelosi": 200, "Mitch McConnell": 35,
        "Alexandria Ocasio-Cortez": 1, "Bernie Sanders": 3, "Elizabeth Warren": 12,
        "Emmanuel Macron": 1, "Justin Trudeau": 10, "Boris Johnson": 5,
        "Rishi Sunak": 800, "Keir Starmer": 2, "Olaf Scholz": 3,
        "Vladimir Putin": 200000, "Xi Jinping": 2, "Narendra Modi": 1,
        "Volodymyr Zelensky": 20, "Benjamin Netanyahu": 80, "Recep Erdogan": 5,
        "Mohammed bin Salman": 1800, "Mohammed bin Zayed": 15000,
        "Kim Jong Un": 5000, "Yoon Suk Yeol": 2, "Fumio Kishida": 3,
        "Pope Francis": 5, "Dalai Lama": 1, "King Charles": 600,
        "Prince William": 40, "Prince Harry": 60, "Meghan Markle": 60,
        "Taylor Swift": 1100, "Beyoncé": 800, "Rihanna": 1400, "Jay-Z": 2500,
        "Kanye West": 400, "Kim Kardashian": 1500, "Kylie Jenner": 700,
        "Oprah Winfrey": 3000, "Ellen DeGeneres": 500, "Dwayne Johnson": 800,
        "Tom Cruise": 600, "Leonardo DiCaprio": 300, "Brad Pitt": 400,
        "Angelina Jolie": 150, "Scarlett Johansson": 200, "Robert Downey": 300,
        "Jennifer Lawrence": 160, "Emma Watson": 85, "Daniel Radcliffe": 120,
        "Lionel Messi": 600, "Cristiano Ronaldo": 900, "Neymar": 100,
        "Kylian Mbappe": 180, "LeBron James": 1200, "Stephen Curry": 200,
        "Kevin Durant": 300, "Tom Brady": 300, "Tiger Woods": 1300,
        "Roger Federer": 600, "Novak Djokovic": 250, "Rafael Nadal": 230,
        "Serena Williams": 300, "Naomi Osaka": 45, "Simone Biles": 20,
        "Lewis Hamilton": 300, "Max Verstappen": 200, "Shohei Ohtani": 85,
        "Patrick Mahomes": 70, "Connor McDavid": 30, "Giannis Antetokounmpo": 110,
        "Usain Bolt": 90, "Michael Phelps": 100, "Michael Jordan": 2500,
        "Magic Johnson": 1200, "David Beckham": 450, "Wayne Gretzky": 250,
        "Steven Spielberg": 5000, "James Cameron": 800, "George Lucas": 5500,
        "Peter Jackson": 1000, "Christopher Nolan": 250, "Quentin Tarantino": 120,
        "Martin Scorsese": 200, "Ridley Scott": 400, "J.K. Rowling": 1000,
        "Stephen King": 500, "Dan Brown": 180, "John Grisham": 400,
        "Sam Altman": 1000, "Sundar Pichai": 1200, "Satya Nadella": 1100,
        "Tim Cook": 2200, "Mark Cuban": 6200, "Peter Thiel": 8000,
        "Reid Hoffman": 2500, "Jack Dorsey": 4000, "Evan Spiegel": 2800,
        "Brian Chesky": 9000, "Travis Kalanick": 5000, "Garrett Camp": 3000,
        "Vitalik Buterin": 600, "Brian Armstrong": 11000, "Fred Ehrsam": 3000,
        "Richard Branson": 3000, "Phil Knight": 45000, "Howard Schultz": 4000,
    }
    return known.get(name, 5)  # Default: $5M for unknown notable people

def add_entity(data, name, nw):
    """Add a new individual entity to the data."""
    ind_template = None
    for d in data:
        if d.get('country_name_en') == '**Musk':
            ind_template = d
            break
    if not ind_template:
        return data
    
    # Clean template
    entry = json.loads(json.dumps(ind_template))
    for k, v in entry.items():
        if k.endswith('_rank') or (isinstance(v, (int, float)) and v == v and k not in ('country_code',)):
            entry[k] = None
    
    code = gen_code(f"**{name}")
    full_name = f"**{name}"
    
    entry.update({
        'flag': code,
        'country_code': code,
        'country_name_en': full_name,
        'country_name_local': full_name,
        'capital_en': 'Global',
        'continent': '⭐인물',
        'subcontinent': '뉴스인물',
        'country_summary': f"{name} - 최근 뉴스 등장, 순자산 추정 ${nw/1000:.1f}B" if nw >= 1000 else f"{name} - 최근 뉴스 등장, 순자산 추정 ${nw}M",
        'population': 1,
        'gdp': nw,
        'head_of_state_en': None,
    })
    
    # Add at end (after countries, with other entities)
    data.append(entry)
    return data

def main():
    print("🔍 Fetching trending news...")
    headlines = fetch_news()
    all_text = " ".join(headlines)
    print(f"   Fetched {len(headlines)} headlines from {len(RSS_FEEDS)} sources")
    
    print("👤 Extracting notable people...")
    people = extract_people(all_text)
    print(f"   Found {len(people)} potential names: {', '.join(list(people)[:10])}...")
    
    print("📊 Checking against existing database...")
    data, existing = load_existing()
    
    new_people = []
    for person in people:
        if person not in existing:
            new_people.append(person)
    
    print(f"   New people: {len(new_people)}")
    
    if not new_people:
        print("✅ No new people to add.")
        return
    
    # Limit additions
    new_people = new_people[:MAX_NEW_PER_RUN]
    
    # Add entities
    for person in new_people:
        nw = estimate_net_worth(person)
        data = add_entity(data, person, nw)
        nw_str = f"${nw/1000:.1f}B" if nw >= 1000 else f"${nw}M"
        print(f"   ✅ Added: **{person} ({nw_str})")
    
    # Save
    with open(COUNTRIES_FILE, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n📈 Database: {len(data)} entries (+{len(new_people)} new)")
    return len(new_people)

if __name__ == '__main__':
    count = main()
    if count:
        print(f"\n🔄 Run 'git add docs/data/countries.json && git commit && git push' to deploy")
