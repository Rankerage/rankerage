import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Coffee consumption
coffee_data = [(c['country_name_en'], c.get('coffee'), c['flag']) for c in countries if c.get('coffee') is not None]
coffee_data.sort(key=lambda x: x[1], reverse=True)

print('Top 10 Coffee Consumption (kg per capita/year):')
for i, (name, val, flag) in enumerate(coffee_data[:10], 1):
    print(f'{i}. {flag} {name}: {val} kg')

print()

# Happiness
happy_data = [(c['country_name_en'], c.get('happiness'), c['flag']) for c in countries if c.get('happiness') is not None]
happy_data.sort(key=lambda x: x[1], reverse=True)
print('Top 5 Happiness:')
for i, (name, val, flag) in enumerate(happy_data[:5], 1):
    print(f'{i}. {flag} {name}: {val}')

print()

# FIFA
fifa_data = [(c['country_name_en'], c.get('fifa_ranking'), c['flag']) for c in countries if c.get('fifa_ranking') is not None]
fifa_data.sort(key=lambda x: x[1])  # Lower is better
print('Top 5 FIFA (lower is better):')
for i, (name, val, flag) in enumerate(fifa_data[:5], 1):
    print(f'{i}. {flag} {name}: {val}')

print()

# Chocolate
choc_data = [(c['country_name_en'], c.get('chocolate'), c['flag']) for c in countries if c.get('chocolate') is not None]
choc_data.sort(key=lambda x: x[1], reverse=True)
print('Top 5 Chocolate (kg per capita):')
for i, (name, val, flag) in enumerate(choc_data[:5], 1):
    print(f'{i}. {flag} {name}: {val} kg')
