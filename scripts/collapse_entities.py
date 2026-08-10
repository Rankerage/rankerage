#!/usr/bin/env python3
"""collapse_entities.py — 1022개 엔티티 → 3개 대표행으로 축소"""
import json, sys

DATA_FILE = "docs/data/countries.json"

with open(DATA_FILE) as f:
    data = json.load(f)

countries = []
companies, people, orgs = [], [], []

for d in data:
    name = d.get('country_name_en', '')
    if name.startswith('***'):
        orgs.append(d)
    elif name.startswith('**'):
        people.append(d)
    elif name.startswith('*'):
        companies.append(d)
    else:
        countries.append(d)

print(f"국가: {len(countries)}, 기업: {len(companies)}, 인물: {len(people)}, 단체: {len(orgs)}")

def aggregate(entities, prefix, code, continent, subcontinent, capital, name_en, name_local):
    agg = {
        'country_code': code,
        'country_name_en': name_en,
        'country_name_local': name_local,
        'continent': continent,
        'subcontinent': subcontinent,
        'capital_en': capital,
        'flag': code,
        'country_summary': f'{len(entities)} entities in this category',
    }
    
    numeric_fields = set()
    for e in entities:
        for k, v in e.items():
            if isinstance(v, (int, float)) and not k.startswith('_') and not k.endswith('_rank') and v is not None:
                numeric_fields.add(k)
    
    for field in numeric_fields:
        vals = [e.get(field) for e in entities if e.get(field) is not None]
        if vals:
            agg[field] = max(vals)
    
    return agg

agg_c = aggregate(companies, '*', 'XXCOMPS', '🏢기업', '통합', 'Global', '*Companies', '*기업')
agg_p = aggregate(people, '**', 'XXPEEPS', '⭐인물', '통합', 'Global', '**People', '**인물')
agg_o = aggregate(orgs, '***', 'XXORGSS', '🏟️단체', '통합', 'Global', '***Organizations', '***단체')

new_data = countries + [agg_c, agg_p, agg_o]

with open(DATA_FILE, 'w') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=2)

print(f"완료: {len(new_data)}행 (국가 {len(countries)} + 통합 3행)")
