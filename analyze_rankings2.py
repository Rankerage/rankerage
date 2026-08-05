import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

def top_n(field, field_name, n=5):
    data = [(c['country_name_en'], c['flag'], c.get(field)) for c in countries if c.get(field) is not None]
    data.sort(key=lambda x: x[2])
    print(f"\n=== Top {n} {field_name} ===")
    for name, flag, rank in data[:n]:
        print(f'{flag} {name}: rank {rank}')

top_n('coffee_rank', 'Coffee Consumption')
top_n('chocolate_rank', 'Chocolate Consumption')
top_n('beer_rank', 'Beer Consumption')
top_n('wine_rank', 'Wine Consumption')
top_n('internet_pct_rank', 'Internet Penetration')
top_n('basket_rank', 'Basketball (FIBA)')
top_n('chess_rank', 'Chess')
top_n('cricket_rank', 'Cricket')
top_n('olympic_rank', 'Olympic Medals')
top_n('nobel_per_capita_rank', 'Nobel per Capita')
top_n('gpi_rank', 'Global Peace Index')
top_n('startups_rank', 'Startups')
top_n('renew_rank', 'Renewable Energy')
top_n('hdi_rank', 'Human Development Index')
