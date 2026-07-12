#!/usr/bin/env python3
"""gen_search_data.py — 모든 지표에 대한 검색 alias + 클러스터 생성"""
import json, re

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"

with open(f"{REPO}/docs/data/countries.json") as f:
    countries = json.load(f)
with open(f"{REPO}/docs/data/descriptions.json") as f:
    desc = json.load(f)
with open(f"{REPO}/docs/js/table.js") as f:
    js = f.read()

all_fields = sorted(k for k in countries[0].keys()
    if not k.endswith("_rank")
    and k not in ("flag","country_summary","country_code","country_name_en",
        "country_name_local","capital_en","capital_local","continent",
        "subcontinent","ethnic","head_of_state_en","head_of_state_local",
        "lat","lon","national_anthem_en","national_anthem_local",
        "election_date","brics_member","brics_year","oecd_member","oecd_year"))

# Korean translations (English field name + desc as fallback)
KO = {
    "agri":"농업 농경지", "airports":"공항", "ai_research":"AI 인공지능", "alcohol":"술 알코올 음주",
    "antibiotics":"항생제", "approval":"지지율 대통령", "area":"면적 국토 크기",
    "arms_export":"무기수출", "asean_member":"ASEAN 아세안", "apec_member":"APEC 아펙",
    "assault":"폭행", "aviation":"항공 비행기", "baldness":"대머리 탈모",
    "baseball":"야구", "basic_income":"기본소득", "beds":"병상 병원",
    "beef_consume":"소고기", "beer":"맥주", "birth_rate":"출생률 출산",
    "bmi_avg":"BMI 체질량", "books":"도서 책", "bottled_water":"생수",
    "bread_consume":"빵", "brics_member":"BRICS 브릭스", "burglary":"절도 도둑",
    "business_ease":"비즈니스 창업", "cabinet_age":"내각연령",
    "cancer":"암", "car_density":"자동차 차량", "cat_own":"고양이",
    "chess":"체스", "chicken_consume":"닭고기", "child_labor":"아동노동",
    "child_marriage":"조혼", "chocolate":"초콜릿", "co2":"탄소배출 CO2",
    "coffee":"커피", "college_rate":"대학진학률", "condom_use":"콘돔",
    "contraception":"피임", "corp_tax":"법인세", "cost_living":"생활비 물가",
    "cpi":"부패지수 CPI 청렴", "credit_rating":"신용등급", "cricket":"크리켓",
    "crypto_own":"암호화폐 가상화폐", "cyclone_freq":"사이클론 태풍",
    "dating_apps":"데이팅앱", "davis_cup":"데이비스컵 테니스",
    "death_penalty":"사형", "death_rate":"사망률", "debt":"부채 정부부채",
    "democracy":"민주주의", "diabetes":"당뇨병", "disability":"장애인",
    "divorce":"이혼", "doctors":"의사", "dog_own":"개",
    "domestic_viol":"가정폭력", "drug_offense":"마약",
    "earthquake_count":"지진횟수", "earthquakes":"지진",
    "ecommerce":"전자상거래", "edu":"교육", "egov_index":"전자정부",
    "electricity":"전력 전기", "elevation":"고도 해발",
    "emigration":"해외이주", "energy_per_capita":"에너지소비",
    "english":"영어", "eu_member":"EU 유럽연합",
    "ev_adoption":"전기차", "exports":"수출", "extreme_poverty":"극빈곤",
    "fast_food":"패스트푸드", "fertility":"출산율", "festivals":"축제",
    "fields_medal":"필즈상 수학", "fifa_ranking":"FIFA 축구",
    "fifa_w":"여자축구 FIFA", "film_prod":"영화",
    "flood_risk":"홍수", "food_waste":"음식물쓰레기",
    "forest":"산림 숲", "fortune500":"포춘500 기업",
    "freedom":"자유 민주", "g20_member":"G20",
    "g5_coverage":"5G", "g7_member":"G7",
    "game_market":"게임시장", "gang_violence":"갱 폭력",
    "gas_price":"휘발유 기름값", "gay_marriage":"동성결혼",
    "gdp":"GDP 경제", "gdp_per_capita":"1인당GDP 소득",
    "gender":"성평등 젠더", "gender_gap":"성별격차 임금",
    "gini":"지니계수 불평등", "gold_reserves":"금보유고",
    "govern_spend":"정부지출", "gpi":"평화지수",
    "happiness":"행복 웰빙", "hdi":"HDI 인간개발",
    "hdi_adj":"HDI조정", "health":"의료비 건강",
    "height_f":"여성키", "height_m":"남성키",
    "heritage":"유네스코 세계유산", "hiv_prev":"HIV 에이즈",
    "holidays":"공휴일", "homelessness":"노숙자",
    "house_price":"주택가격 집값", "immigration":"이민 이주",
    "imports":"수입", "infant_mortality":"영아사망률",
    "inflation":"인플레이션 물가", "influencers":"인플루언서",
    "insurance":"보험", "intangible":"무형문화재",
    "internet_pct":"인터넷", "languages":"언어",
    "leader_age":"지도자연령", "leave":"휴가",
    "lgbtq_rights":"LGBTQ 성소수자", "libraries":"도서관",
    "life_expectancy":"기대수명 수명", "line_length":"철도",
    "literacy":"문해율", "literature":"문학",
    "manufacturing":"제조업", "marathon_elite":"마라톤",
    "marriage_age_f":"여성초혼", "marriage_age_m":"남성초혼",
    "marriage_rate":"혼인율", "maternal_mortality":"산모사망",
    "math_olympiad":"수학올림피아드", "mcdonalds":"맥도날드",
    "meat":"육류 고기", "med_tourism":"의료관광",
    "median_age":"중위연령", "mental_health":"정신건강",
    "michelin":"미쉐린 레스토랑", "military_pct":"군사비 국방비",
    "military_personnel":"군인", "min_wage":"최저임금",
    "minority_rights":"소수자인권", "motorcycle":"오토바이",
    "murder":"살인율", "nato_year":"NATO 나토",
    "netspeed":"인터넷속도", "nobel":"노벨상",
    "nobel_per_capita":"1인당노벨상", "nuclear":"핵무기",
    "nuclear_power":"원자력 원전", "nuke_reactors":"원자로",
    "nurses":"간호사", "obesity":"비만",
    "oecd_member_order":"OECD 가입순서",
    "olympic":"올림픽", "olympic_gold":"올림픽금메달",
    "olympic_per_cap":"인구대비올림픽",
    "online_gov":"온라인정부", "onlyfans":"온리팬스",
    "organic_food":"유기농", "parental_leave":"육아휴직",
    "park_area":"공원", "parl_age":"의원연령",
    "passport":"여권", "patents":"특허",
    "peacekeeping":"평화유지군", "penetration":"소셜미디어",
    "pension_rate":"연금", "phd_per_cap":"박사학위",
    "physicists":"물리학자", "pisa_math":"PISA수학",
    "pisa_reading":"PISA독서", "pisa_science":"PISA과학",
    "plastic_waste":"플라스틱쓰레기", "pm25":"미세먼지 초미세먼지",
    "police":"경찰", "polit_kill":"정치적살인",
    "population":"인구", "population_density":"인구밀도",
    "pork_consume":"돼지고기", "porn_search":"포르노검색",
    "poverty":"빈곤율", "poverty_gap":"빈곤격차",
    "press":"언론자유", "prison":"수감자 교도소",
    "race_diversity":"인종다양성", "radiation_risk":"방사능",
    "rd":"R&D 연구개발", "recycling":"재활용",
    "refugees":"난민", "renew":"재생에너지 신재생",
    "research_pub":"논문 연구", "reserves":"외환보유고",
    "rice_consume":"쌀", "rugby":"럭비",
    "salary":"임금 월급", "school_yrs":"교육연수",
    "sex_duration":"섹스시간", "sex_education":"성교육",
    "sex_frequency":"섹스빈도", "smoking":"흡연 담배",
    "social_media":"소셜미디어 SNS",
    "solar_power":"태양광", "space_launch":"우주발사",
    "startup_rate":"스타트업 창업률", "stock_market":"주식시장",
    "street_food":"길거리음식", "strike_days":"파업",
    "suicide":"자살율", "surgeons":"외과의사",
    "tanning":"태닝 선탠", "tax_burden":"조세부담",
    "tax_rev":"세수입", "tax_top":"최고세율",
    "tea_consume":"차", "teen_pregnancy":"십대임신",
    "tertiary":"고등교육", "tourism":"관광 여행",
    "trafficking":"인신매매", "trump_approval":"트럼프지지율",
    "tsunami_risk":"쓰나미 지진해일", "tz":"시간대",
    "ubi_experiment":"기본소득실험", "unemp":"실업률",
    "unemp_benefit":"실업급여", "unicorns":"유니콘기업",
    "union_rate":"노조", "universities":"대학",
    "urban_pop":"도시인구", "vaccination":"백신 접종",
    "vat_rate":"부가세 VAT", "vc_funding":"벤처투자",
    "volcanoes":"화산", "water_scarcity":"물부족",
    "welfare_spend":"복지지출", "wildfire_freq":"산불",
    "wind_power":"풍력", "wine":"와인",
    "women_parl":"여성의원", "workhours":"노동시간 근로시간",
    "worldcup_parts":"월드컵출전", "youngest_leader":"최연소지도자",
    "yt_creators":"유튜버",
}

