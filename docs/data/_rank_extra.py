# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'countries.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

# Coffee
items = [c for c in data if c.get('coffee') is not None]
items = sorted(items, key=lambda x: x.get('coffee') or 0, reverse=True)
print('=== COFFEE CONSUMPTION TOP ===')
for c in items[:10]:
    print('%s %s: %s kg/인' % (c['flag'], c['country_name_en'], c.get('coffee')))

# Also check some other quirky ones
for key in ['beer', 'wine', 'chocolate', 'chess', 'meat', 'salary', 'gas_price', 'startups', 'books', 'car_density']:
    ikeys = [c for c in data if c.get(key) is not None]
    if ikeys:
        isorted = sorted(ikeys, key=lambda x: x.get(key) or 0, reverse=True)
        print('\n=== %s TOP 5 ===' % key.upper())
        for c in isorted[:5]:
            print('%s %s: %s' % (c['flag'], c['country_name_en'], c.get(key)))