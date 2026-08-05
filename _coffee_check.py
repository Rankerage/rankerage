import json

with open('docs/data/countries.json', 'r') as f:
    countries = json.load(f)

# Coffee rankings - show more data
coffee = [(c['country_name_en'], c.get('coffee'), c.get('flag', ''), c.get('coffee_rank')) for c in countries if c.get('coffee') is not None]
coffee.sort(key=lambda x: x[1], reverse=True)
print('=== COFFEE TOP 10 ===')
for name, val, flag, rank in coffee[:10]:
    print(f'  {flag} {name}: {val} (rank: {rank})')

# South Korea coffee
for c in countries:
    if c['country_name_en'] == 'South Korea':
        print(f'\nSouth Korea coffee: {c.get("coffee")} kg, rank: {c.get("coffee_rank")}')
        print(f'  Population: {c.get("population")}')
        print(f'  GDP per capita: {c.get("gdp_per_capita")}')
        break
