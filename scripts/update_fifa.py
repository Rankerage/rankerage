#!/usr/bin/env python3
"""Update FIFA rankings in countries.json — run weekly via cron"""
import json, sys, urllib.request, re, os

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'public', 'data', 'countries.json')

def fetch_fifa_men():
    """Scrape FIFA Men's Ranking from FIFA website"""
    url = "https://inside.fifa.com/fifa-world-ranking/men"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"FIFA Men fetch failed: {e}")
        return {}

    # Look for ranking data in the page
    # FIFA typically embeds data in a script tag or JSON
    rankings = {}
    # Try to find country codes and ranks
    pattern = re.findall(r'"countryCode":"(\w{3})".*?"rank":(\d+)', html)
    if not pattern:
        pattern = re.findall(r'"abbreviation":"(\w{3})".*?"position":(\d+)', html)
    for code, rank in pattern:
        rankings[code.upper()] = int(rank)
    
    if rankings:
        print(f"FIFA Men: scraped {len(rankings)} rankings")
    return rankings

def fetch_fifa_women():
    """Scrape FIFA Women's Ranking"""
    url = "https://inside.fifa.com/fifa-world-ranking/women"
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"FIFA Women fetch failed: {e}")
        return {}

    rankings = {}
    pattern = re.findall(r'"countryCode":"(\w{3})".*?"rank":(\d+)', html)
    if not pattern:
        pattern = re.findall(r'"abbreviation":"(\w{3})".*?"position":(\d+)', html)
    for code, rank in pattern:
        rankings[code.upper()] = int(rank)
    
    if rankings:
        print(f"FIFA Women: scraped {len(rankings)} rankings")
    return rankings

def iso3_to_country_code(iso3):
    """Convert 3-letter ISO to 2-letter country code"""
    mapping = {
        'AFG':'af','ALB':'al','DZA':'dz','ASM':'as','AND':'ad','AGO':'ao','AIA':'ai',
        'ATG':'ag','ARG':'ar','ARM':'am','ABW':'aw','AUS':'au','AUT':'at','AZE':'az',
        'BHS':'bs','BHR':'bh','BGD':'bd','BRB':'bb','BLR':'by','BEL':'be','BLZ':'bz',
        'BEN':'bj','BMU':'bm','BTN':'bt','BOL':'bo','BIH':'ba','BWA':'bw','BRA':'br',
        'VGB':'vg','BRN':'bn','BGR':'bg','BFA':'bf','BDI':'bi','KHM':'kh','CMR':'cm',
        'CAN':'ca','CPV':'cv','CYM':'ky','CAF':'cf','TCD':'td','CHL':'cl','CHN':'cn',
        'COL':'co','COM':'km','COG':'cg','COD':'cd','COK':'ck','CRI':'cr','CIV':'ci',
        'HRV':'hr','CUB':'cu','CUW':'cw','CYP':'cy','CZE':'cz','DNK':'dk','DJI':'dj',
        'DMA':'dm','DOM':'do','ECU':'ec','EGY':'eg','SLV':'sv','ENG':'gb','GNQ':'gq',
        'ERI':'er','EST':'ee','ETH':'et','FRO':'fo','FJI':'fj','FIN':'fi','FRA':'fr',
        'GAB':'ga','GMB':'gm','GEO':'ge','DEU':'de','GHA':'gh','GIB':'gi','GRC':'gr',
        'GRD':'gd','GUM':'gu','GTM':'gt','GIN':'gn','GNB':'gw','GUY':'gy','HTI':'ht',
        'HND':'hn','HKG':'hk','HUN':'hu','ISL':'is','IND':'in','IDN':'id','IRN':'ir',
        'IRQ':'iq','ISR':'il','ITA':'it','JAM':'jm','JPN':'jp','JOR':'jo','KAZ':'kz',
        'KEN':'ke','PRK':'kp','KOR':'kr','KWT':'kw','KGZ':'kg','LAO':'la','LVA':'lv',
        'LBN':'lb','LSO':'ls','LBR':'lr','LBY':'ly','LIE':'li','LTU':'lt','LUX':'lu',
        'MAC':'mo','MDG':'mg','MWI':'mw','MYS':'my','MDV':'mv','MLI':'ml','MLT':'mt',
        'MRT':'mr','MUS':'mu','MEX':'mx','MDA':'md','MNG':'mn','MNE':'me','MSR':'ms',
        'MAR':'ma','MOZ':'mz','MMR':'mm','NAM':'na','NPL':'np','NLD':'nl','NCL':'nc',
        'NZL':'nz','NIC':'ni','NER':'ne','NGA':'ng','MKD':'mk','NIR':'gb','NOR':'no',
        'OMN':'om','PAK':'pk','PSE':'ps','PAN':'pa','PNG':'pg','PRY':'py','PER':'pe',
        'PHL':'ph','POL':'pl','PRT':'pt','PRI':'pr','QAT':'qa','ROU':'ro','RUS':'ru',
        'RWA':'rw','KNA':'kn','LCA':'lc','VCT':'vc','WSM':'ws','SMR':'sm','STP':'st',
        'SAU':'sa','SCT':'gb','SEN':'sn','SRB':'rs','SYC':'sc','SLE':'sl','SGP':'sg',
        'SVK':'sk','SVN':'si','SLB':'sb','SOM':'so','ZAF':'za','SSD':'ss','ESP':'es',
        'LKA':'lk','SDN':'sd','SUR':'sr','SWZ':'sz','SWE':'se','CHE':'ch','SYR':'sy',
        'TWN':'tw','TJK':'tj','TZA':'tz','THA':'th','TLS':'tl','TGO':'tg','TON':'to',
        'TTO':'tt','TUN':'tn','TUR':'tr','TKM':'tm','TCA':'tc','UGA':'ug','UKR':'ua',
        'ARE':'ae','USA':'us','URY':'uy','VIR':'vi','UZB':'uz','VUT':'vu','VEN':'ve',
        'VNM':'vn','WAL':'gb','YEM':'ye','ZMB':'zm','ZWE':'zw','XKX':'xk',
    }
    return mapping.get(iso3, '').lower()

def main():
    print("=== FIFA Ranking Updater ===")
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        countries = json.load(f)
    
    updated = {'men': 0, 'women': 0}
    
    # Update men's rankings
    men = fetch_fifa_men()
    if men:
        for c in countries:
            code = (c.get('country_code') or '').upper()
            # Find matching 3-letter code
            for iso3, rank in men.items():
                if iso3_to_country_code(iso3) == code.lower():
                    c['fifa_ranking'] = rank
                    updated['men'] += 1
                    break
    
    # Update women's rankings
    women = fetch_fifa_women()
    if women:
        for c in countries:
            code = (c.get('country_code') or '').upper()
            for iso3, rank in women.items():
                if iso3_to_country_code(iso3) == code.lower():
                    c['fifa_w'] = rank
                    updated['women'] += 1
                    break
    
    if updated['men'] or updated['women']:
        # Recalculate ranks
        for field in ['fifa_ranking', 'fifa_w']:
            vals = [(i, c.get(field)) for i, c in enumerate(countries) if c.get(field) is not None]
            vals.sort(key=lambda x: x[1])
            for rank, (idx, val) in enumerate(vals, 1):
                countries[idx][field + '_rank'] = rank
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(countries, f, ensure_ascii=False)
        print(f"Saved: {updated['men']} men, {updated['women']} women updated")
        return 0
    else:
        print("No updates — FIFA site may have changed structure")
        return 1

if __name__ == '__main__':
    sys.exit(main())
