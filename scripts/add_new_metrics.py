#!/usr/bin/env python3
"""
add_new_metrics.py — rankerage.com  신규 21개 지표 추가
World Bank API에서 데이터 수집 → countries.json 병합
"""

import json, time, urllib.request, sys, os
from collections import defaultdict

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
DATA_FILE = f"{REPO}/docs/data/countries.json"

# ── World Bank 지표 코드 ──
INDICATORS = {
    # 👴 노인 지표
    "elderly_population_pct":  "SP.POP.65UP.TO.ZS",    # 65세+ 인구 비율
    "old_age_dependency":      "SP.POP.DPND.OL",        # 노년부양비
    "healthy_life_exp_60":     "SH.HLE.60UP",           # 60세 건강수명 (WHO 데이터)
    "suicide_rate":            "SH.STA.SUIC.P5",         # 자살률 (인구 10만명당)
    
    # 👫 남녀 지표
    "female_labor_participation": "SL.TLF.CACT.FE.ZS",  # 여성 경제활동 참가율
    "women_in_parliament":        "SG.GEN.PARL.ZS",     # 여성 국회의원 비율
    "teen_pregnancy":             "SP.ADO.TFRT",         # 10대 출산율 (여성 1000명당)
    "female_life_expectancy":     "SP.DYN.LE00.FE.IN",   # 여성 기대수명
    "male_life_expectancy":       "SP.DYN.LE00.MA.IN",   # 남성 기대수명
}

# ── 배치 크기 (World Bank API 한 번에 60개국까지) ──
BATCH_SIZE = 50

def fetch_indicator(indicator_code, country_codes):
    """World Bank API에서 지표 데이터 가져오기"""
    all_data = {}
    
    for i in range(0, len(country_codes), BATCH_SIZE):
        batch = country_codes[i:i+BATCH_SIZE]
        codes_str = ";".join(batch)
        url = (
            f"https://api.worldbank.org/v2/country/{codes_str}"
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
                        value = entry["value"]
                        
                        # 가장 최근 데이터만 사용
                        if iso3 not in all_data or year > all_data[iso3][0]:
                            all_data[iso3] = (year, value)
            
            time.sleep(0.3)  # API rate limit
        except Exception as e:
            print(f"  ⚠️ {indicator_code} 배치 실패: {e}", file=sys.stderr)
    
    return {k: v[1] for k, v in all_data.items()}  # {iso3: value}

def main():
    print("📦 rankerage.com 신규 지표 추가기")
    print("="*50)
    
    # 1. 기존 데이터 로드
    print("\n1️⃣ countries.json 로드 중...")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        countries = json.load(f)
    print(f"   {len(countries)}개 국가 로드 완료")
    
    # 2. ISO 코드 매핑
    print("\n2️⃣ 국가 코드 매핑...")
    country_codes = [c["country_code"].upper() for c in countries]
    print(f"   {len(country_codes)}개 코드: {', '.join(country_codes[:5])}...")
    
    # World Bank는 ISO3 코드를 사용하므로 매핑 필요
    # 먼저 ISO2→ISO3 매핑 가져오기
    print("\n3️⃣ World Bank ISO 코드 매핑 중...")
    url = "https://api.worldbank.org/v2/country?format=json&per_page=300"
    req = urllib.request.Request(url, headers={"User-Agent": "Rankerage/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        wb_countries = json.loads(resp.read())
    
    iso2_to_iso3 = {}
    for c in wb_countries[1]:
        iso2 = c.get("iso2Code", "").strip()
        iso3 = c.get("id", "").strip()
        if iso2 and iso3 and iso3 != "NAM":
            iso2_to_iso3[iso2] = iso3
    
    # ISO3 → JSON 인덱스 매핑
    iso3_to_idx = {}
    for i, c in enumerate(countries):
        iso2 = c["country_code"].upper()
        if iso2 in iso2_to_iso3:
            iso3_to_idx[iso2_to_iso3[iso2]] = i
    
    wb_codes = list(iso3_to_idx.keys())
    print(f"   {len(wb_codes)}개국 World Bank 매핑 완료")
    
    # 4. 각 지표 수집
    print("\n4️⃣ World Bank 데이터 수집 시작...")
    collected = {}
    for field, code in INDICATORS.items():
        print(f"   📡 {field} ({code})...")
        data = fetch_indicator(code, wb_codes)
        collected[field] = data
        count = len(data)
        print(f"      → {count}개국 데이터 수집 완료")
    
    # 5. 데이터 병합
    print(f"\n5️⃣ countries.json에 데이터 병합 중...")
    new_field_count = 0
    stats = defaultdict(int)
    
    for i, country in enumerate(countries):
        iso2 = country["country_code"].upper()
        iso3 = iso2_to_iso3.get(iso2)
        
        for field in INDICATORS:
            # rank 필드도 함께 추가
            rank_field = f"{field}_rank"
            
            if iso3 and iso3 in collected.get(field, {}):
                value = collected[field][iso3]
                
                # 특별 처리
                if field == "suicide_rate":
                    value = round(value, 1)
                elif field == "teen_pregnancy":
                    value = round(value, 1)
                elif field in ("elderly_population_pct", "old_age_dependency",
                              "female_labor_participation", "women_in_parliament"):
                    value = round(value, 1)
                elif field in ("female_life_expectancy", "male_life_expectancy",
                              "healthy_life_exp_60"):
                    value = round(value, 1)
                
                country[field] = value
                stats[field] += 1
            else:
                country[field] = None
            
            # rank는 None으로 초기화 (rank 계산은 analyze_rankings.py에서)
            country[rank_field] = None
        
        # 계산 필드
        # 남녀 수명 격차
        if country.get("female_life_expectancy") and country.get("male_life_expectancy"):
            country["life_exp_gender_gap"] = round(
                country["female_life_expectancy"] - country["male_life_expectancy"], 1
            )
        else:
            country["life_exp_gender_gap"] = None
        country["life_exp_gender_gap_rank"] = None
        
        # 노인 자살률은 일반 자살률을 대리로 사용 (연령별 데이터는 별도 수집 필요)
        country["elderly_suicide"] = country.get("suicide_rate")
        country["elderly_suicide_rank"] = None
    
    # 6. 저장
    print(f"\n6️⃣ 저장 중...")
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(countries, f, ensure_ascii=False)
    
    # 7. 결과 보고
    print("\n" + "="*50)
    print("✅ 데이터 수집 완료!")
    print(f"\n📊 수집 통계:")
    for field, count in sorted(stats.items()):
        pct = count / len(countries) * 100
        bar = "█" * int(pct / 5) + "░" * (20 - int(pct / 5))
        print(f"   {field:35s} {count:3d}개국 ({pct:5.1f}%) {bar}")
    
    # 신규 필드 목록 출력 (table.js 수정용)
    new_fields = list(INDICATORS.keys()) + ["life_exp_gender_gap", "elderly_suicide"]
    print(f"\n📝 신규 필드 {len(new_fields)}개:")
    for f in new_fields:
        print(f"   {f}")
    
    print(f"\n🔢 총 필드 수: {len(countries[0])}개")
    
    # site_meta 업데이트
    meta_file = f"{REPO}/docs/data/site_meta.json"
    with open(meta_file, "r") as f:
        meta = json.load(f)
    meta["total_rankings"] = 257 + len(new_fields)
    meta["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(meta_file, "w") as f:
        json.dump(meta, f, ensure_ascii=False)
    print(f"\n📊 site_meta 업데이트: total_rankings → {meta['total_rankings']}")

if __name__ == "__main__":
    main()
