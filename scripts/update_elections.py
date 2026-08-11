#!/usr/bin/env python3
"""update_elections.py — IFES Election Guide에서 선거 데이터 수집하여 countries.json 갱신

데이터 소스: https://www.electionguide.org/elections/
추출: mapJson (페이지 내 script 태그)
갱신 필드: election_date, election_title, election_days (절대값), election_url
"""
import json, re, sys, urllib.request
from datetime import datetime, date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "docs" / "data" / "countries.json"
IFES_URL = "https://www.electionguide.org/elections/"

def fetch_elections():
    """IFES elections 페이지에서 mapJson 데이터 추출"""
    req = urllib.request.Request(IFES_URL, headers={
        'User-Agent': 'Mozilla/5.0 (compatible; Rankerage/1.0; +https://rankerage.com)'
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
    
    # mapJson.push({...}) 패턴에서 JSON 추출
    entries = []
    # 먼저 thisurl 변수들을 추출 (라인 번호 기준)
    url_map = {}
    lines = html.split('\n')
    for i, line in enumerate(lines):
        m = re.search(r'thisurl\s*=\s*"/countries/id/"\s*\+\s*(\d+)', line)
        if m:
            url_map[i] = '/countries/id/' + m.group(1)
    
    for m in re.finditer(r'mapJson\.push\(\{([^}]+)\}\)', html):
        block = m.group(1)
        fields = {}
        for f in ['id', 'electionname', 'electiondate', 'institution', 'electionstatus']:
            fm = re.search(r'"' + f + r'":\s*"([^"]+)"', block)
            if fm:
                fields[f] = fm.group(1)
        # url은 thisurl 변수 참조 → 가장 가까운 thisurl 찾기
        block_start_line = html[:m.start()].count('\n')
        for line_num in sorted(url_map.keys(), reverse=True):
            if line_num <= block_start_line:
                fields['url'] = url_map[line_num]
                break
        if fields.get('id') and fields.get('electiondate'):
            entries.append(fields)
    
    # 중복 제거 (같은 국가+날짜+institution 조합)
    seen = set()
    unique = []
    for e in entries:
        key = (e['id'], e['electiondate'], e.get('institution', ''))
        if key not in seen:
            seen.add(key)
            unique.append(e)
    
    return unique

def main():
    print("IFES Election Guide 데이터 수집 중...")
    elections = fetch_elections()
    print(f"수집된 선거: {len(elections)}개")
    
    if not elections:
        print("⚠ 수집된 데이터 없음")
        return 1
    
    # 국가 데이터 로드
    with open(DATA_FILE) as f:
        countries = json.load(f)
    
    # country_code → index 매핑
    code_idx = {}
    for i, c in enumerate(countries):
        code = (c.get('country_code') or '').upper()
        if len(code) == 2:  # 실제 국가 코드만 (XX 접두어 제외)
            code_idx[code] = i
    
    today = date.today()
    updated = 0
    
    for e in elections:
        code = e['id'].upper()
        if code not in code_idx:
            continue
        
        idx = code_idx[code]
        c = countries[idx]
        
        try:
            edate = datetime.strptime(e['electiondate'], '%Y-%m-%d').date()
            days = (edate - today).days
        except:
            continue
        
        c['election_date'] = e['electiondate']
        c['election_title'] = e.get('institution', '') or e.get('electionname', '')
        c['election_days'] = abs(days)  # 절대값 (과거/미래 구분 없이 근접도)
        c['election_url'] = f"https://www.electionguide.org{e['url']}"
        updated += 1
        print(f"  {code} {e['electionname']}: {e['electiondate']} ({'+'if days>=0 else ''}{days}d) — {e.get('institution','')}")
    
    # 순위 재계산 (election_days asc → 작을수록 임박)
    # ── 모든 국가의 election_days를 오늘 기준으로 재계산 (절대값) ──
    recalc = 0
    for c in countries:
        dt = c.get('election_date')
        if dt:
            try:
                edate = datetime.strptime(dt, '%Y-%m-%d').date()
                c['election_days'] = abs((edate - today).days)
                recalc += 1
            except:
                pass
    
    ranked = sorted(
        [(i, c.get('election_days', 99999)) for i, c in enumerate(countries) if c.get('election_date')],
        key=lambda x: x[1]
    )
    for rank, (idx, _) in enumerate(ranked, 1):
        countries[idx]['election_rank'] = rank
    
    # 저장
    with open(DATA_FILE, 'w') as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)
    
    print(f"\n업데이트: {updated}개국 (전체 {len(ranked)}개국 선거 데이터)")
    return 0

if __name__ == '__main__':
    sys.exit(main())
