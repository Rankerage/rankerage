#!/usr/bin/env python3
"""validate_data.py — countries.json 무결성 검사"""
import json, sys, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "docs", "data", "countries.json")

with open(DATA) as f:
    data = json.load(f)

errors = 0
fields = list(data[0].keys())
print(f"Countries: {len(data)}, Fields: {len(fields)}")

for i, c in enumerate(data):
    if len(c) != len(fields):
        print(f'  ❌ Country {i}: {len(c)} fields (expected {len(fields)})')
        errors += 1
    if 'country_code' not in c or not c['country_code']:
        print(f'  ❌ Country {i}: missing country_code')
        errors += 1

if errors:
    print(f'\n❌ {errors} errors found!')
    sys.exit(1)
else:
    print(f'\n✅ All {len(data)} countries valid')