# Generate alias entries
alias_lines = []
for field in all_fields:
    en = desc.get(field, field).replace('"', '\\"')
    ko = KO.get(field, "")
    en_words = field.replace("_", " ")
    tags = f'{ko} {en_words} {en}' if ko else f'{en_words} {en}'
    alias_lines.append(f'      "{field}": "{tags}".split(" "),')

# Generate cluster entries (topic groupings)  
cluster_defs = {
    "경제 경제력 GDP 소득 부자 무역 수출입 세금": ["gdp","gdp_per_capita","reserves","exports","imports","fortune500","stock_market","salary","min_wage","tax_rev","tax_top","tax_burden","corp_tax","vat_rate","inflation","debt","govern_spend","credit_rating","vc_funding","manufacturing","union_rate"],
    "건강 의료 병원 수명 질병 암 당뇨": ["health","life_expectancy","doctors","nurses","surgeons","beds","cancer","diabetes","antibiotics","vaccination","mental_health","hiv_prev","maternal_mortality","infant_mortality","obesity","alcohol","smoking"],
    "범죄 살인 절도 폭력 마약": ["murder","burglary","assault","drug_offense","gang_violence","trafficking","prison","police","death_penalty","domestic_viol","polit_kill"],
    "교육 학교 대학 문해 PISA": ["edu","tertiary","college_rate","literacy","pisa_math","pisa_science","pisa_reading","phd_per_cap","research_pub","universities","school_yrs","sex_education"],
    "환경 탄소 숲 재활용 공기 미세먼지": ["co2","forest","renew","recycling","park_area","plastic_waste","pm25","food_waste","solar_power","wind_power","nuclear_power","radiation_risk","ev_adoption","organic_food"],
    "기술 인터넷 AI 5G 디지털": ["internet_pct","netspeed","g5_coverage","ai_research","ecommerce","penetration","egov_index","online_gov","social_media","space_launch"],
    "스포츠 올림픽 축구 농구 야구": ["olympic","olympic_gold","olympic_per_cap","worldcup_parts","fifa_ranking","fifa_w","basket","baseball","cricket","rugby","davis_cup","marathon_elite","chess"],
    "음식 커피 차 맥주 와인 고기": ["coffee","tea_consume","rice_consume","beer","wine","alcohol","beef_consume","pork_consume","chicken_consume","meat","bread_consume","michelin","street_food","organic_food","bottled_water","chocolate","fast_food"],
    "인권 자유 평등 여성 LGBTQ 성소수자": ["freedom","lgbtq_rights","disability","minority_rights","gay_marriage","death_penalty","gender","gender_gap","women_parl","democracy","press"],
    "군사 전쟁 핵무기 국방 NATO": ["military_pct","military_personnel","arms_export","nuclear","nuke_reactors","nato_year","peacekeeping","war_index"],
    "인구 출생 사망 도시 연령": ["population","population_density","birth_rate","death_rate","infant_mortality","fertility","urban_pop","median_age","immigration","emigration","refugees","displaced_from"],
    "에너지 전기 석유 태양광 풍력": ["energy_per_capita","electricity","solar_power","wind_power","nuclear_power","renew","gas_price"],
    "자연재해 지진 쓰나미 홍수 화산": ["earthquake_count","tsunami_risk","cyclone_freq","flood_risk","wildfire_freq","volcanoes","earthquakes"],
    "문화 영화 축제 유산 문학": ["film_prod","intangible","literature","festivals","libraries","game_market","books"],
    "여행 관광 여권 공항 비자": ["tourism","airports","aviation","passport","med_tourism","holidays"],
    "노인 연금 은퇴 고령 수명": ["life_expectancy","median_age","pension_rate","death_rate","cabinet_age","parl_age","leader_age"],
    "성관계 섹스 피임 콘돔 데이트": ["sex_frequency","sex_duration","condom_use","contraception","teen_pregnancy","onlyfans","adult_films","porn_search","sex_education","dating_apps"],
    "결혼 이혼 혼인 가족": ["marriage_age_m","marriage_age_f","marriage_rate","divorce","child_marriage","gay_marriage","parental_leave","divorce"],
    "노동 임금 실업 근로 파업": ["salary","min_wage","workhours","unemp","unemp_benefit","strike_days","union_rate","child_labor"],
    "국제기구 OECD EU G20 ASEAN NATO": ["oecd_member_order","eu_member","g20_member","g7_member","asean_member","apec_member","nato_year"],
    "생활 물가 집값 자동차 교통": ["cost_living","house_price","car_density","gas_price","motorcycle","line_length","railway","electricity","insurance"],
    "반려동물 고양이 개 애완": ["cat_own","dog_own"],
    "과학 노벨상 특허 논문 우주": ["nobel","nobel_per_capita","nobel_science","fields_medal","patents","rd","research_pub","physicists","chem_olympiad","math_olympiad","space_launch"],
}

cluster_lines = []
for key, fields in cluster_defs.items():
    existing = [f for f in fields if f in all_fields]
    if existing:
        cluster_lines.append(f'      "{key}": {json.dumps(existing)},')

# Build replacement blocks
new_aliases = "    var aliases = {\n" + "\n".join(alias_lines) + "\n    };"
new_clusters = "    var searchClusters = {\n" + "\n".join(cluster_lines) + "\n    };"

# Replace in JS
js = re.sub(r'var aliases = \{.*?\n    \};', new_aliases, js, flags=re.DOTALL)
js = re.sub(r'var searchClusters = \{.*?\n    \};', new_clusters, js, flags=re.DOTALL)

with open(f"{REPO}/docs/js/table.js", "w") as f:
    f.write(js)

print(f"✅ aliases: {len(alias_lines)}개 지표")
print(f"✅ clusters: {len(cluster_lines)}개 주제")
print(f"✅ table.js 업데이트 완료")
