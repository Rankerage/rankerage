#!/usr/bin/env python3
"""
fill_wb_only.py — Fetch World Bank data using the fast 'all' endpoint approach.
Runs after hardcoded membership is already saved.
"""

import json, time, urllib.request, sys, os, socket

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
DATA = f"{REPO}/docs/data/countries.json"
META = f"{REPO}/docs/data/site_meta.json"

WB = {
    "women_parl":       "SG.GEN.PARL.ZS",
    "teen_pregnancy":   "SP.ADO.TFRT",
    "college_rate":     "SE.TER.ENRR",
    "diabetes":         "SH.STA.DIAB.ZS",
    "cancer":           "SH.CMS.LIFE.FE.ZS",
    "mental_health":    "SH.STA.MHAD.P5",
    "hiv_prev":         "SH.DYN.AIDS.ZS",
    "extreme_poverty":  "SI.POV.DDAY",
    "child_labor":      "SL.TLF.0714.ZS",
    "child_marriage":   "SP.M15.2024.FE.ZS",
    "refugees":         "SM.POP.REFG.OR",
    "union_rate":       "SL.TLF.ACTI.ZS",
}

ROUND_FIELDS = {"women_parl","teen_pregnancy","diabetes","cancer","mental_health",
                "hiv_prev","extreme_poverty","child_labor","child_marriage","union_rate"}
INT_FIELDS = {"refugees"}

socket.setdefaulttimeout(90)

def fetch_indicator_all(code):
    """Fetch all countries for one indicator using the 'all' endpoint"""
    data = {}
    page = 1
    while True:
        url = f"https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&page={page}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.loads(r.read())
            if d and len(d) > 1 and d[1]:
                for e in d[1]:
                    if e["value"] is not None:
                        iso3 = e["countryiso3code"]
                        yr = e["date"]
                        if iso3 not in data or yr > data[iso3][0]:
                            data[iso3] = (yr, e["value"])
            total_pages = d[0].get("pages", 1)
            if page >= total_pages:
                break
            page += 1
            time.sleep(0.2)
        except Exception as ex:
            sys.stderr.write(f"  [!] page {page} error: {ex}\n")
            break
    return {k: v[1] for k, v in data.items()}


def save_countries(countries):
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False)


def main():
    print("🌐 World Bank API - Fast 'all' endpoint fetch")
    print("=" * 50)

    # Load countries
    with open(DATA, encoding="utf-8") as f:
        countries = json.load(f)
    print(f"   Loaded {len(countries)} countries")

    # ── ISO2 → ISO3 mapping ──
    print("📡 Fetching ISO code mapping...")
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        wb_all = json.loads(r.read())

    iso2_to_iso3 = {}
    wb_country_iso3s = set()
    for c in wb_all[1]:
        i2 = c.get("iso2Code", "").strip().upper()
        i3 = c.get("id", "").strip()
        region_id = c.get("region", {}).get("id", "")
        # Only include actual countries (not aggregates like "WLD", "EAS", "ECS")
        if region_id != "NA" and i3 and len(i3) == 3 and i3[0] != 'X':
            wb_country_iso3s.add(i3)
            if i2:
                iso2_to_iso3[i2] = i3

    # Build iso3 list from our countries
    iso3_set = set()
    for c in countries:
        i3 = iso2_to_iso3.get(c["country_code"].upper())
        if i3:
            iso3_set.add(i3)
    iso3_list = sorted(iso3_set)
    print(f"   {len(iso3_list)} of our countries mapped to WB ISO3 codes")
    print(f"   {len(wb_country_iso3s)} actual country codes known (for filtering)")

    # ── Fetch each indicator ──
    print(f"\n📊 Fetching {len(WB)} indicators...")
    total_new = 0
    for idx, (field, code) in enumerate(WB.items(), 1):
        t0 = time.time()
        sys.stdout.write(f"   [{idx:2d}/{len(WB)}] {field:22s} ... ")
        sys.stdout.flush()
        
        wb_data = fetch_indicator_all(code)
        
        # Filter to only actual country codes (not aggregates like AFE, ARB, etc.)
        filtered = {k: v for k, v in wb_data.items() if k in wb_country_iso3s}
        t1 = time.time()
        
        added = 0
        for c in countries:
            iso2 = c["country_code"].upper()
            i3 = iso2_to_iso3.get(iso2)
            if i3 and i3 in filtered:
                val = filtered[i3]
                if field in ROUND_FIELDS:
                    val = round(val, 1)
                elif field in INT_FIELDS:
                    val = round(val)
                c[field] = val
            else:
                c[field] = None
            c[f"{field}_rank"] = None
            if c[field] is not None:
                added += 1
        
        elapsed = t1 - t0
        print(f"{added:3d} countries ({elapsed:.1f}s)")
        total_new += added
        
        # Save after each indicator
        save_countries(countries)

    # ── Update site_meta ──
    print(f"\n💾 Updating site_meta...")
    
    meta_keys = {"flag","country_summary","country_name_en","country_name_local",
                 "capital_en","capital_local","continent","subcontinent","ethnic",
                 "head_of_state_en","head_of_state_local","lat","lon",
                 "national_anthem_en","national_anthem_local","country_code",
                 "election_date","brics_member","brics_year","oecd_member","oecd_year"}
    
    metrics = len([k for k in countries[0].keys() 
                   if not k.endswith("_rank") and not k.endswith("_desc") 
                   and k not in meta_keys])
    
    with open(META) as f:
        meta = json.load(f)
    old_rankings = meta.get("total_rankings", 0)
    meta["total_rankings"] = metrics
    meta["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(META, "w") as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"✅ COMPLETE!")
    print(f"   World Bank: {total_new} data points ({len(WB)} indicators)")
    print(f"   Rankings: {old_rankings} → {metrics}")
    print(f"   Saved: {DATA}")


if __name__ == "__main__":
    main()
