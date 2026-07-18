#!/usr/bin/env python3
"""
collect_history.py — Fetch historical World Bank data for ALL available indicators
matching fields in countries.json, going back to 1960.

Expands docs/data/history.json dramatically:
  Old: 19 indicators, 2015-2025 only
  New: ~60 indicators, 1960-present

Strategy:
  1. Map countries.json field names → World Bank indicator codes
  2. Use the 'all' endpoint per indicator (fetches all countries in one go)
  3. Merge into existing history.json (preserves existing data, adds new years/indicators)
  4. Rate-limit: ~1 request per second; use per-page pagination
"""

import json
import time
import sys
import os

# Use requests as specified
try:
    import requests
except ImportError:
    print("⚠ Installing requests...")
    os.system(f"{sys.executable} -m pip install requests --quiet")
    import requests

# ─── Paths ───
REPO = "/mnt/c/Users/mathe/Desktop/rankerage"
HISTORY_FILE = os.path.join(REPO, "docs", "data", "history.json")
COUNTRIES_FILE = os.path.join(REPO, "docs", "data", "countries.json")

# ─── Session with generous timeout ───
session = requests.Session()
session.headers.update({"User-Agent": "RankerageBot/2.0 (collect-history)"})

# ────────────────────────────────────────────────────────
#  COMPREHENSIVE WORLD BANK INDICATOR MAP
#  countries.json field → WB indicator code
#  Fields NOT in WB (happiness, hdi, democracy, press, cpi,
#  gpi, olympic, fifa, cricket, rugby, etc.) are SKIPPED.
# ────────────────────────────────────────────────────────
WB_INDICATORS = {
    # ── Core Demographics ──
    "population":         "SP.POP.TOTL",           # Total population
    "area":               "AG.LND.TOTL.K2",         # Land area (sq km)
    "population_density": "EN.POP.DNST",            # Population density

    # ── Economy ──
    "gdp":                "NY.GDP.MKTP.CD",         # GDP (current US$)
    "gdp_per_capita":     "NY.GDP.PCAP.CD",         # GDP per capita (current US$)
    "gni":                "NY.GNP.MKTP.CD",         # GNI (current US$)
    "gni_per_capita":     "NY.GNP.PCAP.CD",         # GNI per capita

    # ── Trade & Finance ──
    "exports":            "NE.EXP.GNFS.ZS",         # Exports of goods and services (% GDP)
    "imports":            "NE.IMP.GNFS.ZS",         # Imports of goods and services (% GDP)
    "fdi_inflow":         "BX.KLT.DINV.WD.GD.ZS",   # Foreign direct investment, net inflows (% GDP)
    "fdi_outflow":        "BM.KLT.DINV.WD.GD.ZS",   # Foreign direct investment, net outflows (% GDP)
    "trade":              "NE.TRD.GNFS.ZS",         # Trade (% GDP)
    "tax_rev":            "GC.TAX.TOTL.GD.ZS",      # Tax revenue (% GDP)
    "reserves":           "FI.RES.TOTL.CD",         # Total reserves (current US$)
    "debt":               "GC.DOD.TOTL.GD.ZS",      # Central government debt (% GDP)
    "inflation":          "FP.CPI.TOTL.ZG",         # Inflation, consumer prices (annual %)
    "gdp_growth":         "NY.GDP.MKTP.KD.ZG",      # GDP growth (annual %)

    # ── Health ──
    "life_expectancy":    "SP.DYN.LE00.IN",         # Life expectancy at birth (years)
    "fertility":          "SP.DYN.TFRT.IN",         # Fertility rate (births per woman)
    "birth_rate":         "SP.DYN.CBRT.IN",         # Birth rate (per 1000 people)
    "death_rate":         "SP.DYN.CDRT.IN",         # Death rate (per 1000 people)
    "infant_mortality":   "SP.DYN.IMRT.IN",         # Infant mortality (per 1000 live births)
    "maternal_mortality": "SH.STA.MMRT",            # Maternal mortality ratio
    "health":             "SH.XPD.CHEX.GD.ZS",      # Current health expenditure (% GDP)
    "health_per_capita":  "SH.XPD.CHEX.PC.CD",      # Health expenditure per capita
    "obesity":            "SH.STA.OB18.MA.ZS",      # Obesity prevalence (% adults, modeled)
    "smoking":            "SH.PRV.SMOK",            # Smoking prevalence (% adults)
    "alcohol":            "SH.ALC.PCAP.LI",         # Alcohol consumption (liters per capita)
    "diabetes":           "SH.STA.DIAB.ZS",         # Diabetes prevalence (% of population 20-79)
    "hiv_prev":           "SH.DYN.AIDS.ZS",         # HIV prevalence (% of population 15-49)
    "doctors":            "SH.MED.PHYS.ZS",         # Physicians (per 1000 people)
    "nurses":             "SH.MED.NUMW.P3",         # Nurses and midwives (per 1000 people)
    "beds":               "SH.MED.BEDS.ZS",         # Hospital beds (per 1000 people)
    "stunting":           "SH.STA.STNT.ZS",         # Prevalence of stunting (% children under 5)
    "undernourish":       "SN.ITK.DEFC.ZS",         # Prevalence of undernourishment (%)
    "tb_incidence":       "SH.TBS.INCD",            # Incidence of tuberculosis (per 100k people)

    # ── Education ──
    "edu":                "SE.XPD.TOTL.GD.ZS",      # Government expenditure on education (% GDP)
    "literacy":           "SE.ADT.LITR.ZS",         # Literacy rate, adult total (%)
    "primary_enroll":     "SE.PRM.ENRR",            # School enrollment, primary (% gross)
    "secondary_enroll":   "SE.SEC.ENRR",            # School enrollment, secondary (% gross)
    "college_rate":       "SE.TER.ENRR",            # School enrollment, tertiary (% gross)
    "students_per_teacher":"SE.PRM.ENRL.TC.ZS",     # Pupil-teacher ratio, primary

    # ── Technology ──
    "internet_pct":       "IT.NET.USER.ZS",         # Individuals using the Internet (%)
    "mobile_cellular":    "IT.CEL.SETS.P2",         # Mobile cellular subscriptions (per 100)
    "broadband":          "IT.NET.BBND.P2",         # Fixed broadband subscriptions (per 100)
    "patents":            "IP.PAT.NRES",            # Patent applications, nonresidents
    "patents_resident":   "IP.PAT.RESD",            # Patent applications, residents
    "rd":                 "GB.XPD.RSDV.GD.ZS",      # Research and development expenditure (% GDP)
    "electricity":        "EG.USE.ELEC.KH.PC",      # Electric power consumption (kWh per capita)
    "energy_per_capita":  "EG.USE.PCAP.KG.OE",      # Energy use (kg of oil equivalent per capita)
    "fossil_energy":      "EG.USE.COMM.FO.ZS",      # Fossil fuel energy consumption (%)
    "renew":              "EG.FEC.RNEW.ZS",         # Renewable energy consumption (%)
    "elec_access":        "EG.ELC.ACCS.ZS",         # Access to electricity (%)
    "hic_tech_exports":   "TX.VAL.TECH.MF.ZS",      # High-tech exports (% manufactured exports)

    # ── Environment ──
    "co2":                "EN.ATM.CO2E.KT",         # CO2 emissions (kt)
    "co2_per_capita":     "EN.ATM.CO2E.PC",         # CO2 emissions (metric tons per capita)
    "forest":             "AG.LND.FRST.ZS",         # Forest area (% land)
    "pm25":               "EN.ATM.PM25.MC.M3",      # PM2.5 air pollution (mean annual exposure)
    "water_fresh":        "ER.H2O.FWTL.K3",         # Annual freshwater withdrawals
    "arable_land":        "AG.LND.ARBL.ZS",         # Arable land (%)
    "agri_land":          "AG.LND.AGRI.ZS",         # Agricultural land (%)
    "methane":            "EN.ATM.METH.KT.CE",      # Methane emissions (kt)
    "nitrous_oxide":      "EN.ATM.NOXE.KT.CE",      # Nitrous oxide emissions

    # ── Social & Labor ──
    "unemp":              "SL.UEM.TOTL.ZS",         # Unemployment, total (% labor force)
    "unemp_female":       "SL.UEM.TOTL.FE.ZS",      # Unemployment, female (%)
    "unemp_male":         "SL.UEM.TOTL.MA.ZS",      # Unemployment, male (%)
    "unemp_youth":        "SL.UEM.1524.ZS",          # Unemployment, youth total (%)
    "labor_force":        "SL.TLF.TOTL.IN",          # Labor force total
    "labor_female":       "SL.TLF.TOTL.FE.ZS",       # Labor force, female (% total)
    "urban_pop":          "SP.URB.TOTL.IN.ZS",       # Urban population (% total)
    "urban_pop_total":    "SP.URB.TOTL",             # Urban population (total)
    "rural_pop":          "SP.RUR.TOTL",             # Rural population (total)
    "refugees_in":        "SM.POP.REFG",             # Refugee population by country of asylum
    "migrant":            "SM.POP.TOTL",             # International migrant stock, total
    "migrant_pct":        "SM.POP.TOTL.ZS",          # International migrant stock (%)
    "remittances":        "BX.TRF.PWKR.DT.GD.ZS",   # Personal remittances, received (% GDP)
    "union_rate":         "SL.TLF.ACTI.ZS",          # Labor force participation rate

    # ── Military & Crime ──
    "military_pct":       "MS.MIL.XPND.GD.ZS",      # Military expenditure (% GDP)
    "military_expend":    "MS.MIL.XPND.CD",         # Military expenditure (current US$)
    "military_personnel": "MS.MIL.TOTL.P1",         # Armed forces personnel, total
    "arms_imports":       "MS.MIL.MPRT.KD",         # Arms imports (SIPRI trend indicator)
    "murder":             "VC.IHR.PSRC.P5",          # Intentional homicides (per 100k)

    # ── Gender & Governance ──
    "women_parl":         "SG.GEN.PARL.ZS",         # Proportion of seats held by women in parliament (%)
    "teen_pregnancy":     "SP.ADO.TFRT",            # Adolescent fertility rate (births per 1000 women 15-19)
    "child_labor":        "SL.TLF.0714.ZS",          # Children in employment (% of children 7-14)
    "child_marriage":     "SP.M15.2024.FE.ZS",       # Women married by age 15 (%)
    "gender":             "SE.ENR.PRSC.FM.ZS",       # School enrollment primary, gender parity index (GPI)

    # ── Poverty & Inequality ──
    "gini":               "SI.POV.GINI",            # Gini index
    "extreme_poverty":    "SI.POV.DDAY",            # Poverty headcount ratio at $2.15/day (%)
    "poverty_national":   "SI.POV.NAHC",            # Poverty headcount ratio at national poverty lines (%)
    "income_share_10":    "SI.DST.FRST.10",         # Income share held by lowest 10%
    "income_share_20":    "SI.DST.05TH.20",         # Income share held by highest 20%

    # ── Infrastructure ──
    "tourism":            "ST.INT.ARVL",            # International tourism, number of arrivals
    "tourism_receipts":   "ST.INT.RCPT.CD",         # International tourism receipts (current US$)

    # ── Other ──
    "independence":       "NY.GDP.MKTP.CD",          # NOTE: this is a stand-in - we skip it
    # "independence" is year, not a WB indicator, so we handle it below
}

