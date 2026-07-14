#!/usr/bin/env python3
"""
fill_data.py — rankerage.com 데이터 채우기
1) 국제기구 하드코딩 (즉시)
2) World Bank API (작은 배치 + 긴 타임아웃)
"""

import json, time, urllib.request, sys, os, socket

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
DATA = f"{REPO}/docs/data/countries.json"
META = f"{REPO}/docs/data/site_meta.json"

# ── 하드코딩 ──
OECD = {"AT":1961,"BE":1961,"CA":1961,"DK":1961,"FR":1961,"DE":1961,"GR":1961,
        "IS":1961,"IE":1961,"IT":1961,"LU":1961,"NL":1961,"NO":1961,"PT":1961,
        "ES":1961,"SE":1961,"CH":1961,"TR":1961,"GB":1961,"US":1961,
        "JP":1964,"FI":1969,"AU":1971,"NZ":1973,"MX":1994,"CZ":1995,
        "HU":1996,"PL":1996,"KR":1996,"SK":2000,"CL":2010,"SI":2010,
        "IL":2010,"EE":2010,"LV":2016,"LT":2018,"CO":2020,"CR":2021}

G20 = {"AR","AU","BR","CA","CN","FR","DE","IN","ID","IT","JP","KR","MX","RU","SA","ZA","TR","GB","US","EU"}
EU27 = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}
ASEAN = {"BN","KH","ID","LA","MY","MM","PH","SG","TH","VN"}
APEC = {"AU","BN","CA","CL","CN","HK","ID","JP","KR","MY","MX","NZ","PG","PE","PH","RU","SG","TW","TH","US","VN"}
G7 = {"CA","FR","DE","IT","JP","GB","US"}
NATO = {"BE":1949,"CA":1949,"DK":1949,"FR":1949,"IS":1949,"IT":1949,"LU":1949,
        "NL":1949,"NO":1949,"PT":1949,"GB":1949,"US":1949,"GR":1952,"TR":1952,
        "DE":1955,"ES":1982,"CZ":1999,"HU":1999,"PL":1999,"BG":2004,"EE":2004,
        "LV":2004,"LT":2004,"RO":2004,"SK":2004,"SI":2004,"AL":2009,"HR":2009,
        "ME":2017,"MK":2020,"FI":2023,"SE":2024}

# ── World Bank API (핵심 12개) ──
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

socket.setdefaulttimeout(45)

def fetch_wb(code, iso3_list):
    data = {}
    for i in range(0, len(iso3_list), 15):
        batch = iso3_list[i:i+15]
        url = f"https://api.worldbank.org/v2/country/{';'.join(batch)}/indicator/{code}?format=json&per_page=500"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.loads(r.read())
            if d and len(d) > 1 and d[1]:
                for e in d[1]:
                    if e["value"] is not None:
                        iso3 = e["countryiso3code"]
                        yr = e["date"]
                        if iso3 not in data or yr > data[iso3][0]:
                            data[iso3] = (yr, e["value"])
            time.sleep(0.6)
        except Exception as ex:
            pass
    return {k: v[1] for k, v in data.items()}


def main():
    print("🚀 rankerage.com 데이터 채우기")
    print("=" * 50)

    with open(DATA, encoding="utf-8") as f:
        countries = json.load(f)

    # ISO 매핑
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"R/1"})) as r:
        wb_all = json.loads(r.read())

    iso2_to_iso3 = {}
    for c in wb_all[1]:
        i2 = c.get("iso2Code","").strip()
        i3 = c.get("id","").strip()
        if i2 and i3: iso2_to_iso3[i2] = i3

    iso3_set = set()
    for c in countries:
        i3 = iso2_to_iso3.get(c["country_code"].upper())
        if i3: iso3_set.add(i3)
    iso3_list = sorted(iso3_set)
    print(f"   {len(iso3_list)}개국 매핑")

    # ── 1단계: 하드코딩 주입 ──
    print("\n📌 하드코딩 데이터 주입 중...")
    for c in countries:
        iso2 = c["country_code"].upper()

        c["oecd_member_order"] = OECD.get(iso2)
        c["g20_member"] = 1 if iso2 in G20 else 0
        c["eu_member"] = 1 if iso2 in EU27 else 0
        c["asean_member"] = 1 if iso2 in ASEAN else 0
        c["apec_member"] = 1 if iso2 in APEC else 0
        c["g7_member"] = 1 if iso2 in G7 else 0
        c["nato_year"] = NATO.get(iso2)

    # rank 필드 초기화
    hard_fields = ["oecd_member_order","g20_member","eu_member","asean_member","apec_member","g7_member","nato_year"]
    for f in hard_fields:
        rf = f"{f}_rank"
        for c in countries:
            if rf not in c: c[rf] = None
    print(f"   OECD({len(OECD)}), G20({len([c for c in countries if c.get('g20_member')])}), EU({len([c for c in countries if c.get('eu_member')])}), ASEAN({len([c for c in countries if c.get('asean_member')])}), APEC({len([c for c in countries if c.get('apec_member')])}), G7({len([c for c in countries if c.get('g7_member')])}), NATO({len(NATO)})")

    # ── 2단계: World Bank API ──
    print(f"\n🌐 World Bank API ({len(WB)}개 지표)")
    total_new = 0
    for field, code in WB.items():
        sys.stdout.write(f"   {field:20s}... ")
        sys.stdout.flush()
        wb_data = fetch_wb(code, iso3_list)
        added = 0
        for c in countries:
            iso2 = c["country_code"].upper()
            i3 = iso2_to_iso3.get(iso2)
            if i3 and i3 in wb_data:
                val = wb_data[i3]
                if field in ("women_parl","teen_pregnancy","diabetes","cancer","mental_health",
                            "hiv_prev","extreme_poverty","child_labor","child_marriage","union_rate"):
                    val = round(val, 1)
                elif field == "refugees":
                    val = round(val)
                c[field] = val
                c[f"{field}_rank"] = None
                added += 1
            else:
                c[field] = None
                c[f"{field}_rank"] = None
        print(f"{added}개국")
        total_new += added

    # ── 저장 ──
    print(f"\n💾 저장 중...")
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False)

    # 통계
    metrics = len([k for k in countries[0].keys() if not k.endswith("_rank") and not k.endswith("_desc") 
                   and k not in ("flag","country_summary","country_name_en","country_name_local",
                                "capital_en","capital_local","continent","subcontinent","ethnic",
                                "head_of_state_en","head_of_state_local","lat","lon",
                                "national_anthem_en","national_anthem_local","country_code",
                                "election_date","brics_member","brics_year","oecd_member","oecd_year")])

    with open(META) as f:
        meta = json.load(f)
    meta["total_rankings"] = metrics
    meta["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(META, "w") as f:
        json.dump(meta, f, ensure_ascii=False)

    print(f"\n✅ 완료!")
    print(f"   하드코딩: 7개 지표 ({len(OECD)}+α개국)")
    print(f"   World Bank: {total_new}건 데이터")
    print(f"   총 랭킹: {metrics} → site_meta 업데이트 완료")

if __name__ == "__main__":
    main()
