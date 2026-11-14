# -*- coding: utf-8 -*-
import json, os

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'countries.json'), 'r', encoding='utf-8') as f:
    data = json.load(f)

print('Total countries:', len(data))
print('Keys sample:', sorted(data[0].keys()))

def show(title, key, reverse=True, fmt=lambda v: v, extra=None, top=5, filter_none=True):
    items = [c for c in data if c.get(key) is not None] if filter_none else data
    items = sorted(items, key=lambda x: x.get(key) or 0, reverse=reverse)
    print('\n=== %s ===' % title)
    for c in items[:top]:
        e = (' | ' + extra(c)) if extra else ''
        print('%s %s: %s%s' % (c['flag'], c['country_name_en'], fmt(c.get(key)), e))

show('HAPPINESS TOP', 'happiness', fmt=lambda v: '%.2f' % v, extra=lambda c: 'gdp_pc=%s' % c.get('gdp_per_capita'))
show('HAPPINESS BOTTOM', 'happiness', reverse=False, fmt=lambda v: '%.2f' % v)
show('GDP PER CAPITA TOP', 'gdp_per_capita', fmt=lambda v: int(v))
show('FIFA TOP (lower=better)', 'fifa_ranking', reverse=False)
show('LIFE EXPECTANCY TOP', 'life_expectancy', fmt=lambda v: '%.1f' % v)
show('INTERNET %% TOP', 'internet_pct', fmt=lambda v: '%s%%' % v)
show('CPI LEAST CORRUPT TOP', 'cpi')
show('CO2 PER CAPITA TOP', 'co2', fmt=lambda v: '%.1f t' % v)
show('FOREST %% TOP', 'forest', fmt=lambda v: '%s%%' % v)
show('DEMOCRACY TOP', 'democracy', fmt=lambda v: '%.2f' % v)
show('CRICKET RANKING TOP (lower=better)', 'cricket', reverse=False)
show('EDU INDEX TOP', 'edu', fmt=lambda v: '%.2f' % v)
show('TOURISM TOP', 'tourism', fmt=lambda v: '%sM' % v)
show('FERTILITY TOP', 'fertility', fmt=lambda v: '%.2f' % v)
show('MILITARY PCT TOP', 'military_pct', fmt=lambda v: '%s%%' % v)
show('OLYMPIC MEDALS TOP', 'olympic', fmt=lambda v: v)
show('NUCLEAR TOP', 'nuclear', fmt=lambda v: v)
show('NOBEL TOP', 'nobel', fmt=lambda v: v)
show('PATENTS TOP', 'patents', fmt=lambda v: v)
show('PM25 (air pollution) TOP', 'pm25', fmt=lambda v: v)
show('SMOKING TOP', 'smoking', fmt=lambda v: '%s%%' % v)
show('ALCOHOL TOP', 'alcohol', fmt=lambda v: v)
show('OBESITY TOP', 'obesity', fmt=lambda v: '%s%%' % v)
show('SUICIDE TOP', 'suicide', fmt=lambda v: v)
show('MURDER RATE TOP', 'murder', fmt=lambda v: v)
show('MCDONALDS TOP', 'mcdonalds', fmt=lambda v: v)
show('HERITAGE SITES TOP', 'heritage', fmt=lambda v: v)
