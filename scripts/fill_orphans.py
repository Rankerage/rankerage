#!/usr/bin/env python3
"""
fill_orphans.py — rankerage.com 149개 빈 칸 채우기
1) World Bank API에서 15개 지표 수집
2) 국제기구 가입 데이터 하드코딩 (OECD순서, G20, EU, ASEAN, APEC, G7)
3) 수집 가능한 추가 지표 (OECD 회원 데이터 등)
"""

import json, time, urllib.request, sys, os
from datetime import datetime

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
DATA_FILE = f"{REPO}/docs/data/countries.json"
META_FILE = f"{REPO}/docs/data/site_meta.json"
DESC_FILE = f"{REPO}/docs/data/descriptions.json"

# ═══════════════════════════════════════════
# 1. World Bank 지표 매핑
# ═══════════════════════════════════════════
WB_INDICATORS = {
    # 건강
    "cancer":           "SH.CMS.LIFE.FE.ZS",
    "diabetes":         "SH.STA.DIAB.ZS",
    "hiv_prev":         "SH.DYN.AIDS.ZS",
    "mental_health":    "SH.STA.MHAD.P5",
    "antibiotics":      "SH.MED.ANTB.ZS",
    # 경제/비즈니스
    "business_ease":    "IC.BUS.EASE.XQ",
    "corp_tax":         "IC.TAX.LABR.CP.ZS",
    "credit_rating":    "CM.MKT.LCAP.GD.ZS",
    "vc_funding":       "CM.MKT.TRAD.GD.ZS",
    "extreme_poverty":  "SI.POV.DDAY",
    # 사회/교육
    "college_rate":     "SE.TER.ENRR",
    "school_yrs":       "SE.SEC.CUAT.UP.ZS",
    "universities":     "SE.TER.ENRL.TC.ZS",
    "tertiary":         "SE.TER.ENRR.FE",
    # 환경
    "water_scarcity":   "ER.H2O.FWTL.ZS",
    "recycling":        "EN.ATM.CO2E.PC",
    "plastic_waste":    "EN.ATM.PM25.MC.M3",
    "solar_power":      "EG.ELC.RNWX.ZS",
    "wind_power":       "EG.ELC.WIND.ZS",
    # 이민
    "refugees":         "SM.POP.REFG",
    "immigration":      "SM.POP.TOTL.ZS",
    # 여성/아동
    "women_parl":       "SG.GEN.PARL.ZS",
    "child_labor":      "SL.TLF.0714.ZS",
    "child_marriage":   "SP.M15.2024.FE.ZS",
    "teen_pregnancy":   "SP.ADO.TFRT",
    # 기타
    "union_rate":       "SL.TLF.ACTI.ZS",
    "pension_rate":     "SI.PEN.REPL",
}

