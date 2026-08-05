import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Fields we might care about for rankings
rank_fields = [
    'happiness', 'happiness_rank', 'fifa_ranking', 'cpi', 'cpi_rank', 
    'gpi', 'gpi_rank', 'internet_pct', 'internet_pct_rank',
    'life_expectancy', 'life_expectancy_rank', 'hdi', 'hdi_rank',
    'gdp_per_capita', 'gdp_per_capita_rank', 'tourism', 'tourism_rank',
    'co2', 'co2_rank', 'cricket', 'cricket_rank', 'education',
    'fertility', 'fertility_rank', 'forest', 'forest_rank',
    'democracy', 'democracy_rank', 'press', 'press_rank',
]

# Check which fields are populated
for field in rank_fields:
    vals = [c.get(field) for c in countries if c.get(field) is not None]
    print(f'{field}: {len(vals)}/{len(countries)} non-null, sample: {vals[:5]}')
