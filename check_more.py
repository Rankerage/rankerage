import json

with open('docs/data/countries.json', 'r') as f:
    data = json.load(f)

# Netflix ranking
print('=== NETFLIX TOP 10 ===')
netflix_data = [(c['flag'], c['country_name_en'], c.get('netflix', 0), c.get('netflix_rank', 999)) 
                for c in data if c.get('netflix') is not None]
netflix_data.sort(key=lambda x: -x[2])  # Higher netflix value = better
for i, (f, n, v, r) in enumerate(netflix_data[:10]):
    print(f'  {i+1}. {f} {n} - score:{v} rank:{r}')

# Internet speed
print('\n=== NETSPEED TOP 10 ===')
speed_data = [(c['flag'], c['country_name_en'], c.get('netspeed', 0), c.get('netspeed_rank', 999)) 
              for c in data if c.get('netspeed') is not None]
speed_data.sort(key=lambda x: -x[2])
for i, (f, n, v, r) in enumerate(speed_data[:10]):
    print(f'  {i+1}. {f} {n} - speed:{v} rank:{r}')

# G5 coverage
print('\n=== G5 COVERAGE TOP 10 ===')
g5_data = [(c['flag'], c['country_name_en'], c.get('g5_coverage', 0), c.get('g5_coverage_rank', 999)) 
           for c in data if c.get('g5_coverage') is not None]
g5_data.sort(key=lambda x: -x[2])
for i, (f, n, v, r) in enumerate(g5_data[:10]):
    print(f'  {i+1}. {f} {n} - coverage:{v} rank:{r}')

# Social media
print('\n=== SOCIAL MEDIA TOP 10 ===')
sm_data = [(c['flag'], c['country_name_en'], c.get('social_media', 0), c.get('social_media_rank', 999)) 
           for c in data if c.get('social_media') is not None]
sm_data.sort(key=lambda x: -x[2])
for i, (f, n, v, r) in enumerate(sm_data[:10]):
    print(f'  {i+1}. {f} {n} - usage:{v} rank:{r}')

# E-scooter
print('\n=== E-SCOOTER TOP 10 ===')
escooter_data = [(c['flag'], c['country_name_en'], c.get('e_scooter', 0), c.get('e_scooter_rank', 999)) 
                 for c in data if c.get('e_scooter') is not None]
escooter_data.sort(key=lambda x: -x[2])
for i, (f, n, v, r) in enumerate(escooter_data[:10]):
    print(f'  {i+1}. {f} {n} - value:{v} rank:{r}')

# Food waste
print('\n=== FOOD WASTE TOP 10 ===')
fw_data = [(c['flag'], c['country_name_en'], c.get('food_waste', 0), c.get('food_waste_rank', 999)) 
           for c in data if c.get('food_waste') is not None]
fw_data.sort(key=lambda x: -x[2])  
for i, (f, n, v, r) in enumerate(fw_data[:10]):
    print(f'  {i+1}. {f} {n} - value:{v} rank:{r}')

# Coffee
print('\n=== COFFEE TOP 10 ===')
coffee_data = [(c['flag'], c['country_name_en'], c.get('coffee', 0), c.get('coffee_rank', 999)) 
               for c in data if c.get('coffee') is not None]
coffee_data.sort(key=lambda x: -x[2])
for i, (f, n, v, r) in enumerate(coffee_data[:10]):
    print(f'  {i+1}. {f} {n} - consumption:{v} rank:{r}')
