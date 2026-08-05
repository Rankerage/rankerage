import json
with open('countries.json', 'r', encoding='utf-8') as f:
    countries = json.load(f)

# Get more coffee data
coffee = [c for c in countries if c.get('coffee')]
coffee.sort(key=lambda x: x['coffee'], reverse=True)
print('=== COFFEE CONSUMPTION (kg per capita per year) ===')
for c in coffee[:15]:
    print(f"  {c['flag']} {c['country_name_en']}: {c['coffee']} kg (rank #{c.get('coffee_rank','?')})")

# Check South Korea
for c in countries:
    if c['country_name_en'] == 'South Korea':
        print(f"\n🇰🇷 South Korea coffee: {c.get('coffee')} kg, rank: {c.get('coffee_rank')}")
        print(f"  Population: {c.get('population')}")
        break

# Also check how many countries have coffee data
print(f"\nTotal countries with coffee data: {len(coffee)}")
