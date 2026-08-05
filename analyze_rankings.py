import json

with open('docs/data/countries.json', 'r') as f:
    countries = json.load(f)

# Find ranking fields that have data
ranking_fields = [k for k in countries[0].keys() if k.endswith('_rank') and k != 'country_code']
print(f'Total countries: {len(countries)}')

# For each ranking field, count non-null values
results = []
for field in ranking_fields:
    count = sum(1 for c in countries if c.get(field) is not None)
    if count >= 3:
        base = field.replace('_rank', '')
        val_count = sum(1 for c in countries if c.get(base) is not None)
        results.append((count, field, val_count))

results.sort(reverse=True)
for count, field, val_count in results:
    print(f'{field}: {count} countries ranked (base value in {val_count})')
