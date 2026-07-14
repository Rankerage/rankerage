#!/usr/bin/env python3
"""
Compute News Score for all entities based on recent news mentions.
Higher score = more frequently mentioned in current news.
"""
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime

try:
    import feedparser
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "feedparser", "-q"])
    import feedparser

DATA_DIR = Path(__file__).resolve().parent.parent / "docs" / "data"
COUNTRIES_FILE = DATA_DIR / "countries.json"
NEWS_SCORE_FILE = DATA_DIR / "news_score.json"

RSS_FEEDS = [
    "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

def load_entities():
    with open(COUNTRIES_FILE) as f:
        return json.load(f)

def extract_keywords(name):
    """Generate search keywords from entity name."""
    clean = name.lstrip('*')
    keywords = [clean.lower()]
    parts = clean.split()
    if len(parts) > 1:
        keywords.append(parts[-1].lower())  # Last name
    return keywords

def compute_scores(entities, headlines):
    """Score each entity by mention count in headlines."""
    scores = {}
    all_text = " ".join(headlines).lower()
    
    for entity in entities:
        name = entity.get('country_name_en', '')
        score = 0
        for kw in extract_keywords(name):
            # Count case-insensitive mentions
            count = len(re.findall(re.escape(kw), all_text))
            score += count
        
        if score > 0:
            scores[name] = {
                'score': score,
                'name': name,
                'country_code': entity.get('country_code', ''),
                'summary': entity.get('country_summary', ''),
            }
    
    # Sort by score desc
    sorted_scores = dict(sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True))
    return sorted_scores

def update_news_score_field(entities, scores):
    """Add news_score field to entity data."""
    for entity in entities:
        name = entity.get('country_name_en', '')
        entity['news_score'] = scores.get(name, {}).get('score', 0)
    return entities

def main():
    print("📰 Fetching news...")
    headlines = []
    headline_items = []  # Store {title, link, source}
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source = feed.feed.get('title','News')[:20]
            for entry in feed.entries[:15]:
                title = entry.get('title', '')
                link = entry.get('link', '')
                headlines.append(title)
                headline_items.append({'title':title, 'link':link, 'source':source})
        except Exception as e:
            print(f"  ⚠️ {url[:50]}: {e}")
    
    print(f"   {len(headlines)} headlines")
    
    print("🔍 Loading entities...")
    entities = load_entities()
    print(f"   {len(entities)} entities")
    
    print("📊 Computing mention scores...")
    scores = compute_scores(entities, headlines)
    trending = list(scores.values())[:20]
    
    print(f"\n   Top 20 Trending:")
    for i, s in enumerate(trending[:10], 1):
        bar = "█" * min(s['score'], 20)
        print(f"   {i:2}. {s['name']:30s} {bar} ({s['score']})")
    
    # Save scores
    with open(NEWS_SCORE_FILE, 'w') as f:
        json.dump({
            'updated': datetime.now().isoformat(),
            'total_headlines': len(headlines),
            'trending': trending,
            'all_scores': scores,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Saved to {NEWS_SCORE_FILE}")
    
    # Also update entities with news_score
    entities = update_news_score_field(entities, scores)
    with open(COUNTRIES_FILE, 'w') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Updated {len(entities)} entities with news_score field")
    return len(trending)

if __name__ == '__main__':
    main()
