import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# HAPPINESS
print('=== HAPPINESS (Top 5) ===')
sorted_h = sorted(data, key=lambda x: (x.get('happiness') or 0), reverse=True)
for c in sorted_h[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: happiness={c.get('happiness')} (rank={c.get('happiness_rank')})")

print()
print('=== GDP per capita (Top 5) ===')
sorted_g = sorted(data, key=lambda x: (x.get('gdp_per_capita') or 0), reverse=True)
for c in sorted_g[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: gdp_pc={c.get('gdp_per_capita')} (rank={c.get('gdp_per_capita_rank')})")

print()
print('=== FIFA Ranking (Top 5) ===')
sorted_f = sorted(data, key=lambda x: (x.get('fifa_ranking') or 9999))
for c in sorted_f[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: fifa={c.get('fifa_ranking')}")

print()
print('=== Life Expectancy (Top 5) ===')
sorted_l = sorted(data, key=lambda x: (x.get('life_expectancy') or 0), reverse=True)
for c in sorted_l[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: life={c.get('life_expectancy')} (rank={c.get('life_expectancy_rank')})")

print()
print('=== Internet % (Top 5) ===')
sorted_i = sorted(data, key=lambda x: (x.get('internet_pct') or 0), reverse=True)
for c in sorted_i[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: internet={c.get('internet_pct')}% (rank={c.get('internet_pct_rank')})")

print()
print('=== CPI / Corruption (best=low corruption) (Top 5) ===')
sorted_c = sorted(data, key=lambda x: (x.get('cpi') or 0), reverse=True)
for c in sorted_c[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: cpi={c.get('cpi')} (rank={c.get('cpi_rank')})")

print()
print('=== GPI / Peace Index (most peaceful, lowest score) (Top 5) ===')
sorted_p = sorted(data, key=lambda x: (x.get('gpi') or 999))
for c in sorted_p[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: gpi={c.get('gpi')} (rank={c.get('gpi_rank')})")

print()
print('=== Nobel Prizes (Top 5) ===')
sorted_n = sorted(data, key=lambda x: (x.get('nobel') or 0), reverse=True)
for c in sorted_n[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: nobel={c.get('nobel')}")

print()
print('=== Tourism (Top 5) ===')
sorted_t = sorted(data, key=lambda x: (x.get('tourism') or 0), reverse=True)
for c in sorted_t[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: tourism={c.get('tourism')} (rank={c.get('tourism_rank')})")

print()
print('=== Olympic Medals (Top 5) ===')
sorted_o = sorted(data, key=lambda x: (x.get('olympic') or 0), reverse=True)
for c in sorted_o[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: olympic={c.get('olympic')}")

print()
print('=== Democracy Index (Top 5) ===')
sorted_d = sorted(data, key=lambda x: (x.get('democracy') or 0), reverse=True)
for c in sorted_d[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: democracy={c.get('democracy')} (rank={c.get('democracy_rank')})")

print()
print('=== Literacy (Top 5) ===')
sorted_lit = sorted(data, key=lambda x: (x.get('literacy') or 0), reverse=True)
for c in sorted_lit[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: literacy={c.get('literacy')}%")

print()
print('=== Forest % (Top 5) ===')
sorted_for = sorted(data, key=lambda x: (x.get('forest') or 0), reverse=True)
for c in sorted_for[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: forest={c.get('forest')}% (rank={c.get('forest_rank')})")

print()
print('=== Alcohol (Top 5) ===')
sorted_al = sorted(data, key=lambda x: (x.get('alcohol') or 0), reverse=True)
for c in sorted_al[:5]:
    print(f"  {c['flag']} {c['country_name_en']}: alcohol={c.get('alcohol')}")
