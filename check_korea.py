import json

with open('docs/data/countries.json', 'r') as f:
    data = json.load(f)

# Check where South Korea ranks in various metrics
korea = [c for c in data if c['country_name_en'] == 'South Korea']
if korea:
    k = korea[0]
    print('=== SOUTH KOREA ===')
    for field in sorted(k.keys()):
        if 'rank' in field and k[field] is not None:
            print(f'  {field}: {k[field]}')

# Also check some other interesting rankings
print('\n=== NOBEL ===')
nobel_data = [(c['flag'], c['country_name_en'], c.get('nobel', 0)) for c in data if c.get('nobel')]
nobel_data.sort(key=lambda x: -x[2])
for i, (f, n, v) in enumerate(nobel_data[:10]):
    print(f'  {i+1}. {f} {n} - {v}')

print('\n=== PATENTS ===')
patent_data = [(c['flag'], c['country_name_en'], c.get('patents', 0)) for c in data if c.get('patents')]
patent_data.sort(key=lambda x: -x[2])
for i, (f, n, v) in enumerate(patent_data[:10]):
    print(f'  {i+1}. {f} {n} - {v}')

print('\n=== TOURISM ===')
tourism_data = [(c['flag'], c['country_name_en'], c.get('tourism', 0)) for c in data if c.get('tourism')]
tourism_data.sort(key=lambda x: -x[2])
for i, (f, n, v) in enumerate(tourism_data[:10]):
    print(f'  {i+1}. {f} {n} - {v}')

print('\n=== OLYMPIC ===')
olympic_data = [(c['flag'], c['country_name_en'], c.get('olympic', 0)) for c in data if c.get('olympic')]
olympic_data.sort(key=lambda x: -x[2])
for i, (f, n, v) in enumerate(olympic_data[:10]):
    print(f'  {i+1}. {f} {n} - {v}')

print('\n=== ALCOHOL ===')
alcohol_data = [(c['flag'], c['country_name_en'], c.get('alcohol', 0)) for c in data if c.get('alcohol')]
alcohol_data.sort(key=lambda x: -x[2])
for i, (f, n, v) in enumerate(alcohol_data[:10]):
    print(f'  {i+1}. {f} {n} - {v}')
