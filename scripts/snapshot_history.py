#!/usr/bin/env python3
"""snapshot_history.py — countries.json 스냅샷을 history.json에 누적 저장
모든 지표의 과거 추이를 쌓아서 트렌드 그래프 데이터로 활용
매일 실행 → 각 지표별로 오늘 날짜의 값을 기록
"""
import json, sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "docs" / "data" / "countries.json"
HIST_FILE = REPO / "docs" / "data" / "history.json"

with open(DATA_FILE) as f:
    countries = json.load(f)

hist = {}
if HIST_FILE.exists():
    with open(HIST_FILE) as f:
        hist = json.load(f)

today = str(date.today())
updated = 0

for c in countries:
    code = c.get('country_code', '').upper()
    if not code or len(code) > 3:  # XX 접두어 엔티티 제외
        continue
    for k, v in c.items():
        if k.startswith('_') or k.endswith('_rank') or k in ('country_code','country_name_en','country_name_local',
            'flag','capital_en','capital_local','continent','subcontinent','ethnic','head_of_state_en',
            'head_of_state_local','lat','lon','national_anthem_en','national_anthem_local','country_summary',
            'election_date','election_title','election_url','news_title','news_url','news_image','news_source',
            'news_age','news_columns','news_score','brics_member','brics_year','oecd_member','oecd_year',
            'g20_member','eu_member','asean_member','apec_member','g7_member'):
            continue
        if v is None:
            continue
        if k not in hist:
            hist[k] = {}
        if code not in hist[k]:
            hist[k][code] = {}
        hist[k][code][today] = v
        updated += 1

with open(HIST_FILE, 'w') as f:
    json.dump(hist, f, ensure_ascii=False)

print(f"✅ {updated}개 값 스냅샷 저장 ({today})")
