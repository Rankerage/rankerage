#!/usr/bin/env python3
"""update_elections.py — Wikipedia + IFES에서 전 세계 선거 데이터 수집

데이터 소스:
- Wikipedia: List of next general elections (197개국 커버)
- IFES Election Guide (실시간 임박 선거 보강)
"""
import json, re, sys, urllib.request
from datetime import datetime, date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_FILE = REPO / "docs" / "data" / "countries.json"
WP_API = "https://en.wikipedia.org/w/api.php?action=parse&page=List_of_next_general_elections&prop=wikitext&format=json"
IFES_URL = "https://www.electionguide.org/elections/"

# ISO 3166-1 alpha-2 매핑 (Wikipedia 국가명 → 코드)
NAME_TO_CODE = {
    'Algeria':'DZ','Angola':'AO','Benin':'BJ','Botswana':'BW','Burkina Faso':'BF','Burundi':'BI',
    'Cameroon':'CM','Cape Verde':'CV','Central African Republic':'CF','Chad':'TD','Comoros':'KM',
    'DR Congo':'CD','Democratic Republic of the Congo':'CD','Republic of the Congo':'CG','Congo':'CG',
    'Djibouti':'DJ','Egypt':'EG','Equatorial Guinea':'GQ','Eritrea':'ER','Ethiopia':'ET',
    'Gabon':'GA','Gambia':'GM','Ghana':'GH','Guinea':'GN','Guinea-Bissau':'GW',
    'Ivory Coast':'CI','Côte d\'Ivoire':'CI','Kenya':'KE','Lesotho':'LS','Liberia':'LR',
    'Libya':'LY','Madagascar':'MG','Malawi':'MW','Mali':'ML','Mauritania':'MR','Mauritius':'MU',
    'Morocco':'MA','Mozambique':'MZ','Namibia':'NA','Niger':'NE','Nigeria':'NG',
    'Rwanda':'RW','São Tomé and Príncipe':'ST','Sao Tome and Principe':'ST','Senegal':'SN',
    'Seychelles':'SC','Sierra Leone':'SL','Somalia':'SO','South Africa':'ZA','South Sudan':'SS',
    'Sudan':'SD','Tanzania':'TZ','Togo':'TG','Tunisia':'TN','Uganda':'UG','Zambia':'ZM','Zimbabwe':'ZW',
    'Eswatini':'SZ','Swaziland':'SZ',
    # Americas
    'Argentina':'AR','Bolivia':'BO','Brazil':'BR','Canada':'CA','Chile':'CL','Colombia':'CO',
    'Costa Rica':'CR','Cuba':'CU','Dominican Republic':'DO','Ecuador':'EC','El Salvador':'SV',
    'Guatemala':'GT','Haiti':'HT','Honduras':'HN','Jamaica':'JM','Mexico':'MX','Nicaragua':'NI',
    'Panama':'PA','Paraguay':'PY','Peru':'PE','United States':'US','Uruguay':'UY','Venezuela':'VE',
    'Bahamas':'BS','Barbados':'BB','Belize':'BZ','Guyana':'GY','Suriname':'SR','Trinidad and Tobago':'TT',
    # Asia
    'Afghanistan':'AF','Armenia':'AM','Azerbaijan':'AZ','Bahrain':'BH','Bangladesh':'BD','Bhutan':'BT',
    'Brunei':'BN','Cambodia':'KH','China':'CN','Georgia':'GE','India':'IN','Indonesia':'ID',
    'Iran':'IR','Iraq':'IQ','Israel':'IL','Japan':'JP','Jordan':'JO','Kazakhstan':'KZ','Kuwait':'KW',
    'Kyrgyzstan':'KG','Laos':'LA','Lebanon':'LB','Malaysia':'MY','Maldives':'MV','Mongolia':'MN',
    'Myanmar':'MM','Nepal':'NP','North Korea':'KP','Oman':'OM','Pakistan':'PK','Philippines':'PH',
    'Qatar':'QA','Saudi Arabia':'SA','Singapore':'SG','South Korea':'KR','Korea':'KR',
    'Sri Lanka':'LK','Syria':'SY','Taiwan':'TW','Tajikistan':'TJ','Thailand':'TH','Timor-Leste':'TL',
    'East Timor':'TL','Turkey':'TR','Turkmenistan':'TM','United Arab Emirates':'AE','UAE':'AE',
    'Uzbekistan':'UZ','Vietnam':'VN','Yemen':'YE',
    # Europe
    'Albania':'AL','Andorra':'AD','Austria':'AT','Belarus':'BY','Belgium':'BE',
    'Bosnia and Herzegovina':'BA','Bosnia':'BA','Bulgaria':'BG','Croatia':'HR','Cyprus':'CY',
    'Czech Republic':'CZ','Czechia':'CZ','Denmark':'DK','Estonia':'EE','Finland':'FI','France':'FR',
    'Germany':'DE','Greece':'GR','Hungary':'HU','Iceland':'IS','Ireland':'IE','Italy':'IT',
    'Kosovo':'XK','Latvia':'LV','Liechtenstein':'LI','Lithuania':'LT','Luxembourg':'LU',
    'Malta':'MT','Moldova':'MD','Monaco':'MC','Montenegro':'ME','Netherlands':'NL',
    'North Macedonia':'MK','Macedonia':'MK','Norway':'NO','Poland':'PL','Portugal':'PT',
    'Romania':'RO','Russia':'RU','Russian Federation':'RU','San Marino':'SM','Serbia':'RS',
    'Slovakia':'SK','Slovenia':'SI','Spain':'ES','Sweden':'SE','Switzerland':'CH',
    'Ukraine':'UA','United Kingdom':'GB','UK':'GB','Vatican City':'VA',
    # Oceania
    'Australia':'AU','Fiji':'FJ','Kiribati':'KI','Marshall Islands':'MH','Micronesia':'FM',
    'Nauru':'NR','New Zealand':'NZ','Palau':'PW','Papua New Guinea':'PG','Samoa':'WS',
    'Solomon Islands':'SB','Tonga':'TO','Tuvalu':'TV','Vanuatu':'VU',
}

