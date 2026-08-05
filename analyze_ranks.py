import json

with open(r'C:\Users\mathe\Desktop\rankerage\docs\data\countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

rank_fields = {
    'happiness': 'happiness_rank', 'gdp': 'gdp_rank', 'gdp_per_capita': 'gdp_per_capita_rank',
    'hdi': 'hdi_rank', 'life_expectancy': 'life_expectancy_rank', 'fifa': 'fifa_ranking_rank',
    'cpi': 'cpi_rank', 'gpi': 'gpi_rank', 'internet': 'internet_pct_rank',
    'military': 'military_pct_rank', 'fertility': 'fertility_rank', 'press': 'press_rank',
    'co2': 'co2_rank', 'forest': 'forest_rank', 'democracy': 'democracy_rank',
    'edu': 'edu_rank', 'population_density': 'population_density_rank',
    'tourism': 'tourism_rank', 'murder': 'murder_rank', 'debt': 'debt_rank',
    'birth_rate': 'birth_rate_rank', 'infant_mortality': 'infant_mortality_rank',
    'median_age': 'median_age_rank', 'obesity': 'obesity_rank', 'alcohol': 'alcohol_rank',
    'coffee': 'coffee_rank', 'nobel': 'nobel_rank', 'smoking': 'smoking_rank',
    'suicide': 'suicide_rank', 'literacy': 'literacy_rank', 'english': 'english_rank',
}

for field_name, rank_field in rank_fields.items():
    valid = [(c['flag'], c['country_name_en'], c.get(field_name), c.get(rank_field))
             for c in countries
             if c.get(field_name) is not None and c.get(rank_field) is not None and c.get(rank_field) <= 200]
    if len(valid) >= 3:
        valid_sorted = sorted(valid, key=lambda x: x[3])
        top3 = valid_sorted[:3]
        print(f'--- {field_name} ({len(valid)} countries) ---')
        for flag, name, val, rank in top3:
            print(f'  #{int(rank)} {flag} {name}: {val}')
        print()