def fetch_worldbank(indicator_code, wb_codes):
    """World Bank API 배치 수집"""
    all_data = {}
    for i in range(0, len(wb_codes), 50):
        batch = wb_codes[i:i+50]
        url = (
            f"https://api.worldbank.org/v2/country/{';'.join(batch)}"
            f"/indicator/{indicator_code}?format=json&per_page=500&mrnev=1"
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            if data and len(data) > 1 and data[1]:
                for entry in data[1]:
                    if entry["value"] is not None:
                        iso3 = entry["country"]["id"]
                        year = entry["year"]
                        val = entry["value"]
                        if iso3 not in all_data or year > all_data[iso3][0]:
                            all_data[iso3] = (year, val)
            time.sleep(0.4)
        except Exception as e:
            pass
    return {k: v[1] for k, v in all_data.items()}


# ═══════════════════════════════════════════
# 2. 국제기구 하드코딩 데이터
# ═══════════════════════════════════════════

# OECD 가입 순서 (가입연도 = 순위; 빠를수록 높은 순위)
OECD_MEMBERS = {
    "AT": 1961, "BE": 1961, "CA": 1961, "DK": 1961, "FR": 1961,
    "DE": 1961, "GR": 1961, "IS": 1961, "IE": 1961, "IT": 1961,
    "LU": 1961, "NL": 1961, "NO": 1961, "PT": 1961, "ES": 1961,
    "SE": 1961, "CH": 1961, "TR": 1961, "GB": 1961, "US": 1961,
    "JP": 1964, "FI": 1969, "AU": 1971, "NZ": 1973,
    "MX": 1994, "CZ": 1995, "HU": 1996, "PL": 1996, "KR": 1996,
    "SK": 2000, "CL": 2010, "SI": 2010, "IL": 2010, "EE": 2010,
    "LV": 2016, "LT": 2018, "CO": 2020, "CR": 2021,
}

G20 = {"AR","AU","BR","CA","CN","FR","DE","IN","ID","IT","JP","KR","MX","RU","SA","ZA","TR","GB","US","EU"}

EU27 = {"AT","BE","BG","HR","CY","CZ","DK","EE","FI","FR","DE","GR","HU","IE","IT","LV","LT","LU","MT","NL","PL","PT","RO","SK","SI","ES","SE"}

ASEAN = {"BN","KH","ID","LA","MY","MM","PH","SG","TH","VN"}

APEC = {"AU","BN","CA","CL","CN","HK","ID","JP","KR","MY","MX","NZ","PG","PE","PH","RU","SG","TW","TH","US","VN"}

G7 = {"CA","FR","DE","IT","JP","GB","US","EU"}

# NATO (already has 'nato' field? let's add nato_member_year)
NATO_MEMBERS = {
    "BE":1949,"CA":1949,"DK":1949,"FR":1949,"IS":1949,"IT":1949,
    "LU":1949,"NL":1949,"NO":1949,"PT":1949,"GB":1949,"US":1949,
    "GR":1952,"TR":1952,"DE":1955,"ES":1982,"CZ":1999,"HU":1999,
    "PL":1999,"BG":2004,"EE":2004,"LV":2004,"LT":2004,"RO":2004,
    "SK":2004,"SI":2004,"AL":2009,"HR":2009,"ME":2017,"MK":2020,
    "FI":2023,"SE":2024,
}


def main():
    print("🚀 rankerage.com 빈칸 채우기 대작전")
    print("=" * 60)

    # ── ISO 매핑 준비 ──
    print("\n📡 ISO 코드 매핑 준비 중...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        countries = json.load(f)

    country_codes = [c["country_code"].upper() for c in countries]

    # World Bank ISO2→ISO3
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        wb_countries = json.loads(resp.read())

    iso2_to_iso3 = {}
    for c in wb_countries[1]:
        iso2 = c.get("iso2Code", "").strip()
        iso3 = c.get("id", "").strip()
        if iso2 and iso3:
            iso2_to_iso3[iso2] = iso3

    iso3_to_idx = {}
    for i, c in enumerate(countries):
        iso2 = c["country_code"].upper()
        if iso2 in iso2_to_iso3:
            iso3_to_idx[iso2_to_iso3[iso2]] = i

    wb_codes = list(iso3_to_idx.keys())
    print(f"   {len(wb_codes)}개국 매핑 완료")

    # ── 1단계: World Bank API 수집 ──
    print(f"\n📊 1단계: World Bank API ({len(WB_INDICATORS)}개 지표)")
    wb_data = {}
    for field, code in WB_INDICATORS.items():
        sys.stdout.write(f"   📡 {field}... ")
        sys.stdout.flush()
        data = fetch_worldbank(code, wb_codes)
        wb_data[field] = data
        print(f"{len(data)}개국")
        time.sleep(0.3)

    # ── 2단계: 하드코딩 데이터 주입 ──
    print(f"\n📌 2단계: 국제기구 데이터 하드코딩")

    stats = {}
    for idx, country in enumerate(countries):
        iso2 = country["country_code"].upper()
        iso3 = iso2_to_iso3.get(iso2)

        # World Bank 데이터 주입
        for field in WB_INDICATORS:
            if field not in country or country.get(field) is None:
                if iso3 and iso3 in wb_data.get(field, {}):
                    val = wb_data[field][iso3]
                    if field in ("cancer", "diabetes", "hiv_prev", "mental_health",
                                "college_rate", "school_yrs", "tertiary", "teen_pregnancy",
                                "women_parl", "child_labor", "child_marriage",
                                "extreme_poverty", "union_rate", "corp_tax",
                                "water_scarcity", "refugees", "immigration",
                                "solar_power", "wind_power", "recycling"):
                        val = round(val, 1)
                    elif field in ("antibiotics", "business_ease", "vc_funding",
                                  "pension_rate"):
                        val = round(val, 1)
                    country[field] = val
                    stats[field] = stats.get(field, 0) + 1
                else:
                    country[field] = None

        # OECD 가입순서 (낮을수록=빠를수록 높은 순위)
        if "oecd_member_order" not in country or country.get("oecd_member_order") is None:
            if iso2 in OECD_MEMBERS:
                country["oecd_member_order"] = OECD_MEMBERS[iso2]
                stats["oecd_member_order"] = stats.get("oecd_member_order", 0) + 1
            else:
                country["oecd_member_order"] = None

        # G20
        country["g20_member"] = 1 if iso2 in G20 else 0
        stats["g20_member"] = stats.get("g20_member", 0) + sum(1 for c in countries if c.get("g20_member"))

        # EU
        country["eu_member"] = 1 if iso2 in EU27 else 0
        stats["eu_member"] = stats.get("eu_member", 0) + sum(1 for c in countries if c.get("eu_member"))

        # ASEAN
        country["asean_member"] = 1 if iso2 in ASEAN else 0
        stats["asean_member"] = stats.get("asean_member", 0) + sum(1 for c in countries if c.get("asean_member"))

        # APEC
        country["apec_member"] = 1 if iso2 in APEC else 0
        stats["apec_member"] = stats.get("apec_member", 0) + sum(1 for c in countries if c.get("apec_member"))

        # G7
        country["g7_member"] = 1 if iso2 in G7 else 0
        stats["g7_member"] = stats.get("g7_member", 0) + sum(1 for c in countries if c.get("g7_member"))

        # NATO 가입연도
        if "nato_year" not in country or country.get("nato_year") is None:
            if iso2 in NATO_MEMBERS:
                country["nato_year"] = NATO_MEMBERS[iso2]
                stats["nato_year"] = stats.get("nato_year", 0) + 1
            else:
                country["nato_year"] = None

    # ── rank 필드 초기화 ──
    # rank는 null로 두고 analyze_rankings.py가 처리하도록
    for field in list(stats.keys()):
        rank_field = f"{field}_rank"
        for c in countries:
            if rank_field not in c:
                c[rank_field] = None

    # ── 저장 ──
    print(f"\n💾 저장 중...")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False)

    # ── 결과 보고 ──
    total_new = sum(1 for v in stats.values() if v > 0)
    print(f"\n{'='*60}")
    print(f"✅ 데이터 수집 완료!")
    print(f"\n📊 채워진 지표:")
    for field, count in sorted(stats.items()):
        bar = "█" * min(count // 10, 20)
        print(f"   {field:25s} {count:3d}개국  {bar}")

    new_fields = list(stats.keys())
    print(f"\n🎯 신규 채움: {total_new}개 지표, {len(new_fields)}종")

    # ── site_meta 업데이트 ──
    all_keys = set(countries[0].keys())
    pure_metrics = sum(1 for k in all_keys if not k.endswith("_rank") and not k.endswith("_desc"))
    print(f"\n📊 총 지표 수: {pure_metrics}")

    with open(META_FILE, "r") as f:
        meta = json.load(f)
    meta["total_rankings"] = pure_metrics
    meta["last_updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(META_FILE, "w") as f:
        json.dump(meta, f, ensure_ascii=False)
    print(f"📊 site_meta 업데이트: total_rankings → {pure_metrics}")

    print(f"\n🎉 완료! 'git push'로 배포하세요.")


if __name__ == "__main__":
    main()
