import json

with open('docs/data/countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Filter only real countries (exclude XX-prefix entries and things like Harvard, MIT)
# Real countries have population data typically
real = [c for c in countries if c.get('population') is not None and c.get('flag') and not c.get('country_name_en','').startswith('XX')]

print(f"Real countries (with population): {len(real)}")

# FIFA real countries
fifa = [(c['fifa_ranking'], c['flag'], c['country_name_en'], c.get('fifa_ranking_rank'))
        for c in real if c.get('fifa_ranking') is not None]
fifa.sort()
print("\n=== FIFA REAL TOP 5 ===")
for val, flag, name, rank in fifa[:5]:
    print(f"  {flag} {name}: FIFA ranking={val}, rank={rank}")

# Check some interesting facts for happiness
print("\n=== HAPPINESS BOTTOM 5 ===")
happy = [(c['happiness'], c['flag'], c['country_name_en'])
         for c in real if c.get('happiness') is not None]
happy.sort()
for val, flag, name in happy[:5]:
    print(f"  {flag} {name}: {val}")

# Where does Korea rank in happiness?
for c in real:
    if 'Korea' in c.get('country_name_en','') and c.get('happiness'):
        print(f"\n🇰🇷 South Korea happiness: {c['happiness']}, rank: {c.get('happiness_rank')}")

# Check forest - South Korea at #4, relevant for Korean audience
print("\n=== FOREST - Korea ===")
for c in real:
    if 'Korea' in c.get('country_name_en','') and c.get('forest'):
        print(f"  {c['flag']} {c['country_name_en']}: forest={c['forest']}%, rank={c.get('forest_rank')}")

# 재생에너지 with full data
print("\n=== RENEWABLE ENERGY DETAIL ===")
renew = [(c['renew'], c['flag'], c['country_name_en'], c.get('renew_rank'), c.get('population',0))
         for c in real if c.get('renew') is not None]
renew.sort(reverse=True)
for val, flag, name, rank, pop in renew[:8]:
    print(f"  {flag} {name}: renew={val}%, rank={rank}, pop={pop:,}")