# Fields that are in countries.json but NOT in World Bank API — SKIP these
SKIP_FIELDS = {
    "happiness", "hdi", "hdighdi_adj", "democracy", "press", "cpi", "gpi",
    "olympic", "olympic_gold", "olympic_per_cap", "fifa_ranking", "fifa_w",
    "cricket", "rugby", "basket", "baseball", "nobel", "nobel_per_capita",
    "nobel_science", "fields_medal", "turing", "nuclear", "nuclear_power",
    "nuke_reactors", "solar_power", "wind_power", "chess", "math_olympiad",
    "chem_olympiad", "pisa_math", "pisa_reading", "pisa_science",
    "elevation", "line_length", "tz", "median_age", "independence",
    "corruption", "war_index", "freedom", "heritage",
    # Non-WB social/cultural
    "english", "languages", "religion_div", "race_diversity", "ethnic",
    "divorce", "marriage_rate", "marriage_age_f", "marriage_age_m",
    "leave", "parental_leave", "holidays", "festivals", "gay_marriage",
    "lgbtq_rights", "minority_rights", "gender_gap", "domestic_viol",
    "slavery", "trafficking", "death_penalty", "police", "prison",
    "polit_kill", "police_kill", "assault", "burglary", "drug_offense",
    "gang_violence", "condom_use", "contraception", "sex_education",
    "suicide", "mental_health", "cancer", "disability", "vaccination",
    "antibiotics", "bmi_avg", "height_m", "height_f", "baldness",
    "fast_food", "chocolate", "coffee", "tea_consume", "wine", "beer",
    "meat", "pork_consume", "chicken_consume", "beef_consume",
    "bread_consume", "rice_consume", "organic_food", "food_waste",
    "mcdonalds", "street_food", "bottled_water",
    "gas_price", "car_density", "motorcycle", "e_scooter",
    "aviation", "airports",
    "film_prod", "literature", "books", "libraries", "music",
    "netflix", "game_market",
    "fortune500", "startups", "startup_rate", "unicorns",
    "stock_market", "vc_funding", "crypto_own", "ecommerce",
    "cost_living", "house_price", "min_wage", "salary",
    "tax_burden", "tax_top", "corp_tax", "vat_rate", "pension_rate",
    "insurance", "insurance_cap", "unemp_benefit", "basic_income",
    "ubi_experiment", "welfare_spend", "govern_spend",
    "intangible", "manufacturing",
    "social_media", "penetration", "dating_apps", "onlyfans",
    "porn_search", "sex_frequency", "sex_duration", "adult_films",
    "influencers", "yt_creators",
    "g5_coverage", "netspeed", "ai_adopt", "ai_research",
    "ev_adoption", "e_scooter",
    "passport", "credit_rating", "egov_index", "online_gov",
    "business_ease", "school_yrs", "phd_per_cap", "tertiary",
    "surgeons", "doctors_per_cap", "life_exp_f", "life_exp_m",
    "physicists", "research_pub",
    "michelin", "davis_cup", "worldcup_parts", "marathon_elite",
    "cat_own", "dog_own", "homelessness",
    "strike_days", "workhours",
    "earthquake_count", "earthquakes", "volcanoes", "tsunami_risk",
    "cyclone_freq", "flood_risk", "wildfire_freq", "water_scarcity",
    "drought_risk", "radiation_risk",
    "gold_reserves", "arms_export",
    "parl_age", "cabinet_age", "leader_age", "youngest_leader",
    "trump_approval", "approval",
    "plastic_waste", "recycling",
    "immigration", "emigration", "displaced_from",
    "space_launch", "peacekeeping",
    "news_age", "news_title", "news_url", "news_source", "news_score",
    "news_columns", "news_image", "election_days", "election_date",
    "election_rank",
}

