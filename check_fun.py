import json

with open('docs/data/countries.json', 'r') as f:
    countries = json.load(f)

# Check which "fun" fields have data
fun_fields = ['coffee', 'beer', 'wine', 'chocolate', 'happiness', 'fifa_ranking', 'chess', 'nobel', 'nobel_per_capita', 'olympic', 'cricket', 'rugby', 'basket', 'mcdonalds', 'smoking', 'obesity', 'alcohol', 'meat', 'books', 'startups', 'math_olympiad']

for field in fun_fields:
    count = sum(1 for c in countries if c.get(field) is not None)
    if count > 0:
        print(f'{field}: {count} countries have data')
        # Show top 5
        ranked = [(c['country_name_en'], c.get(field), c.get('flag', '')) for c in countries if c.get(field) is not None]
        # For happiness higher is better, for fifa lower is better
        if field in ['happiness', 'nobel', 'nobel_per_capita', 'olympic', 'books', 'startups', 'math_olympiad']:
            ranked.sort(key=lambda x: x[1], reverse=True)
        else:
            ranked.sort(key=lambda x: x[1])
        for name, val, flag in ranked[:5]:
            print(f'  {flag} {name}: {val}')
        print()
