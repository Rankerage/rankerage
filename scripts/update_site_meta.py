#!/usr/bin/env python3
"""update_site_meta.py — 실제 지표 수를 세서 site_meta.json 갱신"""
import json, os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "docs", "data", "countries.json")
META_FILE = os.path.join(BASE, "docs", "data", "site_meta.json")

META_KEYS = {
    "flag", "country_summary", "country_code", "country_name_en",
    "country_name_local", "capital_en", "capital_local", "continent",
    "subcontinent", "ethnic", "head_of_state_en", "head_of_state_local",
    "lat", "lon", "national_anthem_en", "national_anthem_local",
    "election_date", "brics_member", "brics_year", "oecd_member", "oecd_year",
}

with open(DATA_FILE, encoding="utf-8") as f:
    countries = json.load(f)

all_keys = set(countries[0].keys())
metrics = {k for k in all_keys if not k.endswith("_rank")} - META_KEYS

with open(META_FILE, "r", encoding="utf-8") as f:
    meta = json.load(f)

meta["total_rankings"] = len(metrics)
meta["total_countries"] = len(countries)
meta["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

with open(META_FILE, "w", encoding="utf-8") as f:
    json.dump(meta, f, ensure_ascii=False, indent=2)

print(f"📊 total_rankings = {len(metrics)} (total_countries = {len(countries)})")
