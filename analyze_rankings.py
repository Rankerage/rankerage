import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Find all rank fields
rank_fields = set()
direct_fields = set()
for c in countries:
    for k, v in c.items():
        if isinstance(v, (int, float)):
            if k.endswith('_rank'):
                rank_fields.add(k)
            elif k not in ('lat', 'lon'):
                direct_fields.add(k)

print("=== Rank fields ===")
for f in sorted(rank_fields):
    print(f"  {f}")
print(f"\nTotal: {len(rank_fields)} rank fields")

print("\n=== Direct value fields (non-rank, non-lat/lon) ===")
for f in sorted(direct_fields):
    print(f"  {f}")
print(f"\nTotal: {len(direct_fields)} direct fields")

# Pick some interesting ones and find top 5 countries
interesting = [
    'happiness', 'happiness_rank',
    'gdp', 'gdp_rank',
    'fifa_ranking', 'fifa_ranking_rank',
    'coffee', 'cricket', 'cricket_rank',
    'olympic', 'nobel', 'chess',
    'beer', 'wine', 'chocolate',
    'life_expectancy', 'life_expectancy_rank',
    'internet_pct', 'internet_pct_rank',
    'tourism', 'tourism_rank',
    'fertility', 'fertility_rank',
    'literacy', 'literacy_rank',
    'forest', 'forest_rank',
    'edu', 'edu_rank',
    'renew', 'renew_rank',
]

for field in interesting:
    if field.endswith('_rank'):
        # Sort by rank (lower is better)
        base = field.replace('_rank', '')
        ranked = [(c.get(field, 9999), c.get('flag', '🏳️'), c.get('country_name_en', '?'), c.get(base)) 
                  for c in countries if c.get(field) is not None and c.get(field) > 0]
        ranked.sort(key=lambda x: x[0])
        if ranked:
            print(f"\n=== Top 5 by {field} ===")
            for rank, flag, name, val in ranked[:5]:
                print(f"  #{rank} {flag} {name} ({base}: {val})")
    else:
        # Direct value - sort descending
        ranked = [(c.get(field), c.get('flag', '🏳️'), c.get('country_name_en', '?')) 
                  for c in countries if c.get(field) is not None]
        ranked.sort(key=lambda x: x[0] or 0, reverse=True)
        if ranked and ranked[0][0] is not None:
            print(f"\n=== Top 5 by {field} ===")
            for val, flag, name in ranked[:5]:
                print(f"  {flag} {name}: {val}")
