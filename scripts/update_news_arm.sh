#!/bin/bash
# rankerage news refresh — ARM (migrated from Windows WSL 2026-09-04)
# cron: */30 * * * *
set -e
REPO=/home/ubuntu/rankerage
cd "$REPO"
[ -f .env ] && export $(grep -v '^#' .env | xargs)
timeout 15 git pull origin master 2>/dev/null || true
python3 scripts/update_news.py 2>&1
if ! git diff --quiet docs/data/countries.json; then
    git add docs/data/countries.json
    COUNT=$(python3 -c "import json;d=json.load(open('docs/data/countries.json'));print(sum(1 for r in d if r.get('news_score',0)>0))")
    git commit -m "📰 News refresh: $COUNT entities updated ($(date +%H:%M))"
    git push origin master
    echo "✓ Pushed — $COUNT entities with news"
else
    echo "— No news changes"
fi
