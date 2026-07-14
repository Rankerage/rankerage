#!/usr/bin/env python3
"""
fill_data_v2.py — rankerage.com data filler (robust version)
1) Hardcoded membership data (immediate save)
2) World Bank API (10-country batches, save after each indicator)
3) Update site_meta.json
"""

import json, time, urllib.request, sys, os, socket

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
DATA = f"{REPO}/docs/data/countries.json"
META = f"{REPO}/docs/data/site_meta.json"

# ── Hardcoded Membership ──
OECD = {"AT":1961,"BE":1961,"CA":1961,"DK":1961,"FR":1961,"DE":1961,"GR":1961,
        "IS":1961,"IE":1961,"IT":1961,"LU":1961,"NL":1961,"NO":1961,"PT":1961,
        "ES":1961,"SE":1961,"CH":1961,"TR":1961,"GB":1961,"US":1961,
        "JP":1964,"FI":1969,"AU":1971,"NZ":1973,"MX":1994,"CZ":1995,
        "HU":1996,"PL":1996,"KR":1996,"SK":2000,"CL":2010,"SI":2010,
        "IL":2010,"EE":2010,"LV":2016,"LT":2018,"CO":2020,"CR":2021}

G20 = {"AR","AU","BR","CA","CN","FR","DE","IN","ID","IT","JP","KR","MX","RU","SA","ZA","TR","GB","US"}
EU27 = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}
ASEAN = {"BN","KH","ID","LA","MY","MM","PH","SG","TH","VN"}
APEC = {"AU","BN","CA","CL","CN","HK","ID","JP","KR","MY","MX","NZ","PG","PE","PH","RU","SG","TW","TH","US","VN"}
G7 = {"CA","FR","DE","IT","JP","GB","US"}
NATO = {"BE":1949,"CA":1949,"DK":1949,"FR":1949,"IS":1949,"IT":1949,"LU":1949,
        "NL":1949,"NO":1949,"PT":1949,"GB":1949,"US":1949,"GR":1952,"TR":1952,
        "DE":1955,"ES":1982,"CZ":1999,"HU":1999,"PL":1999,"BG":2004,"EE":2004,
        "LV":2004,"LT":2004,"RO":2004,"SK":2004,"SI":2004,"AL":2009,"HR":2009,
        "ME":2017,"MK":2020,"FI":2023,"SE":2024}

# ── World Bank Indicators ──
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

socket.setdefaulttimeout(60)

def fetch_wb_indicator(code, iso3_list, batch_size=10):
    """Fetch one indicator for all countries in batches"""
    data = {}
    for i in range(0, len(iso3_list), batch_size):
        batch = iso3_list[i:i+batch_size]
        url = f"https://api.worldbank.org/v2/country/{';'.join(batch)}/indicator/{code}?format=json&per_page=500"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
            with urllib.request.urlopen(req, timeout=90) as r:
                d = json.loads(r.read())
            if d and len(d) > 1 and d[1]:
                for e in d[1]:
                    if e["value"] is not None:
                        iso3 = e["countryiso3code"]
                        yr = e["date"]
                        if iso3 not in data or yr > data[iso3][0]:
                            data[iso3] = (yr, e["value"])
            time.sleep(0.3)
        except Exception as ex:
            sys.stderr.write(f"  [!] batch {i//batch_size} error: {ex}\n")
            time.sleep(1)
    return {k: v[1] for k, v in data.items()}


def save_countries(countries):
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False)


def main():
    print("🚀 rankerage.com 데이터 채우기 v2")
    print("=" * 50)

    # Load countries
    with open(DATA, encoding="utf-8") as f:
        countries = json.load(f)
    print(f"   Loaded {len(countries)} countries")

    # ── ISO2 → ISO3 mapping ──
    print("\n📡 Fetching ISO code mapping...")
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        wb_all = json.loads(r.read())

    iso2_to_iso3 = {}
    for c in wb_all[1]:
        i2 = c.get("iso2Code", "").strip().upper()
        i3 = c.get("id", "").strip()
        if i2 and i3 and i2 != "": 
            iso2_to_iso3[i2] = i3

    # Build iso3 list from our countries
    iso3_set = set()
    for c in countries:
        i3 = iso2_to_iso3.get(c["country_code"].upper())
        if i3:
            iso3_set.add(i3)
    iso3_list = sorted(iso3_set)
    print(f"   {len(iso3_list)} countries mapped to ISO3")

    # ── PHASE 1: Hardcoded Membership ──
    print("\n📌 Phase 1: Hardcoded membership data...")
    hard_fields = ["oecd_member_order", "g20_member", "eu_member", "asean_member", "apec_member", "g7_member", "nato_year"]
    
    for c in countries:
        iso2 = c["country_code"].upper()
        c["oecd_member_order"] = OECD.get(iso2)
        c["g20_member"] = 1 if iso2 in G20 else 0
        c["eu_member"] = 1 if iso2 in EU27 else 0
        c["asean_member"] = 1 if iso2 in ASEAN else 0
        c["apec_member"] = 1 if iso2 in APEC else 0
        c["g7_member"] = 1 if iso2 in G7 else 0
        c["nato_year"] = NATO.get(iso2)
        # rank fields
        for f in hard_fields:
            c[f"{f}_rank"] = None

    # Count stats
    oecd_count = len([c for c in countries if c.get("oecd_member_order")])
    g20_count = len([c for c in countries if c.get("g20_member")])
    eu_count = len([c for c in countries if c.get("eu_member")])
    asean_count = len([c for c in countries if c.get("asean_member")])
    apec_count = len([c for c in countries if c.get("apec_member")])
    g7_count = len([c for c in countries if c.get("g7_member")])
    nato_count = len([c for c in countries if c.get("nato_year")])
    print(f"   OECD={oecd_count}, G20={g20_count}, EU={eu_count}, ASEAN={asean_count}, APEC={apec_count}, G7={g7_count}, NATO={nato_count}")

    # Save after phase 1
    save_countries(countries)
    print("   ✅ Saved after phase 1")

    # ── PHASE 2: World Bank API ──
    print(f"\n🌐 Phase 2: World Bank API ({len(WB)} indicators)")
    total_new = 0
    for idx, (field, code) in enumerate(WB.items(), 1):
        sys.stdout.write(f"   [{idx}/{len(WB)}] {field:22s}... ")
        sys.stdout.flush()
        
        wb_data = fetch_wb_indicator(code, iso3_list, batch_size=10)
        added = 0
        for c in countries:
            iso2 = c["country_code"].upper()
            i3 = iso2_to_iso3.get(iso2)
            if i3 and i3 in wb_data:
                val = wb_data[i3]
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
        
        print(f"{added} countries")
        total_new += added
        
        # Save after each indicator (safety)
        save_countries(countries)

    # ── FINAL: Update site_meta ──
    print(f"\n💾 Final save + site_meta update...")
    
    # Count metrics (non-rank, non-desc, non-meta fields that are numeric)
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
    print(f"   Hardcoded: 7 membership fields ({oecd_count}+ countries)")
    print(f"   World Bank: {total_new} data points across {len(WB)} indicators")
    print(f"   Rankings: {old_rankings} → {metrics} (site_meta updated)")
    print(f"   File saved: {DATA}")


if __name__ == "__main__":
    main()
