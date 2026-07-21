#!/usr/bin/env python3
"""Update FIFA rankings in countries.json — run weekly via cron

Uses FIFA's internal ranking-overview API:
- Men's: id-format date IDs (e.g., id15136)
- Women's: ranking_YYYYMMDD format (e.g., ranking_20260616)
"""

import json
import sys
import urllib.request
import re
import os
import time

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'data', 'countries.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Origin': 'https://inside.fifa.com',
    'Referer': 'https://inside.fifa.com/fifa-world-ranking/men',
}


def fetch_ssr_dates(gender='men'):
    """Fetch the SSR page data to get available ranking dates."""
    url = f'https://inside.fifa.com/fifa-world-ranking/{gender}'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Failed to fetch {gender} page: {e}")
        return []

    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        s = s.strip()
        if len(s) > 100000 and s.startswith('{'):
            data = json.loads(s)
            ranking = data['props']['pageProps']['pageData']['ranking']
            return ranking.get('allAvailableDates', [])
    return []


def fetch_ranking_api(date_id, timeout=30):
    """Fetch rankings from the ranking-overview API."""
    url = f'https://inside.fifa.com/api/ranking-overview?dateId={date_id}'
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
            rankings = data.get('rankings', [])
            if rankings:
                result = {}
                for r in rankings:
                    item = r.get('rankingItem', {})
                    code = item.get('countryCode', '').upper()
                    rank = item.get('rank')
                    if code and rank is not None:
                        result[code] = rank
                return result
    except Exception as e:
        print(f"  API call failed for {date_id}: {e}")
    return {}


def find_latest_men_id():
    """Find the latest working id-format ID for men's rankings."""
    # Start from a known recent ID and scan upward
    # Known: id15136 was June 11, 2026 (latest at time of writing)
    known_recent = 15136
    scan_up_to = known_recent + 200  # Look up to 200 IDs ahead

    last_working = known_recent
    last_date = None

    for i in range(known_recent, scan_up_to):
        date_id = f'id{i}'
        try:
            url = f'https://inside.fifa.com/api/ranking-overview?dateId={date_id}'
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Origin': 'https://inside.fifa.com',
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = resp.read().decode()
                if len(data) > 100:
                    d = json.loads(data)
                    rankings = d.get('rankings', [])
                    if rankings:
                        last_working = i
                        last_date = rankings[0].get('lastUpdateDate', '')
        except Exception:
            pass
        time.sleep(0.03)

    if last_date:
        print(f"  Latest men's ID: id{last_working} ({last_date})")
    return f'id{last_working}'


def find_latest_women_id():
    """Find the latest working ID for women's rankings using ranking_YYYYMMDD format."""
    dates = fetch_ssr_dates('women')
    if not dates:
        print("  Could not fetch women's SSR dates")
        return None

    # Try IDs from newest to oldest, looking for the ranking_YYYYMMDD format that works
    for d in dates:
        date_str = d.get('date', '')
        if date_str:
            # Convert YYYY-MM-DD to ranking_YYYYMMDD
            date_id = 'ranking_' + date_str.replace('-', '')
            rankings = fetch_ranking_api(date_id, timeout=10)
            if rankings:
                print(f"  Latest women's ID: {date_id} ({date_str})")
                return date_id

    # Fallback: try the latest date's ranking_ format
    if dates:
        latest = dates[0]
        date_str = latest.get('date', '')
        date_id = 'ranking_' + date_str.replace('-', '')
        rankings = fetch_ranking_api(date_id, timeout=10)
        if rankings:
            return date_id

    print("  No working women's ranking ID found")
    return None


def iso3_to_country_code(iso3):
    """Convert 3-letter ISO to 2-letter country code (unused with new API, kept for reference)."""
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

    # Load existing data
    if not os.path.exists(DATA_FILE):
        print(f"ERROR: Data file not found: {DATA_FILE}")
        return 1

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        countries = json.load(f)

    updated = {'men': 0, 'women': 0}

    # The API returns 3-letter ISO codes; convert to 2-letter for matching
    def build_iso3_index(rankings):
        """Build a lookup from 2-letter country code to rank."""
        result = {}
        for iso3, rank in rankings.items():
            cc2 = iso3_to_country_code(iso3)
            if cc2:
                result[cc2] = rank
        return result

    # --- Update men's rankings ---
    print("\n--- Men's Rankings ---")
    men_id = find_latest_men_id()
    if men_id:
        men_rankings = fetch_ranking_api(men_id)
        if men_rankings:
            print(f"  Fetched {len(men_rankings)} men's rankings from API")
            men_by_cc2 = build_iso3_index(men_rankings)
            for c in countries:
                code = (c.get('country_code') or '').lower()
                if code in men_by_cc2:
                    c['fifa_ranking'] = men_by_cc2[code]
                    updated['men'] += 1
        else:
            print("  Failed to fetch men's rankings from API")
    else:
        print("  Could not determine latest men's ranking ID")

    # --- Update women's rankings ---
    print("\n--- Women's Rankings ---")
    women_id = find_latest_women_id()
    if women_id:
        women_rankings = fetch_ranking_api(women_id)
        if women_rankings:
            print(f"  Fetched {len(women_rankings)} women's rankings from API")
            women_by_cc2 = build_iso3_index(women_rankings)
            for c in countries:
                code = (c.get('country_code') or '').lower()
                if code in women_by_cc2:
                    c['fifa_w'] = women_by_cc2[code]
                    updated['women'] += 1
        else:
            print("  Failed to fetch women's rankings from API")
    else:
        print("  Could not determine latest women's ranking ID")

    # --- Save ---
    if updated['men'] or updated['women']:
        # Recalculate ordinal ranks
        for field in ['fifa_ranking', 'fifa_w']:
            vals = [(i, c.get(field)) for i, c in enumerate(countries) if c.get(field) is not None]
            vals.sort(key=lambda x: x[1])
            for rank, (idx, val) in enumerate(vals, 1):
                countries[idx][field + '_rank'] = rank

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(countries, f, ensure_ascii=False)
        print(f"\nSaved: {updated['men']} men, {updated['women']} women updated")
        return 0
    else:
        print("\nNo rankings were updated — scraping failed for both men and women")
        return 1


if __name__ == '__main__':
    sys.exit(main())
