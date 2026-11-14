import json

with open('countries.json', encoding='utf-8') as f:
    data = json.load(f)

# Find non-null coffee entries, sort descending
coffee = [(c['country_name_en'], c['flag'], c.get('coffee')) for c in data if c.get('coffee')]
coffee.sort(key=lambda x: x[2], reverse=True)
print("COFFEE TOP 15:")
for name, flag, val in coffee[:15]:
    print(f"  {flag} {name}: {val}")

# Also list which ranking fields have good coverage
from collections import Counter
rank_fields = [k for k in data[0] if k.endswith('_rank')]
coverage = {k: sum(1 for c in data if c.get(k) is not None) for k in rank_fields}
cov_sorted = sorted(coverage.items(), key=lambda x: -x[1])
print("\nTOP RANK FIELDS BY COVERAGE:")
for k, v in cov_sorted[:25]:
    print(f"  {k}: {v}/{len(data)}")
