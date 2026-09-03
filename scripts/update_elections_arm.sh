#!/bin/bash
# rankerage elections refresh — ARM daily 06:00 KST (21:00 UTC)
set -e
REPO=/home/ubuntu/rankerage
cd "$REPO"
timeout 15 git pull origin master 2>/dev/null || true
python3 scripts/update_elections.py 2>&1
if ! git diff --quiet docs/data/countries.json; then
    git add docs/data/countries.json
    git commit -m "🗳️ Elections update: $(date +%Y-%m-%d)"
    git push origin master
    echo "✓ Elections pushed"
else
    echo "— No election changes"
fi
