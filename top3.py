import json

with open('docs/data/countries.json', 'r') as f:
    countries = json.load(f)

# Fields where higher is better/more
higher_better = ['happiness', 'coffee', 'beer', 'wine', 'chocolate', 'nobel', 'nobel_per_capita', 'olympic', 'books', 'startups', 'math_olympiad', 'mcdonalds', 'smoking', 'alcohol', 'meat', 'gdp_per_capita', 'gdp', 'hdi', 'internet_pct', 'life_expectancy', 'literacy', 'renew']

# Fields where lower is better
lower_better = ['fifa_ranking', 'obesity', 'cpi', 'gpi', 'co2', 'press', 'infant_mortality', 'maternal_mortality']

fields_to_check = ['coffee', 'beer', 'wine', 'chocolate', 'happiness', 'obesity', 'mcdonalds', 'smoking', 'alcohol', 'meat', 'nobel_per_capita', 'startups', 'books', 'fifa_ranking', 'math_olympiad']

for field in fields_to_check:
    ranked = [(c['country_name_en'], c.get(field), c.get('flag', '')) for c in countries if c.get(field) is not None]
    if not ranked:
        continue
    
    if field in higher_better:
        ranked.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
    else:
        ranked.sort(key=lambda x: x[1] if x[1] is not None else float('inf'))
    
    print(f'=== {field} ===')
    for name, val, flag in ranked[:3]:
        print(f'  {flag} {name}: {val}')
    print()
