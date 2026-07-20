import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Filter to countries with happiness data
happy = [(c['flag'], c['country_name_en'], c['happiness'], c['happiness_rank']) 
         for c in countries if c.get('happiness') is not None]

# Sort by rank (1 = happiest)
happy.sort(key=lambda x: x[3])

print("=== TOP 10 HAPPIEST ===")
for flag, name, score, rank in happy[:10]:
    print(f"  #{rank} {flag} {name} ({score})")

print("\n=== BOTTOM 5 LEAST HAPPY ===")
for flag, name, score, rank in happy[-5:]:
    print(f"  #{rank} {flag} {name} ({score})")

# Also let's get a few surprise facts
# Find countries where happiness rank >> GDP rank (happier than their wealth suggests)
gdp_happy = [(c['flag'], c['country_name_en'], c.get('happiness_rank', 999), c.get('gdp_per_capita_rank', 999),
              c.get('happiness'), c.get('gdp_per_capita'))
             for c in countries 
             if c.get('happiness_rank') is not None and c.get('gdp_per_capita_rank') is not None]

# Find where happiness rank is much better than GDP rank
gdp_happy.sort(key=lambda x: x[2] - x[1])  # negative = happier than rich

print("\n=== HAPPIER THAN THEIR WEALTH (happiness rank - gdp rank) ===")
for flag, name, h_rank, g_rank, h_score, gdp in gdp_happy[:10]:
    diff = h_rank - g_rank
    print(f"  {flag} {name}: happiness #{h_rank}, GDP/capita #{g_rank} (diff: {diff})")
