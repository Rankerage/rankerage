import json

with open('docs/data/countries.json', 'r') as f:
    countries = json.load(f)

# Get top 3 happiness
happiness = [(c, c['happiness']) for c in countries if c.get('happiness') is not None]
happiness.sort(key=lambda x: -x[1])
print("=== TOP 3 HAPPINESS ===")
for i, (c, val) in enumerate(happiness[:3]):
    print(f'{i+1}. {c["flag"]} {c["country_name_en"]}: {val}')

# Fun facts about Finland
finland = [c for c in countries if c['country_name_en'] == 'Finland'][0]
print(f"\n=== FINLAND FACTS ===")
interesting = ['happiness', 'coffee', 'forest', 'edu', 'gpi', 'cpi', 'internet_pct', 'life_expectancy', 'press']
for key in interesting:
    val = finland.get(key)
    rank_key = f'{key}_rank' if key != 'happiness' else 'happiness_rank'
    rank = finland.get(rank_key)
    if val is not None:
        print(f'  {key}: {val} (rank: {rank})')

# Also print Korea's happiness
korea = [c for c in countries if c['country_name_en'] == 'South Korea']
if korea:
    k = korea[0]
    print(f"\n=== SOUTH KOREA ===")
    print(f'  happiness: {k.get("happiness")} (rank: {k.get("happiness_rank")})')
