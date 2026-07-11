#!/usr/bin/env python3
"""Fetch latest World Bank data for historical trends"""
import json, urllib.request, time

INDICATORS = {
    "gdp": "NY.GDP.MKTP.CD", "gdp_per_capita": "NY.GDP.PCAP.CD",
    "population": "SP.POP.TOTL", "life_expectancy": "SP.DYN.LE00.IN",
    "urban_pop": "SP.URB.TOTL.IN.ZS", "internet_pct": "IT.NET.USER.ZS",
    "military_pct": "MS.MIL.XPND.GD.ZS", "health": "SH.XPD.CHEX.GD.ZS",
    "fertility": "SP.DYN.TFRT.IN", "forest": "AG.LND.FRST.ZS",
    "edu": "SE.PRM.ENRR", "rd": "GB.XPD.RSDV.GD.ZS",
    "poverty": "SI.POV.GINI",
    "exports": "NE.EXP.GNFS.ZS", "imports": "NE.IMP.GNFS.ZS",
    "electricity": "EG.USE.ELEC.KH.PC", "energy_per_capita": "EG.USE.PCAP.KG.OE",
    "birth_rate": "SP.DYN.CBRT.IN", "death_rate": "SP.DYN.CDRT.IN",
    "infant_mortality": "SP.DYN.IMRT.IN",
}

# ISO 2→3 mapping
CODE_MAP = {
    "AF":"AFG","AL":"ALB","DZ":"DZA","AO":"AGO","AR":"ARG","AM":"ARM","AU":"AUS","AT":"AUT","AZ":"AZE",
    "BH":"BHR","BD":"BGD","BY":"BLR","BE":"BEL","BZ":"BLZ","BJ":"BEN","BT":"BTN","BO":"BOL","BA":"BIH",
    "BW":"BWA","BR":"BRA","BN":"BRN","BG":"BGR","BF":"BFA","BI":"BDI","KH":"KHM","CM":"CMR","CA":"CAN",
    "CV":"CPV","CF":"CAF","TD":"TCD","CL":"CHL","CN":"CHN","CO":"COL","KM":"COM","CG":"COG","CD":"COD",
    "CR":"CRI","CI":"CIV","HR":"HRV","CU":"CUB","CY":"CYP","CZ":"CZE","DK":"DNK","DJ":"DJI","DO":"DOM",
    "EC":"ECU","EG":"EGY","SV":"SLV","GQ":"GNQ","ER":"ERI","EE":"EST","ET":"ETH","FJ":"FJI","FI":"FIN",
    "FR":"FRA","GA":"GAB","GM":"GMB","GE":"GEO","DE":"DEU","GH":"GHA","GR":"GRC","GT":"GTM","GN":"GIN",
    "GW":"GNB","GY":"GUY","HT":"HTI","HN":"HND","HU":"HUN","IS":"ISL","IN":"IND","ID":"IDN","IR":"IRN",
    "IQ":"IRQ","IE":"IRL","IL":"ISR","IT":"ITA","JM":"JAM","JP":"JPN","JO":"JOR","KZ":"KAZ","KE":"KEN",
    "KI":"KIR","KP":"PRK","KR":"KOR","KW":"KWT","KG":"KGZ","LA":"LAO","LV":"LVA","LB":"LBN","LS":"LSO",
    "LR":"LBR","LY":"LBY","LT":"LTU","LU":"LUX","MG":"MDG","MW":"MWI","MY":"MYS","MV":"MDV","ML":"MLI",
    "MT":"MLT","MH":"MHL","MR":"MRT","MU":"MUS","MX":"MEX","FM":"FSM","MD":"MDA","MC":"MCO","MN":"MNG",
    "ME":"MNE","MA":"MAR","MZ":"MOZ","MM":"MMR","NA":"NAM","NR":"NRU","NP":"NPL","NL":"NLD","NZ":"NZL",
    "NI":"NIC","NE":"NER","NG":"NGA","MK":"MKD","NO":"NOR","OM":"OMN","PK":"PAK","PW":"PLW","PA":"PAN",
    "PG":"PNG","PY":"PRY","PE":"PER","PH":"PHL","PL":"POL","PT":"PRT","QA":"QAT","RO":"ROU","RU":"RUS",
    "RW":"RWA","KN":"KNA","LC":"LCA","VC":"VCT","WS":"WSM","SM":"SMR","ST":"STP","SA":"SAU","SN":"SEN",
    "RS":"SRB","SC":"SYC","SL":"SLE","SG":"SGP","SK":"SVK","SI":"SVN","SB":"SLB","SO":"SOM","ZA":"ZAF",
    "SS":"SSD","ES":"ESP","LK":"LKA","SD":"SDN","SR":"SUR","SE":"SWE","CH":"CHE","SY":"SYR","TW":"TWN",
    "TJ":"TJK","TZ":"TZA","TH":"THA","TL":"TLS","TG":"TGO","TO":"TON","TT":"TTO","TN":"TUN","TR":"TUR",
    "TM":"TKM","TV":"TUV","UG":"UGA","UA":"UKR","AE":"ARE","GB":"GBR","US":"USA","UY":"URY","UZ":"UZB",
    "VU":"VUT","VE":"VEN","VN":"VNM","YE":"YEM","ZM":"ZMB","ZW":"ZWE","HK":"HKG","XK":"XKX"
}
ISO3_TO_2 = {v:k for k,v in CODE_MAP.items()}

# Load existing history
with open("docs/data/history.json") as f:
    history = json.load(f)

updated = 0
for field, wb_code in INDICATORS.items():
    print(f"Fetching {field}...", end=" ")
    field_data = {}
    try:
        page = 1
        while True:
            url = f"https://api.worldbank.org/v2/country/all/indicator/{wb_code}?format=json&per_page=500&date=2015:2025&page={page}"
            req = urllib.request.Request(url, headers={'User-Agent': 'RankerageBot/1.0'})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            if not data or len(data) < 2: break
            for entry in data[1]:
                iso3 = entry.get('countryiso3code','')
                year = entry.get('date','')
                val = entry.get('value')
                if val is not None and iso3 and iso3 in ISO3_TO_2:
                    code2 = ISO3_TO_2[iso3]
                    if code2 not in field_data: field_data[code2] = {}
                    field_data[code2][year] = val
            total_pages = data[0].get('pages', 1)
            if page >= total_pages: break
            page += 1
            time.sleep(0.3)
        if len(field_data) > 10:
            history[field] = field_data
            updated += 1
        print(f"{len(field_data)} countries")
    except Exception as e:
        print(f"Error: {e}")

with open("docs/data/history.json", 'w') as f:
    json.dump(history, f, ensure_ascii=False)

print(f"\nUpdated {updated}/{len(INDICATORS)} indicators")
