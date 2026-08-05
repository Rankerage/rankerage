import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

print(f'Total countries: {len(countries)}')
print()

# Check interesting ranking fields for data coverage
rank_fields = [
    ('happiness', 'happiness_rank', '행복도'),
    ('gdp_per_capita', 'gdp_per_capita_rank', '1인당 GDP'),
    ('fifa_ranking', 'fifa_ranking_rank', 'FIFA 랭킹'),
    ('hdi', 'hdi_rank', '인간개발지수(HDI)'),
    ('life_expectancy', 'life_expectancy_rank', '기대수명'),
    ('coffee', None, '커피소비량'),
    ('internet_pct', 'internet_pct_rank', '인터넷 보급률'),
    ('cpi', 'cpi_rank', '부패인식지수'),
    ('gpi', 'gpi_rank', '평화지수'),
    ('fertility', 'fertility_rank', '출산율'),
    ('military_pct', 'military_pct_rank', 'GDP 대비 국방비'),
    ('obesity', None, '비만율'),
    ('alcohol', None, '알코올 소비량'),
    ('tourism', 'tourism_rank', '관광'),
    ('edu', 'edu_rank', '교육지수'),
    ('democracy', 'democracy_rank', '민주주의 지수'),
    ('press', 'press_rank', '언론자유지수'),
    ('murder', 'murder_rank', '살인율'),
    ('co2', 'co2_rank', 'CO2 배출량'),
    ('renew', 'renew_rank', '재생에너지 비율'),
    ('forest', 'forest_rank', '산림비율'),
    ('literacy', 'literacy_rank', '문해율'),
    ('suicide', None, '자살률'),
    ('smoking', None, '흡연율'),
    ('beer', None, '맥주 소비량'),
    ('wine', None, '와인 소비량'),
    ('chocolate', None, '초콜릿 소비량'),
    ('meat', None, '육류 소비량'),
    ('chess', None, '체스'),
    ('nobel_per_capita', None, '1인당 노벨상'),
    ('books', None, '독서량'),
    ('earthquakes', 'earthquakes_rank', '지진'),
    ('volcanoes', None, '화산'),
    ('nuclear_power', None, '원자력'),
    ('independence', 'independence_rank', '독립기념일까지 남은 일수'),
    ('emigration', 'emigration_rank', '이민율'),
    ('slavery', 'slavery_rank', '현대판 노예제'),
    ('median_age', 'median_age_rank', '중위연령'),
]

for field, rank_field, label in rank_fields:
    non_null = sum(1 for c in countries if c.get(field) is not None)
    non_null_rank = sum(1 for c in countries if c.get(rank_field) is not None) if rank_field else 0
    pct = round(non_null / len(countries) * 100, 1)
    rpct = round(non_null_rank / len(countries) * 100, 1)
    if pct > 0:
        print(f'{label} ({field}): value={non_null}/{len(countries)} ({pct}%), rank={non_null_rank} ({rpct}%)')
