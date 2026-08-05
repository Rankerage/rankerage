import json

with open('countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

def top(rank_key, val_key=None, n=5):
    items = [c for c in countries if c.get(rank_key)]
    items.sort(key=lambda x: x[rank_key])
    print(f'\n=== {rank_key.upper()} (top {n}) ===')
    for c in items[:n]:
        val = f" ({c[val_key]})" if val_key and c.get(val_key) else ""
        print(f"  #{c[rank_key]} {c['flag']} {c['country_name_en']}{val}")

def top_val(val_key, n=5):
    items = [c for c in countries if c.get(val_key)]
    items.sort(key=lambda x: x[val_key], reverse=True)
    print(f'\n=== {val_key.upper()} (top {n}) ===')
    for c in items[:n]:
        print(f"  {c['flag']} {c['country_name_en']} ({c[val_key]})")

top('happiness_rank', 'happiness')
top('gdp_rank', 'gdp')
top('hdi_rank', 'hdi')
top('fifa_ranking')

coffee_countries = [c for c in countries if c.get('coffee') is not None]
print(f'\n=== COFFEE data available: {len(coffee_countries)} countries ===')
if coffee_countries:
    sc = sorted(coffee_countries, key=lambda x: x.get('coffee_rank', 999))
    for c in sc[:5]:
        print(f"  #{c.get('coffee_rank','?')} {c['flag']} {c['country_name_en']} ({c['coffee']})")
else:
    sc = sorted([c for c in countries if c.get('coffee')], key=lambda x: x['coffee'], reverse=True)
    if sc:
        for c in sc[:5]:
            print(f"  {c['flag']} {c['country_name_en']} ({c['coffee']})")

top('internet_pct_rank', 'internet_pct')
top('tourism_rank', 'tourism')
top('life_expectancy_rank', 'life_expectancy')
top('edu_rank', 'edu')
top('democracy_rank', 'democracy')
top('gpi_rank', 'gpi')
top('cpi_rank', 'cpi')
top('press_rank', 'press')
top('fertility_rank', 'fertility')
top('forest_rank', 'forest')
top('literacy_rank', 'literacy')
top('co2_rank', 'co2')

top_val('olympic')
top_val('nobel')
top_val('nobel_per_capita')
top_val('beer')
top_val('wine')
top_val('chocolate')
top_val('mcdonalds')
top_val('chess')
top_val('startups')
top_val('books')
