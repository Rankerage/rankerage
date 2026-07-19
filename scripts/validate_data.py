#!/usr/bin/env python3
"""validate_data.py — countries.json 무결성 검사 (entity-aware)"""
import json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "docs", "data", "countries.json")

with open(DATA) as f:
    data = json.load(f)

errors = 0
codes = set()

REQUIRED = ['country_code', 'country_name_en', 'flag']

print(f"Total entries: {len(data)}")

for i, c in enumerate(data):
    name = c.get('country_name_en', f'Entry {i}')
    code = c.get('country_code', '')
    is_entity = name.startswith('*')
    
    # Check required fields (entities don't need flag — use icon in formatter)
    for field in REQUIRED:
        if field == 'flag' and is_entity:
            continue  # entities use category icons, not flags
        if field not in c or not c[field]:
            print(f'  ❌ {name}: missing {field}')
            errors += 1
    
    # Check duplicate codes (warning only — entities may share codes across categories)
    if code in codes:
        print(f'  ⚠️ {name}: duplicate country_code {code}')
    codes.add(code)
    
    # Check entity prefix consistency
    stars = name.count('*') if name.startswith('*') else 0
    if stars > 0:
        continent = c.get('continent', '')
        if stars == 1 and '기업' not in str(continent):
            print(f'  ⚠️ {name}: single * but continent is not 기업')
        elif stars == 2 and '인물' not in str(continent):
            print(f'  ⚠️ {name}: double ** but continent is not 인물')
        elif stars == 3 and '단체' not in str(continent):
            print(f'  ⚠️ {name}: triple *** but continent is not 단체')

# Count by type
countries = [d for d in data if not d['country_name_en'].startswith('*')]
companies = [d for d in data if d['country_name_en'].count('*') == 1]
individuals = [d for d in data if d['country_name_en'].count('*') == 2]
orgs = [d for d in data if d['country_name_en'].count('*') == 3]

print(f"\n   🌍 Countries: {len(countries)}")
print(f"   🌐 Companies: {len(companies)}")
print(f"   ⭐ Individuals: {len(individuals)}")
print(f"   🏟️ Organizations: {len(orgs)}")

if errors:
    print(f'\n❌ {errors} errors found!')
    sys.exit(1)
else:
    print(f'\n✅ All {len(data)} entries valid')
