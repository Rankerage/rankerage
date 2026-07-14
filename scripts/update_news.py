#!/usr/bin/env python3
"""Update news_score + headlines in countries.json via Google News RSS.

Runs every minute via cron. Uses log-dampened mention counts + exponential
time decay so fresher news dominates and rankings shift minute-by-minute.

Entity matching works for countries, organizations (*), people (**),
and companies (***) — all rows in the dataset.
"""

import json, re, sys, os, math, time, urllib.request, xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "docs" / "data" / "countries.json"
SCORE_FILE = REPO / "docs" / "data" / "news_score.json"

# ── RSS feeds ──
RSS_FEEDS = [
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=world&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=business+economy&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=sports&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=technology+science&hl=en-US&gl=US&ceid=US:en",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; Rankerage/1.0; +https://rankerage.com)"
}

# ── Time decay ──
DECAY_HALF_LIFE_MINUTES = 120

# ── Topic → ranking column mapping ──
# When a headline matches a topic keyword, those columns get pulled to the front
TOPIC_COLUMNS = {
    # Sports
    "world cup|fifa|soccer|football|worldcup": ["fifa_ranking", "fifa_w", "olympic", "basket"],
    "olympic|olympics|medal": ["olympic", "olympic_gold", "olympic_per_cap", "fifa_ranking"],
    "tennis|wimbledon|us open|grand slam": ["davis_cup"],
    "cricket|ipl|test match": ["cricket", "olympic"],
    "rugby|six nations": ["rugby", "olympic"],
    "basketball|nba": ["basket", "olympic"],
    "marathon|running|track": ["marathon_elite", "olympic"],
    "chess|grandmaster": ["chess", "edu"],
    # Economy
    "gdp|economy|recession|growth|inflation|interest rate|tariff|trade war": ["gdp", "gdp_per_capita", "inflation", "unemp", "exports", "imports"],
    "stock|market|wall street|nasdaq|dow|s&p": ["gdp", "gdp_per_capita", "stock_market", "reserves"],
    "oil|gas price|energy|petroleum|crude": ["gas_price", "energy_per_capita", "co2", "renew", "exports"],
    "debt|default|bailout|imf": ["debt", "gdp", "reserves", "govern_spend"],
    "startup|venture capital|unicorn|tech ipo": ["startup_rate", "startups", "unicorns", "rd", "patents"],
    "crypto|bitcoin|ethereum|blockchain": ["internet_pct", "gdp_per_capita", "startups"],
    # Politics
    "election|vote|president|prime minister|parliament": ["democracy", "approval", "press", "election_days"],
    "protest|riot|crackdown|coup": ["democracy", "press", "gpi", "polit_kill"],
    "corruption|scandal|bribe": ["cpi", "democracy", "press"],
    "sanction|embargo|diplomat": ["exports", "imports", "gdp"],
    # Military
    "war|invasion|missile|military|troops|navy|air force": ["military_pct", "nuclear", "military_personnel", "gpi", "arms_export"],
    "nuclear|nuke|icbm|atomic": ["nuclear", "nuclear_power", "military_pct"],
    "nato|alliance": ["nato", "military_pct", "gdp"],
    # Health
    "covid|pandemic|virus|outbreak|vaccine|disease|cancer|diabetes": ["health", "life_expectancy", "doctors", "beds", "vaccination", "infant_mortality"],
    "hospital|doctor|nurse|surgeon|medical": ["doctors", "beds", "health", "life_expectancy"],
    "mental health|depression|suicide": ["suicide", "happiness", "mental_health", "health"],
    "obesity|diet|weight": ["obesity", "health", "life_expectancy"],
    "alcohol|drinking|beer|wine": ["alcohol", "beer", "wine", "health"],
    "smoking|cigarette|tobacco|vape": ["smoking", "health", "life_expectancy"],
    # Environment
    "climate|global warming|carbon|emission|greenhouse": ["co2", "renew", "forest", "pm25"],
    "earthquake|tsunami|flood|hurricane|typhoon|cyclone|wildfire|volcano": ["earthquake_count", "earthquakes", "tsunami_risk", "cyclone_freq", "flood_risk", "wildfire_freq", "volcanoes"],
    "pollution|smog|air quality": ["pm25", "co2", "health", "life_expectancy"],
    # Tech
    "ai|artificial intelligence|chatgpt|openai|machine learning": ["ai_research", "internet_pct", "patents", "rd", "startups"],
    "space|nasa|spacex|rocket|satellite": ["space_launch", "rd", "patents"],
    "5g|internet|broadband|fiber": ["internet_pct", "netspeed", "g5_coverage", "penetration"],
    # Society
    "education|school|university|student|pisa": ["edu", "literacy", "pisa_math", "pisa_science", "pisa_reading", "phd_per_cap", "students_per_teacher"],
    "crime|murder|homicide|shooting|gang": ["murder", "prison", "police", "gpi"],
    "immigration|migrant|refugee|border": ["immigration", "emigration", "refugees", "population"],
    "lgbtq|gay|trans|pride|marriage equality": ["lgbtq_rights", "gay_marriage", "gender", "democracy"],
    "women|gender|feminist|equality": ["gender", "gender_gap", "women_parl", "edu"],
    "poverty|homeless|inequality|hunger": ["poverty", "gini", "hdi", "gdp_per_capita", "homelessness"],
    # Travel
    "travel|tourism|tourist|visa|passport": ["tourism", "passport", "aviation", "airports"],
    # Culture
    "movie|film|oscar|hollywood|netflix|cinema": ["film_prod", "netflix", "intangible"],
    "music|concert|grammy|festival": ["festivals", "intangible"],
    "food|cuisine|restaurant|michelin": ["michelin", "coffee", "tea_consume", "meat", "street_food"],
    # Misc
    "nobel|prize|award": ["nobel", "nobel_per_capita", "nobel_science"],
    "happiness|wellbeing|life satisfaction": ["happiness", "life_expectancy", "hdi", "mental_health"],
    "religion|church|mosque|temple": ["religion_div", "democracy"],
    "car|auto|electric vehicle|ev|tesla": ["car_density", "gas_price", "co2"],
    "coffee|tea|espresso": ["coffee", "tea_consume"],
    "chocolate|cocoa": ["chocolate", "agri"],
    "beer|brewery|craft beer": ["beer", "alcohol"],
    "wine|vineyard": ["wine", "alcohol", "agri"],
    "mcdonald|fast food|burger": ["mcdonalds", "obesity", "meat"],
}  # end TOPIC_COLUMNS

