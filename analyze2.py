import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Filter: only real countries (have country_code like 'af', 'kr', etc. - not XX-prefixed)
real_countries = [c for c in data if c.get('country_code') and not c.get('country_code', '').startswith('XX')]

print(f"Total entries: {len(data)}, Real countries: {len(real_countries)}")

# Alcohol consumption
print('\n=== ALCOHOL (Top 10, real countries) ===')
sorted_al = sorted(real_countries, key=lambda x: (x.get('alcohol') or 0), reverse=True)
for c in sorted_al[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: alcohol={c.get('alcohol')}L")

# Forest %
print('\n=== FOREST % (Top 10, real countries) ===')
sorted_for = sorted(real_countries, key=lambda x: (x.get('forest') or 0), reverse=True)
for c in sorted_for[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: forest={c.get('forest')}% (rank={c.get('forest_rank')})")

# Happiness  
print('\n=== HAPPINESS (Top 10, real countries) ===')
sorted_h = sorted(real_countries, key=lambda x: (x.get('happiness') or 0), reverse=True)
for c in sorted_h[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: happiness={c.get('happiness')} (rank={c.get('happiness_rank')})")

# CPI
print('\n=== CPI (Top 10, real countries) ===')
sorted_c = sorted(real_countries, key=lambda x: (x.get('cpi') or 0), reverse=True)
for c in sorted_c[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: cpi={c.get('cpi')} (rank={c.get('cpi_rank')})")

# GDP per capita
print('\n=== GDP per capita (Top 10, real countries) ===')
sorted_g = sorted(real_countries, key=lambda x: (x.get('gdp_per_capita') or 0), reverse=True)
for c in sorted_g[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: gdp_pc=${c.get('gdp_per_capita'):,} (rank={c.get('gdp_per_capita_rank')})")

# Democracy
print('\n=== DEMOCRACY (Top 10, real countries) ===')
sorted_d = sorted(real_countries, key=lambda x: (x.get('democracy') or 0), reverse=True)
for c in sorted_d[:10]:
    print(f"  {c['flag']} {c['country_name_en']}: democracy={c.get('democracy')} (rank={c.get('democracy_rank')})")

# Check South Korea in happiness
print('\n=== SOUTH KOREA ===')
for c in real_countries:
    if c.get('country_name_en') == 'South Korea':
        print(f"  {c['flag']} Happiness rank: {c.get('happiness_rank')}, score: {c.get('happiness')}")
        print(f"  GDP per capita: ${c.get('gdp_per_capita'):,}, rank: {c.get('gdp_per_capita_rank')}")
        print(f"  Forest: {c.get('forest')}%, rank: {c.get('forest_rank')}")
        print(f"  Alcohol: {c.get('alcohol')}L")
        print(f"  CPI: {c.get('cpi')}, rank: {c.get('cpi_rank')}")
        print(f"  Internet: {c.get('internet_pct')}%")
        print(f"  FIFA: {c.get('fifa_ranking')}")