def parse_wikipedia():
    """Wikipedia List of next general elections 파싱"""
    req = urllib.request.Request(WP_API, headers={'User-Agent': 'RankerageBot/1.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    
    text = data.get('parse',{}).get('wikitext',{}).get('*','')
    
    # Flag|Country 행에서 국가와 날짜 추출
    results = {}
    current_country = None
    
    for line in text.split('\n'):
        fm = re.match(r'\|\{\{Flag\|([^}|]+)', line)
        if not fm:
            fm = re.match(r'\|\{\{[Ff]lagicon\|[^}]+\}\}\s*\[\[([^\]]+)\]\]', line)
        if fm:
            current_country = fm.group(1).strip()
            if current_country not in results:
                results[current_country] = {'dates': [], 'titles': []}
            continue
        
        if current_country and line.startswith('|') and 'dts|' in line:
            dm = re.findall(r'\{\{dts\|([0-9]+ [A-Z][a-z]+ 20[0-9]+)\}\}', line)
            if dm:
                results[current_country]['dates'].extend(dm)
            # 선거 링크 (제목)
            links = re.findall(r'\[\[([^\]|]+)\]\]', line)
            if links:
                results[current_country]['titles'].extend(links)
    
    return results

def parse_date(d):
    """날짜 문자열 → date 객체"""
    for fmt in ['%d %b %Y', '%d %B %Y', '%b %Y', '%B %Y', '%Y']:
        try:
            return datetime.strptime(d, fmt).date()
        except:
            continue
    return None

def main():
    print("Wikipedia 선거 데이터 수집 중...")
    wp = parse_wikipedia()
    print(f"Wikipedia 국가: {len(wp)}개국")
    
    # countries.json 로드
    with open(DATA_FILE) as f:
        countries = json.load(f)
    
    code_idx = {}
    for i, c in enumerate(countries):
        code = (c.get('country_code') or '').upper()
        if len(code) == 2:
            code_idx[code] = i
    
    # 국가명 → 코드 매핑 추가
    name_idx = {}
    for i, c in enumerate(countries):
        name = c.get('country_name_en','').strip()
        name_idx[name.lower()] = i
    
    today = date.today()
    updated = 0
    
    for wp_name, wp_data in wp.items():
        code = NAME_TO_CODE.get(wp_name)
        idx = None
        
        if code and code in code_idx:
            idx = code_idx[code]
        elif wp_name.lower() in name_idx:
            idx = name_idx[wp_name.lower()]
        
        if idx is None:
            continue
        
        c = countries[idx]
        
        # 가장 가까운 미래 날짜 찾기
        future_dates = []
        for d in wp_data['dates']:
            dt = parse_date(d)
            if dt:
                future_dates.append(dt)
        
        if not future_dates:
            # 미래 없으면 가장 최근 과거
            for d in wp_data['dates']:
                dt = parse_date(d)
                if dt:
                    future_dates.append(dt)
        
        if future_dates:
            closest = min(future_dates, key=lambda x: abs((x - today).days))
            c['election_date'] = closest.strftime('%Y-%m-%d')
            c['election_days'] = abs((closest - today).days)
            # 선거 제목
            titles = [t for t in wp_data['titles'] if 'election' in t.lower() or 'presidential' in t.lower() or 'parliamentary' in t.lower()]
            if titles:
                c['election_title'] = titles[0].replace('_',' ')
            updated += 1
    
    # IFES 실시간 데이터로 최신화 (임박 선거 우선)
    print("IFES 실시간 데이터 보강 중...")
    try:
        req = urllib.request.Request(IFES_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        url_map = {}
        for i, line in enumerate(html.split('\n')):
            m = re.search(r'thisurl\s*=\s*"/countries/id/"\s*\+\s*(\d+)', line)
            if m:
                url_map[i] = '/countries/id/' + m.group(1)
        
        for m in re.finditer(r'mapJson\.push\(\{([^}]+)\}\)', html):
            block = m.group(1)
            fields = {}
            for f in ['id','electionname','electiondate','institution']:
                fm = re.search(r'"'+f+r'":\s*"([^"]+)"', block)
                if fm: fields[f] = fm.group(1)
            if fields.get('id') and fields.get('electiondate'):
                code = fields['id'].upper()
                if code in code_idx:
                    idx = code_idx[code]
                    edate = datetime.strptime(fields['electiondate'], '%Y-%m-%d').date()
                    countries[idx]['election_date'] = fields['electiondate']
                    countries[idx]['election_days'] = abs((edate - today).days)
                    countries[idx]['election_title'] = fields.get('institution','') or fields.get('electionname','')
                    updated += 1
    except Exception as e:
        print(f"  ⚠ IFES 실패: {e}")
    
    # 최종 순위 재계산
    ranked = sorted(
        [(i, c.get('election_days', 99999)) for i, c in enumerate(countries) if c.get('election_date')],
        key=lambda x: x[1]
    )
    for rank, (idx, _) in enumerate(ranked, 1):
        countries[idx]['election_rank'] = rank
    
    with open(DATA_FILE, 'w') as f:
        json.dump(countries, f, ensure_ascii=False, indent=2)
    
    print(f"\n총 {len(ranked)}개국 선거 데이터 (Wikipedia + IFES)")

if __name__ == '__main__':
    main()