# Ensure SKIP_FIELDS don't overlap with WB_INDICATORS
for f in SKIP_FIELDS:
    WB_INDICATORS.pop(f, None)

# Fields we know exist in WB but map poorly to countries.json fields
# We skip 'independence' (it's a year value, not a WB indicator)
WB_INDICATORS.pop("independence", None)

# All rank suffixes
UNWANTED_SUFFIXES = ("_rank", "_desc")


def load_history():
    """Load existing history, or create empty if missing."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history):
    """Save history atomically with backup."""
    import shutil
    tmp = HISTORY_FILE + ".tmp"
    bak = HISTORY_FILE + ".bak"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        # Backup existing
        if os.path.exists(HISTORY_FILE):
            shutil.copy2(HISTORY_FILE, bak)
        os.replace(tmp, HISTORY_FILE)
        if os.path.exists(bak):
            os.remove(bak)
    except Exception as e:
        print(f"  ⚠️ save_history error: {e}", flush=True)
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def build_iso_mapping():
    """
    Fetch World Bank country list to build ISO2→ISO3 mapping.
    Also returns the set of valid WB country ISO3 codes (not aggregates).
    """
    print("🌐 Fetching World Bank country code mapping...")
    iso2_to_iso3 = {}
    wb_valid_iso3s = set()

    try:
        resp = session.get(
            "https://api.worldbank.org/v2/country?format=json&per_page=300",
            timeout=90,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ⚠ Could not fetch WB country list: {e}")
        print("  ⚠ Using embedded fallback mapping...")
        return FALLBACK_ISO_MAP, set(FALLBACK_ISO_MAP.values())

    if not data or len(data) < 2:
        print("  ⚠ Unexpected WB response, using fallback mapping")
        return FALLBACK_ISO_MAP, set(FALLBACK_ISO_MAP.values())

    for entry in data[1]:
        iso2 = (entry.get("iso2Code") or "").strip()
        iso3 = (entry.get("id") or "").strip()
        region_id = (entry.get("region") or {}).get("id", "")

        # Only actual countries (not aggregates like "WLD", "EAS", etc.)
        if region_id != "NA" and iso3 and len(iso3) == 3 and not iso3[0] == "X":
            wb_valid_iso3s.add(iso3)
            if iso2:
                iso2_to_iso3[iso2] = iso3

    print(f"  {len(wb_valid_iso3s)} valid WB country codes, {len(iso2_to_iso3)} ISO2→ISO3 mappings")
    return iso2_to_iso3, wb_valid_iso3s


def get_country_iso2_list():
    """Extract all unique ISO2 country codes from countries.json."""
    with open(COUNTRIES_FILE, "r", encoding="utf-8") as f:
        countries = json.load(f)

    iso2_set = set()
    for c in countries:
        cc = (c.get("country_code") or "").strip().upper()
        if cc:
            iso2_set.add(cc)

    return sorted(iso2_set)


def fetch_indicator_history(wb_code):
    """
    Fetch ALL historical data for a WB indicator using the 'all' endpoint.
    Returns dict: {iso3_code: {year_str: value}}
    Paginates through all pages; no date filter = gets all years (back to 1960).
    """
    data = {}
    page = 1

    while True:
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/{wb_code}"
            f"?format=json&per_page=20000&page={page}"
        )
        try:
            resp = session.get(url, timeout=120)
            resp.raise_for_status()
            raw = resp.json()
        except Exception as e:
            sys.stderr.write(f"    [WARN] Page {page} fetch error: {e}\n")
            break

        if not raw or len(raw) < 2:
            break

        entries = raw[1]
        if not entries:
            break

        for entry in entries:
            val = entry.get("value")
            if val is None:
                continue
            iso3 = entry.get("countryiso3code", "")
            year = entry.get("date", "")
            if iso3 and year:
                if iso3 not in data:
                    data[iso3] = {}
                data[iso3][year] = val

        total_pages = raw[0].get("pages", 1)
        if page >= total_pages:
            break

        page += 1
        # Small delay between pages (generous per_page keeps pages low)
        time.sleep(0.3)

    return data


def merge_history(existing, new_data, indicator, iso3_to_iso2):
    """
    Merge new WB data into history dict.
    new_data: {iso3_code: {year_str: value}}
    existing: full history dict
    Converts ISO3 → ISO2 for storage.
    """
    if indicator not in existing:
        existing[indicator] = {}

    added_countries = 0
    added_years = 0

    for iso3, year_data in new_data.items():
        iso2 = iso3_to_iso2.get(iso3)
        if not iso2:
            continue

        if iso2 not in existing[indicator]:
            existing[indicator][iso2] = {}
            added_countries += 1

        existing_country_data = existing[indicator][iso2]
        for year, val in year_data.items():
            if year not in existing_country_data:
                existing_country_data[year] = val
                added_years += 1
            # If year exists, keep existing value (don't overwrite newer data)

    return added_countries, added_years


# ─── Fallback ISO2→ISO3 mapping (used if WB API is unreachable) ───
FALLBACK_ISO_MAP = {
    "AF": "AFG", "AL": "ALB", "DZ": "DZA", "AD": "AND", "AO": "AGO",
    "AG": "ATG", "AR": "ARG", "AM": "ARM", "AU": "AUS", "AT": "AUT",
    "AZ": "AZE", "BS": "BHS", "BH": "BHR", "BD": "BGD", "BB": "BRB",
    "BY": "BLR", "BE": "BEL", "BZ": "BLZ", "BJ": "BEN", "BT": "BTN",
    "BO": "BOL", "BA": "BIH", "BW": "BWA", "BR": "BRA", "BN": "BRN",
    "BG": "BGR", "BF": "BFA", "BI": "BDI", "CV": "CPV", "KH": "KHM",
    "CM": "CMR", "CA": "CAN", "CF": "CAF", "TD": "TCD", "CL": "CHL",
    "CN": "CHN", "CO": "COL", "KM": "COM", "CG": "COG", "CD": "COD",
    "CR": "CRI", "CI": "CIV", "HR": "HRV", "CU": "CUB", "CY": "CYP",
    "CZ": "CZE", "DK": "DNK", "DJ": "DJI", "DM": "DMA", "DO": "DOM",
    "EC": "ECU", "EG": "EGY", "SV": "SLV", "GQ": "GNQ", "ER": "ERI",
    "EE": "EST", "SZ": "SWZ", "ET": "ETH", "FJ": "FJI", "FI": "FIN",
    "FR": "FRA", "GA": "GAB", "GM": "GMB", "GE": "GEO", "DE": "DEU",
    "GH": "GHA", "GR": "GRC", "GD": "GRD", "GT": "GTM", "GN": "GIN",
    "GW": "GNB", "GY": "GUY", "HT": "HTI", "HN": "HND", "HU": "HUN",
    "IS": "ISL", "IN": "IND", "ID": "IDN", "IR": "IRN", "IQ": "IRQ",
    "IE": "IRL", "IL": "ISR", "IT": "ITA", "JM": "JAM", "JP": "JPN",
    "JO": "JOR", "KZ": "KAZ", "KE": "KEN", "KI": "KIR", "KP": "PRK",
    "KR": "KOR", "KW": "KWT", "KG": "KGZ", "LA": "LAO", "LV": "LVA",
    "LB": "LBN", "LS": "LSO", "LR": "LBR", "LY": "LBY", "LI": "LIE",
    "LT": "LTU", "LU": "LUX", "MG": "MDG", "MW": "MWI", "MY": "MYS",
    "MV": "MDV", "ML": "MLI", "MT": "MLT", "MH": "MHL", "MR": "MRT",
    "MU": "MUS", "MX": "MEX", "FM": "FSM", "MD": "MDA", "MC": "MCO",
    "MN": "MNG", "ME": "MNE", "MA": "MAR", "MZ": "MOZ", "MM": "MMR",
    "NA": "NAM", "NR": "NRU", "NP": "NPL", "NL": "NLD", "NZ": "NZL",
    "NI": "NIC", "NE": "NER", "NG": "NGA", "MK": "MKD", "NO": "NOR",
    "OM": "OMN", "PK": "PAK", "PW": "PLW", "PA": "PAN", "PG": "PNG",
    "PY": "PRY", "PE": "PER", "PH": "PHL", "PL": "POL", "PT": "PRT",
    "QA": "QAT", "RO": "ROU", "RU": "RUS", "RW": "RWA", "KN": "KNA",
    "LC": "LCA", "VC": "VCT", "WS": "WSM", "SM": "SMR", "ST": "STP",
    "SA": "SAU", "SN": "SEN", "RS": "SRB", "SC": "SYC", "SL": "SLE",
    "SG": "SGP", "SK": "SVK", "SI": "SVN", "SB": "SLB", "SO": "SOM",
    "ZA": "ZAF", "SS": "SSD", "ES": "ESP", "LK": "LKA", "SD": "SDN",
    "SR": "SUR", "SE": "SWE", "CH": "CHE", "SY": "SYR", "TW": "TWN",
    "TJ": "TJK", "TZ": "TZA", "TH": "THA", "TL": "TLS", "TG": "TGO",
    "TO": "TON", "TT": "TTO", "TN": "TUN", "TR": "TUR", "TM": "TKM",
    "TV": "TUV", "UG": "UGA", "UA": "UKR", "AE": "ARE", "GB": "GBR",
    "US": "USA", "UY": "URY", "UZ": "UZB", "VU": "VUT", "VA": "VAT",
    "VE": "VEN", "VN": "VNM", "YE": "YEM", "ZM": "ZMB", "ZW": "ZWE",
    "HK": "HKG", "XK": "XKX", "PS": "PSE", "PR": "PRI", "MO": "MAC",
    "FO": "FRO", "GL": "GRL", "BM": "BMU", "KY": "CYM", "GI": "GIB",
    "NC": "NCL", "PF": "PYF", "VI": "VIR", "GU": "GUM", "MP": "MNP",
    "AS": "ASM", "CK": "COK", "NU": "NIU", "TK": "TKL", "WF": "WLF",
    "AI": "AIA", "MS": "MSR", "TC": "TCA", "VG": "VGB", "FK": "FLK",
    "PN": "PCN", "SH": "SHN", "PM": "SPM", "AW": "ABW", "CW": "CUW",
    "SX": "SXM", "BQ": "BES", "BL": "BLM", "MF": "MAF", "AX": "ALA",
    "IM": "IMN", "JE": "JEY", "GG": "GGY", "YT": "MYT", "RE": "REU",
    "GP": "GLP", "MQ": "MTQ", "GF": "GUF", "EH": "ESH", "IO": "IOT",
    "CX": "CXR", "CC": "CCK", "NF": "NFK", "AQ": "ATA", "BV": "BVT",
    "HM": "HMD", "TF": "ATF", "GS": "SGS", "UM": "UMI",
}


def main():
    print("=" * 70)
    print("  📊 COLLECT HISTORY — World Bank Historical Data Fetcher")
    print("  Target: ALL indicators from 1960 to present")
    print("=" * 70)

    # ── Load existing history ──
    print("\n📂 Loading existing history.json...")
    history = load_history()
    existing_indicators = set(history.keys())
    print(f"   {len(existing_indicators)} existing indicators")

    # How many total country-year data points?
    existing_points = sum(
        sum(len(years) for years in country_data.values())
        for country_data in history.values()
    )
    print(f"   {existing_points} existing country-year data points")

    # ── Build ISO mapping ──
    print()
    iso2_to_iso3, wb_valid_iso3s = build_iso_mapping()

    # Reverse mapping: ISO3→ISO2
    iso3_to_iso2 = {v: k for k, v in iso2_to_iso3.items()}

    # ── Determine which indicators to fetch ──
    all_indicators = list(WB_INDICATORS.items())
    new_only = [(f, c) for f, c in all_indicators if f not in existing_indicators]
    existing_to_update = [(f, c) for f, c in all_indicators if f in existing_indicators]

    print(f"\n📋 Indicator plan:")
    print(f"   Total WB indicators:    {len(all_indicators)}")
    print(f"   New (not in history):   {len(new_only)}")
    print(f"   Existing (add years):   {len(existing_to_update)}")
    print(f"   Skipped (non-WB):       {len(SKIP_FIELDS)}")

    # ── Process: NEW indicators first (most valuable) ──
    fetch_order = new_only + existing_to_update

    print(f"\n🚀 Starting fetch of {len(fetch_order)} indicators...")
    print(f"   Rate limit: ~1 request/second")
    print(f"   Expected runtime: {len(fetch_order) * 5:.0f}-{len(fetch_order) * 10:.0f} seconds")
    print("=" * 70)

    total_new_years = 0
    total_new_countries = 0
    start_time = time.time()

    for idx, (field, wb_code) in enumerate(fetch_order, 1):
        t_start = time.time()

        # Status indicator
        status = "🆕" if field not in existing_indicators else "📝"
        print(f"\n  [{idx:3d}/{len(fetch_order)}] {status} {field}  ({wb_code})")
        sys.stdout.flush()

        try:
            raw_data = fetch_indicator_history(wb_code)
        except Exception as e:
            print(f"    ❌ Fetch failed: {e}")
            continue

        # Filter to only valid country codes
        filtered = {
            k: v for k, v in raw_data.items()
            if k in wb_valid_iso3s
        }

        # Merge into history
        added_c, added_y = merge_history(history, filtered, field, iso3_to_iso2)
        total_new_countries += added_c
        total_new_years += added_y

        elapsed = time.time() - t_start

        # Count total countries and years for this indicator now
        total_countries = len(history.get(field, {}))
        total_ind_years = sum(
            len(yd) for yd in history.get(field, {}).values()
        )

        print(f"    ← WB returned {len(raw_data)} country-entries ({len(filtered)} real countries)")
        print(f"    ← Added {added_c} new countries, {added_y} new years")
        print(f"    ← Now: {total_countries} countries, {total_ind_years} years  ({elapsed:.1f}s)")

        # Save checkpoint every 5 indicators
        if idx % 5 == 0:
            save_history(history)
            elapsed_total = time.time() - start_time
            total_points = sum(
                sum(len(years) for years in country_data.values())
                for country_data in history.values()
            )
            print(f"  💾 Checkpoint saved ({total_points} total data points, {elapsed_total:.0f}s elapsed)")

        # Rate limiting
        time.sleep(1.0)

    # ── Final save ──
    save_history(history)

    # ── Summary ──
    total_time = time.time() - start_time
    final_indicators = len(history)
    final_points = sum(
        sum(len(years) for years in country_data.values())
        for country_data in history.values()
    )

    # Per-indicator stats
    print("\n" + "=" * 70)
    print("  📊 FINAL SUMMARY")
    print("=" * 70)
    print(f"  Runtime:              {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Indicators:           {existing_indicators} → {final_indicators} (+{final_indicators - len(existing_indicators)})")
    print(f"  Total data points:    {existing_points} → {final_points} (+{final_points - existing_points})")
    print(f"  New countries added:  {total_new_countries}")
    print(f"  New years added:      {total_new_years}")
    print(f"  Saved to:             {HISTORY_FILE}")

    # File size
    fsize_mb = os.path.getsize(HISTORY_FILE) / (1024 * 1024)
    print(f"  File size:            {fsize_mb:.1f} MB")

    # Top 10 indicators by data points
    print("\n  📈 Top indicators by data points:")
    indicator_sizes = []
    for ind, data in history.items():
        pts = sum(len(yd) for yd in data.values())
        n_countries = len(data)
        years_set = set()
        for yd in data.values():
            years_set.update(yd.keys())
        years_span = f"{min(years_set)}-{max(years_set)}" if years_set else "none"
        indicator_sizes.append((pts, n_countries, years_span, ind))
    indicator_sizes.sort(reverse=True)

    for pts, n_ctry, yspan, ind in indicator_sizes[:15]:
        marker = " 🆕" if ind not in existing_indicators else ""
        print(f"    {ind:28s} {pts:6d} pts  {n_ctry:4d} countries  {yspan}{marker}")

    # Per-country stats
    all_countries_data = {}
    for ind, data in history.items():
        for cc in data:
            if cc not in all_countries_data:
                all_countries_data[cc] = {"indicators": 0, "years": 0}
            all_countries_data[cc]["indicators"] += 1
            all_countries_data[cc]["years"] += len(data[cc])

    countries_with_data = len(all_countries_data)
    avg_indicators = sum(d["indicators"] for d in all_countries_data.values()) / max(countries_with_data, 1)
    avg_years = sum(d["years"] for d in all_countries_data.values()) / max(countries_with_data, 1)

    print(f"\n  🌍 Country coverage:")
    print(f"    {countries_with_data} countries with at least one data point")
    print(f"    Average {avg_indicators:.0f} indicators per country")
    print(f"    Average {avg_years:.0f} year-points per country")

    print("\n✅ DONE!")


if __name__ == "__main__":
    main()
