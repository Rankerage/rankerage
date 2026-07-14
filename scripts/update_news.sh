#!/bin/bash
# Ran every minute by cron — fetches news, updates countries.json, commits + pushes
set -e
REPO=/mnt/c/Users/mathe/Desktop/rankerage
cd "$REPO"
# Load API keys
[ -f .env ] && export $(grep -v '^#' .env | xargs)

# Pull latest to avoid conflicts (with timeout)
timeout 15 git pull origin master 2>/dev/null || true

# Run news scraper
python3 scripts/update_news.py 2>&1

# Commit if data changed
if ! git diff --quiet docs/data/countries.json; then
    git add docs/data/countries.json
    COUNT=$(python3 -c "import json;d=json.load(open('docs/data/countries.json'));print(sum(1 for r in d if r.get('news_score',0)>0))")
    git commit -m "📰 News refresh: $COUNT entities updated ($(date +%H:%M))"
    git push origin master
    echo "✓ Pushed — $COUNT entities with news"
else
    echo "— No news changes"
fi
