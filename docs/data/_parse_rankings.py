import json

with open(r'C:\Users\mathe\Desktop\rankerage\docs\data\countries.json', encoding='utf-8') as f:
    data = json.load(f)

# Available rankings with their keys and labels
rankings = {
    'gdp': ('GDP (백만$)', 'gdp'),
    'gdp_per_capita': ('1인당 GDP ($)', 'gdp_per_capita'),
    'happiness': ('행복지수', 'happiness'),
    'hdi': ('인간개발지수', 'hdi'),
    'life_expectancy': ('기대수명 (년)', 'life_expectancy'),
    'fifa_ranking': ('FIFA 랭킹', 'fifa_ranking'),
    'cpi': ('부패인식지수', 'cpi'),
    'internet_pct': ('인터넷 보급률 (%)', 'internet_pct'),
    'population': ('인구', 'population'),
    'area': ('면적 (km²)', 'area'),
    'population_density': ('인구밀도 (명/km²)', 'population_density'),
    'co2': ('1인당 CO₂ 배출량 (톤)', 'co2'),
    'military_pct': ('군사비 GDP 대비 (%)', 'military_pct'),
    'forest': ('산림覆盖率 (%)', 'forest'),
    'tourism': ('관광객 (백만)', 'tourism'),
    'fertility': ('출산율', 'fertility'),
    'cricket': ('크리켓 랭킹', 'cricket'),
}

# Pick FIFA ranking for interesting post
key = 'fifa_ranking'
label, field = rankings[key]

# Sort: lower FIFA rank = better (1 is best)
is_reverse = False  # fifa_ranking: lower is better
sorted_data = sorted([c for c in data if c.get(field) is not None and c.get(field) != 0], key=lambda x: x[field], reverse=is_reverse)

top3 = sorted_data[:3]
print("=== TOP 3 ===")
for c in top3:
    print(f"{c['flag']} {c['country_name_en']} ({c['country_name_local']}) — {c[field]}위")

# Find a surprise fact
# E.g., which small country ranks high
print("\n=== SURPRISE ===")
# Look for interesting anomaly
# Let's find countries that are unusually high/low
# E.g., Indonesia in FIFA top 100? Or which populous country is lowest?
print(f"총 {len([c for c in data if c.get(field)])}개국 FIFA 랭킹 보유")
print(f"1위: {sorted_data[0]['flag']} {sorted_data[0]['country_name_en']} ({sorted_data[0][field]}위)")
print(f"꼴찌: {sorted_data[-1]['flag']} {sorted_data[-1]['country_name_en']} ({sorted_data[-1][field]}위)")

# Find a surprising fact: Asian country with highest FIFA rank? Or small country punching above weight
highest_asia = sorted([c for c in data if c.get('continent') == 'Asia' and c.get(field) and c.get(field) != 0], key=lambda x: x[field], reverse=is_reverse)
print(f"\n아시아 최고: {highest_asia[0]['flag']} {highest_asia[0]['country_name_en']} ({highest_asia[0][field]}위)")

# African top
highest_africa = sorted([c for c in data if c.get('continent') == 'Africa' and c.get(field) and c.get(field) != 0], key=lambda x: x[field], reverse=is_reverse)
print(f"아프리카 최고: {highest_africa[0]['flag']} {highest_africa[0]['country_name_en']} ({highest_africa[0][field]}위)")

# Smallest country in top 50
small_top50 = sorted([c for c in data if c.get(field) and c.get(field) <= 50 and c.get(field) != 0], key=lambda x: x.get('area', 9999999))
print(f"TOP50 중 최소국: {small_top50[0]['flag']} {small_top50[0]['country_name_en']} (면적 {small_top50[0].get('area', '?')}km², {small_top50[0][field]}위)")

# Population fact
print("\n=== POPULATION FACT ===")
pop_top = sorted([c for c in data if c.get(field) and c.get(field) != 0], key=lambda x: x.get('population', 0), reverse=True)
for c in pop_top[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: 인구 {c.get('population', 0):,}명, FIFA {c.get(field)}위")