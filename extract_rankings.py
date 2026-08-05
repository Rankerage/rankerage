import json

with open('docs/data/countries.json', 'r') as f:
    data = json.load(f)

rankings = ['happiness_rank', 'fifa_ranking', 'gdp_per_capita_rank', 'internet_pct_rank', 'cpi_rank', 'hdi_rank', 'life_expectancy_rank']

for r in rankings:
    # Sort by rank (lower = better for all rank fields)
    sorted_data = sorted(data, key=lambda x: x.get(r) or 9999)
    raw_field = r.replace('_rank', '')
    print(f'=== {r} ===')
    for i, c in enumerate(sorted_data[:5]):
        val = c.get(r, 'N/A')
        raw_val = c.get(raw_field, 'N/A')
        print(f'  {i+1}. {c["flag"]} {c["country_name_en"]} - rank:{val} raw:{raw_val}')
    print()
