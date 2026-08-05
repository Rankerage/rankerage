import json
with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Surprising facts
for name in ['Mexico', 'Brazil', 'Colombia', 'Costa Rica', 'Panama', 'Uruguay', 'El Salvador', 'Guatemala']:
    for c in countries:
        if c.get('country_name_en') == name:
            h = c.get('happiness_rank', '?')
            g = c.get('gdp_per_capita_rank', '?')
            hs = c.get('happiness', '?')
            print(f'{c["flag"]} {name}: happiness #{h} (score={hs}), GDP/cap #{g}')
            break

print()
# Check South Korea too
for c in countries:
    if c.get('country_name_en') == 'South Korea':
        print(f'{c["flag"]} South Korea: happiness #{c.get("happiness_rank")}, GDP/cap #{c.get("gdp_per_capita_rank")}, internet #{c.get("internet_pct_rank")}')
        break