# ── Blocklist: country codes that cause false positives (short codes matching common words) ──
BLOCKLIST = {"US", "IN", "ME", "TO", "BE", "AT", "IS", "IT", "OR", "AS", "NO", "GO", "SO", "WE", "DO", "BY", "IF", "AN", "PM", "AM", "LA", "TV", "TA", "NE", "RE"}

def load_entities():
    with open(DATA_FILE) as f:
        data = json.load(f)
    entities = []
    for row in data:
        name = (row.get("country_name_en") or "").strip()
        code = (row.get("country_code") or "").upper()
        etype = "country"
        if name.startswith("***"): etype = "org"
        elif name.startswith("**"): etype = "person"
        elif name.startswith("*"): etype = "company"
        clean = re.sub(r"^\*+", "", name).strip()
        aliases = [clean.lower()]
        local = (row.get("country_name_local") or "").strip()
        if local and local != clean:
            aliases.append(local.lower())
        if code and len(code) == 2 and code not in BLOCKLIST:
            aliases.append(code.lower())
        entities.append({"code": code, "name": clean, "type": etype, "aliases": list(set(aliases))})
    return data, entities

def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        items = []
        root = ET.fromstring(raw)
        for item_el in root.iter("item"):
            title_el = item_el.find("title")
            link_el = item_el.find("link")
            desc_el = item_el.find("description")
            pubdate_el = item_el.find("pubDate")
            title = (title_el.text or "") if title_el is not None else ""
            link = (link_el.text or "") if link_el is not None else ""
            desc = (desc_el.text or "") if desc_el is not None else ""
            pubdate_str = (pubdate_el.text or "") if pubdate_el is not None else ""
            # Parse pubDate
            age_minutes = 9999
            if pubdate_str:
                try:
                    dt = parsedate_to_datetime(pubdate_str)
                    age_minutes = (datetime.now(timezone.utc) - dt).total_seconds() / 60
                except Exception:
                    pass
            # Extract image
            img = ""
            for mc in item_el.findall("{http://search.yahoo.com/mrss/}content"):
                url_attr = mc.get("url", "")
                if url_attr:
                    img = url_attr
                    break
            if not img and desc:
                m = re.search(r'<img[^>]+src=["\']([^"\']+)', desc)
                if m:
                    img = m.group(1)
            clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()
            source_el = item_el.find("source")
            source = (source_el.text or "") if source_el is not None else ""
            items.append({
                "title": title, "link": link, "desc": clean_desc[:300],
                "img": img, "source": source, "age_minutes": age_minutes,
            })
        return items
    except Exception as e:
        print(f"  ⚠ {url.split('?')[1][:40] if '?' in url else url}: {e}", file=sys.stderr)
        return []

