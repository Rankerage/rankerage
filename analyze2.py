import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# FIFA ranking - lower is better (1 = best)
print("=== FIFA RANKING TOP 5 ===")
fifa = [(c.get('fifa_ranking', 9999), c.get('flag',''), c.get('country_name_en',''), c.get('fifa_ranking_rank', 9999)) 
        for c in countries if c.get('fifa_ranking') is not None]
fifa.sort()
for rank_val, flag, name, rank_rank in fifa[:5]:
    print(f"  {flag} {name}: FIFA={rank_val}, rank={rank_rank}")

print()
print("=== HAPPINESS TOP 5 ===")
happy = [(c.get('happiness', 0), c.get('flag',''), c.get('country_name_en',''), c.get('happiness_rank', 9999))
         for c in countries if c.get('happiness') is not None]
happy.sort(reverse=True)
for val, flag, name, rank in happy[:5]:
    print(f"  {flag} {name}: happiness={val}, rank={rank}")

print()
print("=== GDP PER CAPITA TOP 5 ===")
gdp_pc = [(c.get('gdp_per_capita', 0), c.get('flag',''), c.get('country_name_en',''), c.get('gdp_per_capita_rank', 9999))
          for c in countries if c.get('gdp_per_capita') is not None]
gdp_pc.sort(reverse=True)
for val, flag, name, rank in gdp_pc[:5]:
    print(f"  {flag} {name}: gdp_per_capita={val}, rank={rank}")

print()
print("=== HDI TOP 5 ===")
hdi = [(c.get('hdi', 0), c.get('flag',''), c.get('country_name_en',''), c.get('hdi_rank', 9999))
       for c in countries if c.get('hdi') is not None]
hdi.sort(reverse=True)
for val, flag, name, rank in hdi[:5]:
    print(f"  {flag} {name}: hdi={val}, rank={rank}")

print()
print("=== LIFE EXPECTANCY TOP 5 ===")
life = [(c.get('life_expectancy', 0), c.get('flag',''), c.get('country_name_en',''), c.get('life_expectancy_rank', 9999))
        for c in countries if c.get('life_expectancy') is not None]
life.sort(reverse=True)
for val, flag, name, rank in life[:5]:
    print(f"  {flag} {name}: life_expectancy={val}, rank={rank}")

print()
print("=== 재생에너지 TOP 5 ===")
renew = [(c.get('renew', 0), c.get('flag',''), c.get('country_name_en',''), c.get('renew_rank', 9999))
         for c in countries if c.get('renew') is not None]
renew.sort(reverse=True)
for val, flag, name, rank in renew[:5]:
    print(f"  {flag} {name}: renew={val}%, rank={rank}")

print()
print("=== MURDER RATE LOWEST (best) ===")
murder = [(c.get('murder', 999), c.get('flag',''), c.get('country_name_en',''), c.get('murder_rank', 9999))
          for c in countries if c.get('murder') is not None]
murder.sort()  # lower is better
for val, flag, name, rank in murder[:5]:
    print(f"  {flag} {name}: murder={val}, rank={rank}")

print()
print("=== FOREST TOP 5 ===")
forest = [(c.get('forest', 0), c.get('flag',''), c.get('country_name_en',''), c.get('forest_rank', 9999))
          for c in countries if c.get('forest') is not None]
forest.sort(reverse=True)
for val, flag, name, rank in forest[:5]:
    print(f"  {flag} {name}: forest={val}%, rank={rank}")
