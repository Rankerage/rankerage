import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Find South Korea
for c in countries:
    if c['country_name_en'] == 'South Korea':
        print(f'🇰🇷 South Korea:')
        print(f'  Coffee: {c.get("coffee")} kg per capita')
        print(f'  Coffee rank: {c.get("coffee_rank")}')
        print(f'  Happiness: {c.get("happiness")} (rank: {c.get("happiness_rank")})')
        print(f'  FIFA: {c.get("fifa_ranking")}')
        print(f'  GDP: {c.get("gdp")} (rank: {c.get("gdp_rank")})')
        print(f'  Internet: {c.get("internet_pct")}%')
        break