def time_weight(age_minutes):
    """Exponential decay: 1.0 at t=0, 0.5 at HALF_LIFE minutes."""
    if age_minutes <= 0:
        return 1.0
    return math.exp(-math.log(2) * age_minutes / DECAY_HALF_LIFE_MINUTES)

def extract_topics(text):
    """Match headline text against TOPIC_COLUMNS regexes, return deduped column fields."""
    text_lower = text.lower()
    columns = []
    for pattern, fields in TOPIC_COLUMNS.items():
        if re.search(pattern, text_lower):
            columns.extend(fields)
    # Deduplicate, keep order
    seen = set()
    return [f for f in columns if not (f in seen or seen.add(f))]

def match_entities(text, entities):
    text_lower = text.lower()
    matched = []
    for ent in entities:
        for alias in ent["aliases"]:
            if len(alias) < 3:
                continue  # skip very short aliases
            pattern = r"\b" + re.escape(alias) + r"\b"
            if re.search(pattern, text_lower):
                matched.append(ent["code"])
                break
    return matched

def compute_scores(weighted_mentions, historical):
    """Time-weighted count → log-dampened + EMA smoothed."""
    scores = {}
    for code, tw in weighted_mentions.items():
        raw = math.log2(1 + tw)  # log2 dampening
        prev = historical.get(code, raw)
        # EMA: 70% history, 30% new — smooths minute-to-minute jitter
        scores[code] = round(prev * 0.7 + raw * 0.3, 2)
    return scores

def main():
    data, entities = load_entities()
    print(f"Loaded {len(entities)} entities")

    historical = {}
    if SCORE_FILE.exists():
        with open(SCORE_FILE) as f:
            historical = json.load(f)

    # Fetch all feeds
    all_items = []
    for url in RSS_FEEDS:
        items = fetch_rss(url)
        label = url.split("?")[1][:35] if "?" in url else url.split("/")[-1]
        print(f"  {label}: {len(items)} items")
        all_items.extend(items)

    # Deduplicate by title
    seen = set()
    unique_items = []
    for item in all_items:
        key = item["title"][:80]
        if key not in seen:
            seen.add(key)
            unique_items.append(item)
    print(f"Unique headlines: {len(unique_items)}")

    # Match entities with time-weighted scoring
    weighted_mentions = defaultdict(float)  # code → time-weighted score
    entity_headlines = {}  # code → best (freshest) headline

    for item in unique_items:
        text = f"{item['title']} {item['desc']}"
        tw = time_weight(item["age_minutes"])
        for code in match_entities(text, entities):
            weighted_mentions[code] += tw
            # Keep the freshest headline (lowest age)
            existing = entity_headlines.get(code)
            if not existing or item["age_minutes"] < existing.get("age_minutes", 9999):
                entity_headlines[code] = item

    # Compute final scores with EMA smoothing
    scores = compute_scores(weighted_mentions, historical)

    # Update data
    code_to_idx = {}
    for i, row in enumerate(data):
        code_to_idx[(row.get("country_code") or "").upper()] = i

    updated = 0
    for code in code_to_idx:
        idx = code_to_idx[code]
        score = scores.get(code, 0)
        data[idx]["news_score"] = round(score, 2)
        hl = entity_headlines.get(code)
        if hl:
            data[idx]["news_title"] = hl["title"]
            data[idx]["news_url"] = hl["link"]
            data[idx]["news_image"] = hl["img"]
            data[idx]["news_source"] = hl["source"]
            data[idx]["news_age"] = f"{int(hl['age_minutes'])}m ago" if hl["age_minutes"] < 120 else f"{int(hl['age_minutes']/60)}h ago"
            # Topic → related ranking columns
            topics = extract_topics(f"{hl['title']} {hl['desc']}")
            if topics:
                data[idx]["news_columns"] = topics[:6]  # max 6 related columns
        else:
            # Decay old score if no recent mentions
            old = data[idx].get("news_score", 0)
            data[idx]["news_score"] = round(old * 0.95, 2)  # 5% decay per tick
        updated += 1

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    all_scores = {code: scores.get(code, 0) for code in code_to_idx}
    with open(SCORE_FILE, "w") as f:
        json.dump(all_scores, f, ensure_ascii=False)

    top = sorted(scores.items(), key=lambda x: -x[1])[:10]
    print(f"\nUpdated {updated} entities. Top 10 (decay HL={DECAY_HALF_LIFE_MINUTES}m):")
    for code, score in top:
        idx = code_to_idx.get(code)
        name = data[idx]["country_name_en"].lstrip("*") if idx is not None else "?"
        hl = entity_headlines.get(code, {})
        age = hl.get("age_minutes", "?")
        title = hl.get("title", "-")[:55]
        print(f"  {score:5.2f}  {name:<22s}  [{int(age)}m] {title}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
