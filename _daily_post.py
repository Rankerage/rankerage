import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Find South Korea's coffee rank
for c in countries:
    if c['country_name_en'] == 'South Korea':
        print(f"🇰🇷 South Korea coffee: {c.get('coffee')} kg, rank: {c.get('coffee_rank')}")
        print(f"  Chocolate: {c.get('chocolate')}, rank: {c.get('chocolate_rank')}")
        print(f"  Beer: {c.get('beer')}, rank: {c.get('beer_rank')}")
        print(f"  Happiness: {c.get('happiness')}, rank: {c.get('happiness_rank')}")
        print(f"  Startups: {c.get('startups')}, rank: {c.get('startups_rank')}")
        print(f"  Nobel per capita: {c.get('nobel_per_capita')}, rank: {c.get('nobel_per_capita_rank')}")
        print(f"  Life expectancy: {c.get('life_expectancy')}, rank: {c.get('life_expectancy_rank')}")
        print(f"  Chess: {c.get('chess')}, rank: {c.get('chess_rank')}")
        print(f"  Olympic: {c.get('olympic')}, rank: {c.get('olympic_rank')}")
        print(f"  Nobel: {c.get('nobel')}, rank: {c.get('nobel_rank')}")
        print(f"  Internet: {c.get('internet_pct')}%, rank: {c.get('internet_pct_rank')}")
        break
