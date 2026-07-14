// ============================================
// Rankerage.com — Main Table
// ============================================
(function() {
  'use strict';

  // ── AdSense Config (replace with real ID when approved) ──
  var ADSENSE_ID = ADSENSE_ID;  // ← AdSense 승인 후 여기만 바꾸면 됨
  var ADSENSE_TOP_SLOT = '1234567890';
  var ADSENSE_INROW_SLOT = '9876543210';
  var ADSENSE_FOOTER_SLOT = '5555555555';
  var ADS_ENABLED = true;  // 실제 ID면 true

  I18N.init().then(function() {
    var t = I18N.t;
    var desc = {};

    // Load descriptions
    fetch('data/descriptions.json').then(function(r){return r.json()}).then(function(d){desc = d;});function descTip(field,title){var d=desc[field]||title;var loc=I18N.getLocale2();if(loc==='ko'||!d)return d;var m=d.match(/^([^—]+?) — ([^(]+)\s*\((.+)\)$/);if(m)return m[1].trim()+' ('+m[3].trim()+')';m=d.match(/^([^—]+?) — (.+)$/);if(m)return m[1].trim();return d;}

    var S = function(a,b,aRow,bRow,col,dir){
      var na=(a==null||a>=NULL_SENTINEL||a<=NEG_SENTINEL),nb=(b==null||b>=NULL_SENTINEL||b<=NEG_SENTINEL);
      if(na&&nb)return 0;
      if(na)return 1;
      if(nb)return -1;
      return a-b;
    };
    var NULL_SENTINEL = 999999;
    var NEG_SENTINEL = -999999;
    function N(v) { return v === null || v === undefined || v === NULL_SENTINEL || v === NEG_SENTINEL; }
    function fmtNumber(n) { if (N(n)) return '-'; if (n >= 1e9) return (n / 1e9).toFixed(1)+'B'; if (n >= 1e6) return (n / 1e6).toFixed(1)+'M'; if (n >= 1e3) return (n / 1e3).toFixed(1)+'K'; return I18N.formatNumber(n); }
    function rankBadge(r) { if(!r)return'<span style="display:inline-block;width:26px;"></span>';var n=parseInt(r),c='#8892b0';if(n<=3)c='#f0a04b';else if(n<=10)c='#5b8def';else if(n<=20)c='#3fb68b';return'<span style="color:'+c+';font-weight:700;font-size:11px;">#'+n+'</span>'; }
    function numberCell(r,v) { return'<div style="display:flex;align-items:center;width:100%;"><span style="flex:0 0 26px;text-align:left;">'+(r?rankBadge(r):'')+'</span><span style="flex:1;text-align:right;font-family:\'JetBrains Mono\',Consolas,monospace;font-size:10.5px;white-space:nowrap;">'+v+'</span></div>'; }
    function suffix(n) { n=parseInt(n);if(!n)return'';return['th','st','nd','rd'][(n%100>10&&n%100<14)?0:(n%10>3?0:n%10)]||'th'; }

    var cols = [
      // Flag / Category Icon
      { title:"Reset",field:"country_code",width:26,frozen:true,headerHozAlign:"center",hozAlign:"center",
        formatter:function(c){var code=(c.getValue()||'??').toUpperCase();var name=c.getRow().getData().country_name_en||'';
          if(name.indexOf('***')===0)return'<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:14px;">🏟️</div>';
          if(name.indexOf('**')===0)return'<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:14px;">⭐</div>';
          if(name.indexOf('*')===0)return'<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:14px;">🏢</div>';
          var hash=0;for(var i=0;i<code.length;i++)hash=code.charCodeAt(i)+((hash<<5)-hash);var hue=Math.abs(hash)%360,sat=40+(Math.abs(hash>>4)%50),lit=25+(Math.abs(hash>>12)%25),bg='hsl('+hue+','+sat+'%,'+lit+'%)';return'<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;"><span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:15px;border-radius:3px;overflow:hidden;background:'+bg+';box-shadow:0 1px 2px rgba(0,0,0,0.3);flex-shrink:0;"><img src="https://flagcdn.com/16x12/'+code.toLowerCase()+'.png" width="16" height="12" loading="lazy" decoding="async" style="display:block;" onerror="this.remove();"></span></div>';},
        tooltip:function(e,c){return c.getRow().getData().country_summary;}},
      // Country
      { title:t('country'),field:"country_name_en",width:80,frozen:true,
        sorter:function(a,b){var pa=a.charCodeAt(0)<65,pb=b.charCodeAt(0)<65;if(pa&&!pb)return 1;if(!pa&&pb)return -1;return a<b?-1:a>b?1:0;},
        formatter:function(c){var d=c.getRow().getData(),code=d.country_code,name=I18N.countryName(code);return'<span style="display:inline-block;max-width:65px;overflow:hidden;text-overflow:clip;white-space:nowrap;">'+(name||d.country_name_en)+'</span>';},
        tooltip:function(e,c){var d=c.getRow().getData(),code=d.country_code,n2=I18N.countryName(code,I18N.getLocale2()),lo=d.country_name_local,p=[];if(n2&&n2!==d.country_name_en)p.push(n2);if(lo&&lo!==n2)p.push(lo);return p.join(' · ')||d.country_name_en;}},
      // === TRENDING (default sort) ===
      { title:"🔥Trend",field:"news_score",width:300,frozen:true,sorter:S,
        formatter:function(c){var d=c.getRow().getData(),v=d.news_score,title=d.news_title||'',img=d.news_image||'',url=d.news_url||'',src=d.news_source||'';
          if(!v||v<=0)return'<div style="color:#333;font-size:10px;padding:4px;">—</div>';
          var bar='█'.repeat(Math.min(Math.round(v),20));
          var h='<div class="news-card">';
          if(img)h+='<img src="'+esc(img)+'" class="news-thumb" loading="lazy" onerror="this.style.display=\'none\'">';
          h+='<div class="news-body">';
          h+='<a href="'+esc(url)+'" target="_blank" class="news-headline" title="'+esc(title)+'">'+esc(title).substring(0,80)+(title.length>80?'…':'')+'</a>';
          h+='<div class="news-meta">';
          if(src)h+=esc(src)+' · ';
          h+='<span style="color:#e0c87c;font-weight:700;">'+bar+' '+v.toFixed(1)+'</span>';
          if(d.news_age)h+=' · <span style="color:#545d7a;">'+esc(d.news_age)+'</span>';
          h+='</div>';
          h+='</div></div>';
          return h;}},
      // === CORE ===
      A(t('population'),"population",100), A(t('area'),"area",100), A(t('density'),"population_density",95),
      // === ECONOMY ===
      A(t('gdp'),"gdp",105), A(t('gdpPerCapita'),"gdp_per_capita",100),
      // === DEVELOPMENT ===
      A(t('hdi'),"hdi",72), A(t('lifeExp'),"life_expectancy",85), A(t('happiness'),"happiness",78),
      // === GOVERNANCE ===
      A(t('democracy'),"democracy",82), A(t('press'),"press",72), A(t('cpi'),"cpi",68), A(t('gpi'),"gpi",68), A(t('approval'),"approval",78), E("election_days",82),
      // === ECONOMY DEEP ===
      A(t('unemp'),"unemp",78), A(t('debt'),"debt",78), A(t('poverty'),"poverty",78),
      // === INNOVATION ===
      A(t('rd'),"rd",72), A(t('patents'),"patents",78),
      // === SOCIETY ===
      A(t('edu'),"edu",72), A(t('english'),"english",78), A(t('internet'),"internet_pct",78), A(t('gender'),"gender",78), A(t('fertility'),"fertility",78),
      // === HEALTH ===
      A(t('health2'),"health",78), A(t('obesity'),"obesity",78), A(t('alcohol'),"alcohol",78), A(t('pm25'),"pm25",78),
      // === ENVIRONMENT ===
      A(t('co2'),"co2",78), A(t('forest'),"forest",78), A(t('renew'),"renew",78),
      // === SECURITY ===
      A(t('military'),"military_pct",78), A(t('nuclear'),"nuclear",72), A(t('murder'),"murder",72),
      // === TRAVEL ===
      A(t('tourism'),"tourism",82),
      // === SPORTS (headerSort disabled for null-heavy columns) ===
      A(t('olympic'),"olympic",78), H(t('fifa'),"fifa_ranking",68), H(t('fifaW'),"fifa_w",72), H(t('basket'),"basket",72), H(t('cricket'),"cricket",72), H(t('rugby'),"rugby",72),
      // === ACHIEVEMENTS ===
      A(t('nobel'),"nobel",72),      A(t('quakeCnt'),"earthquake_count",72,false),      A(t('tsunami'),"tsunami_risk",72,false),      A(t('cyclone'),"cyclone_freq",72,false),      A(t('flood'),"flood_risk",72,false),      A(t('wildfire'),"wildfire_freq",72,false),      A(t('wcPart'),"worldcup_parts",72,false),      A(t('olyGold'),"olympic_gold",72,false),      A(t('olyCap'),"olympic_per_cap",72,false),      A(t('davis'),"davis_cup",72,false),      A(t('marathon'),"marathon_elite",72,false),      A(t('burglary'),"burglary",72,false),      A(t('drug'),"drug_offense",72,false),      A(t('assault'),"assault",72,false),      A(t('traffick'),"trafficking",72,false),      A(t('gang'),"gang_violence",72,false),      A(t('cancer'),"cancer",72,false),      A(t('diabetes'),"diabetes",72,false),      A(t('hiv'),"hiv_prev",72,false),      A(t('vaccine'),"vaccination",72,false),      A(t('mental'),"mental_health",72,false),      A(t('startup'),"startup_rate",72,false),      A(t('costlive'),"cost_living",72,false),      A(t('house'),"house_price",72,false),      A(t('minwage'),"min_wage",72,false),      A(t('pisaM'),"pisa_math",72,false),      A(t('pisaS'),"pisa_science",72,false),      A(t('pisaR'),"pisa_reading",72,false),      A(t('phd'),"phd_per_cap",72,false),      A(t('pub'),"research_pub",72,false),      A(t('recycle'),"recycling",72,false),      A(t('plastW'),"plastic_waste",72,false),      A(t('parkPct'),"park_area",72,false),      A(t('immig'),"immigration",72,false),      A(t('emig'),"emigration",72,false),      A(t('refugee'),"refugees",72,false),      A(t('genderGap'),"gender_gap",72,false),      A(t('lgbtq'),"lgbtq_rights",72,false),      A(t('g5g'),"g5_coverage",72,false),      A(t('ai'),"ai_research",72,false),      A(t('space'),"space_launch",72,false),      A(t('arms'),"arms_export",72,false),      A(t('peacekeep'),"peacekeeping",72,false),      A(t('intangbl'),"intangible",72,false),      A(t('film'),"film_prod",72,false),      A(t('michelin'),"michelin",72,false),      A(t('game'),"game_market",72,false),      A(t('tea'),"tea_consume",72,false),      A(t('rice'),"rice_consume",72,false),      A(t('waste'),"food_waste",72,false),      A(t('holiday'),"holidays",72,false),      A(t('influ'),"influencers",72,false),      A(t('fest'),"festivals",72,false),      A(t('tan'),"tanning",72,false),      A(t('streetfd'),"street_food",72,false),      A(t('cat'),"cat_own",72,false),      A(t('dog'),"dog_own",72,false),
      // === CULTURE/LIFESTYLE ===
      A(t('gini'),"gini",72), A(t('suicide'),"suicide",72),
      A(t('literacy'),"literacy",78), A(t('leave'),"leave",72),
      A(t('independence'),"independence",82), A(t('netspeed'),"netspeed",82),
      A(t('doctors'),"doctors",72), A(t('heritage'),"heritage",72),
      A(t('elevation'),"elevation",78), A(t('agri'),"agri",72),
      A(t('languages'),"languages",78), A(t('coffee'),"coffee",72),
      A(t('smoking'),"smoking",72), A(t('mcdonalds'),"mcdonalds",82),
      A(t('prison'),"prison",72), A(t('tz'),"tz",65),
      // === DEMOGRAPHICS DEEP ===
      A(t('birthRate'),"birth_rate",78,false), A(t('deathRate'),"death_rate",78,false),
      A(t('infantMortality'),"infant_mortality",82,false), A(t('urbanPop'),"urban_pop",78,false),
      A(t('medianAge'),"median_age",78,false),
      // === ECONOMY DEEP ===
      A(t('inflation'),"inflation",72,false), A(t('gasPrice'),"gas_price",78,false),
      A(t('energyCapita'),"energy_per_capita",82,false), A(t('electricity'),"electricity",82,false),
      A(t('reserves'),"reserves",82,false), A(t('exports'),"exports",82,false),
      A(t('imports'),"imports",82,false), A(t('governSpend'),"govern_spend",82,false),
      A(t('taxRev'),"tax_rev",78,false),
      // === LIFESTYLE ===
      A(t('carDensity'),"car_density",82,false), A(t('meat'),"meat",72,false),
      A(t('penetration'),"penetration",85,false), A(t('divorce'),"divorce",72,false),
      A(t('aviation'),"aviation",82,false), A(t('religionDiv'),"religion_div",82,false),

      A(t('milPersonnel'),"military_personnel",78,false),
      A(t('railway'),"line_length",78,false),
      A(t('matMortality'),"maternal_mortality",78,false),
      A(t('beer'),"beer",78,false),
      A(t('wine'),"wine",78,false),
      A(t('chocolate'),"chocolate",78,false),
      A(t('airports'),"airports",78,false),
      A(t('startups'),"startups",78,false),
      A(t('chess'),"chess",78,false),
      A(t('nobelCapita'),"nobel_per_capita",78,false),
      A(t('earthquakes'),"earthquakes",78,false),
      A(t('hdiAdj'),"hdi_adj",78,false),
      A(t('books'),"books",78,false),
      A(t('trump'),"trump_approval",78,false),
      A(t('nato'),"nato",78,false),
      A(t('nuclearPower'),"nuclear_power",78,false),
      A(t('volcanoes'),"volcanoes",78,false),
      A(t('mathOlympiad'),"math_olympiad",78,false),

      // === MORE SOCIAL & WORK ===
      A(t('police'),"police",72,false), A(t('beds'),"beds",72,false),
      A(t('studentsPerTeacher'),"students_per_teacher",82,false), A(t('salary'),"salary",82,false),
      A(t('workhours'),"workhours",78,false),
      // === AUTO-GENERATED from data fields ===
      A(t('adult_films'),"adult_films",72,false),
      A(t('ai_adopt'),"ai_adopt",72,false),
      A(t('antibiotics'),"antibiotics",72,false),
      A(t('apec_member'),"apec_member",72,false),
      A(t('asean_member'),"asean_member",72,false),
      A(t('baldness'),"baldness",72,false),
      A(t('baseball'),"baseball",72,false),
      A(t('basic_income'),"basic_income",72,false),
      A(t('beef_consume'),"beef_consume",72,false),
      A(t('bmi_avg'),"bmi_avg",72,false),
      A(t('bottled_water'),"bottled_water",72,false),
      A(t('bread_consume'),"bread_consume",72,false),
      A(t('business_ease'),"business_ease",72,false),
      A(t('cabinet_age'),"cabinet_age",72,false),
      A(t('chem_olympiad'),"chem_olympiad",72,false),
      A(t('chicken_consume'),"chicken_consume",72,false),
      A(t('child_labor'),"child_labor",72,false),
      A(t('child_marriage'),"child_marriage",72,false),
      A(t('college_rate'),"college_rate",72,false),
      A(t('condom_use'),"condom_use",72,false),
      A(t('contraception'),"contraception",72,false),
      A(t('corp_tax'),"corp_tax",72,false),
      A(t('credit_rating'),"credit_rating",72,false),
      A(t('crypto_own'),"crypto_own",72,false),
      A(t('dating_apps'),"dating_apps",72,false),
      A(t('death_penalty'),"death_penalty",72,false),
      A(t('disability'),"disability",72,false),
      A(t('displaced_from'),"displaced_from",72,false),
      A(t('domestic_viol'),"domestic_viol",72,false),
      A(t('e_scooter'),"e_scooter",72,false),
      A(t('ecommerce'),"ecommerce",72,false),
      A(t('egov_index'),"egov_index",72,false),
      A(t('election_date'),"election_date",72,false),
      A(t('eu_member'),"eu_member",72,false),
      A(t('ev_adoption'),"ev_adoption",72,false),
      A(t('extreme_poverty'),"extreme_poverty",72,false),
      A(t('fast_food'),"fast_food",72,false),
      A(t('fields_medal'),"fields_medal",72,false),
      A(t('fortune500'),"fortune500",72,false),
      A(t('freedom'),"freedom",72,false),
      A(t('g20_member'),"g20_member",72,false),
      A(t('g7_member'),"g7_member",72,false),
      A(t('gay_marriage'),"gay_marriage",72,false),
      A(t('gold_reserves'),"gold_reserves",72,false),
      A(t('height_f'),"height_f",78,false),
      A(t('height_m'),"height_m",78,false),
      A(t('homelessness'),"homelessness",72,false),
      A(t('insurance'),"insurance",72,false),
      A(t('insurance_cap'),"insurance_cap",72,false),
      A(t('leader_age'),"leader_age",72,false),
      A(t('libraries'),"libraries",72,false),
      A(t('life_exp_f'),"life_exp_f",78,false),
      A(t('life_exp_m'),"life_exp_m",78,false),
      A(t('literature'),"literature",72,false),
      A(t('manufacturing'),"manufacturing",72,false),
      A(t('marriage_age_f'),"marriage_age_f",72,false),
      A(t('marriage_age_m'),"marriage_age_m",72,false),
      A(t('marriage_rate'),"marriage_rate",72,false),
      A(t('med_tourism'),"med_tourism",72,false),
      A(t('minority_rights'),"minority_rights",72,false),
      A(t('motorcycle'),"motorcycle",72,false),
      A(t('nato_year'),"nato_year",72,false),
      A(t('netflix'),"netflix",72,false),
      A(t('nobel_science'),"nobel_science",72,false),
      A(t('nuke_reactors'),"nuke_reactors",72,false),
      A(t('nurses'),"nurses",72,false),
      A(t('oecd_member_order'),"oecd_member_order",72,false),
      A(t('online_gov'),"online_gov",72,false),
      A(t('onlyfans'),"onlyfans",72,false),
      A(t('organic_food'),"organic_food",72,false),
      A(t('parental_leave'),"parental_leave",72,false),
      A(t('parl_age'),"parl_age",72,false),
      A(t('passport'),"passport",72,false),
      A(t('pension_rate'),"pension_rate",72,false),
      A(t('physicists'),"physicists",72,false),
      A(t('polit_kill'),"polit_kill",72,false),
      A(t('pork_consume'),"pork_consume",72,false),
      A(t('porn_search'),"porn_search",72,false),
      A(t('poverty_gap'),"poverty_gap",72,false),
      A(t('race_diversity'),"race_diversity",72,false),
      A(t('radiation_risk'),"radiation_risk",72,false),
      A(t('school_yrs'),"school_yrs",72,false),
      A(t('sex_duration'),"sex_duration",72,false),
      A(t('sex_education'),"sex_education",72,false),
      A(t('sex_frequency'),"sex_frequency",72,false),
      A(t('slavery'),"slavery",72,false),
      A(t('social_media'),"social_media",72,false),
      A(t('solar_power'),"solar_power",72,false),
      A(t('stock_market'),"stock_market",72,false),
      A(t('strike_days'),"strike_days",72,false),
      A(t('surgeons'),"surgeons",72,false),
      A(t('tax_burden'),"tax_burden",72,false),
      A(t('tax_top'),"tax_top",72,false),
      A(t('teen_pregnancy'),"teen_pregnancy",72,false),
      A(t('tertiary'),"tertiary",72,false),
      A(t('ubi_experiment'),"ubi_experiment",72,false),
      A(t('unemp_benefit'),"unemp_benefit",72,false),
      A(t('unicorns'),"unicorns",72,false),
      A(t('union_rate'),"union_rate",72,false),
      A(t('universities'),"universities",72,false),
      A(t('vat_rate'),"vat_rate",72,false),
      A(t('vc_funding'),"vc_funding",72,false),
      A(t('war_index'),"war_index",72,false),
      A(t('water_scarcity'),"water_scarcity",72,false),
      A(t('welfare_spend'),"welfare_spend",72,false),
      A(t('wind_power'),"wind_power",72,false),
      A(t('women_parl'),"women_parl",72,false),
      A(t('youngest_leader'),"youngest_leader",72,false),
      A(t('yt_creators'),"yt_creators",72,false),

    ];

    function A(title,field,w,v){var col={title:title,field:field,width:w,sorter:S,
      headerTooltip:function(){return descTip(field,title);},
      formatter:function(c){var d=c.getRow().getData(),v=d[field];return numberCell(d[field+'_rank'],!N(v)?fmtNumber(v):'-');}};
      if(v===false)col.visible=false;return col;}
    function H(title,field,w,v){var col={title:title,field:field,width:w,sorter:S,
      headerTooltip:function(){return descTip(field,title);},
      formatter:function(c){var d=c.getRow().getData(),v=d[field];return numberCell(d[field+'_rank'],!N(v)?fmtNumber(v):'-');}};
      if(v===false)col.visible=false;return col;}
    function E(field,w){return{title:t('election'),field:field,width:w,
      sorter:function(a,b,aRow,bRow,col,dir){var da=aRow.getData().election_date,db=bRow.getData().election_date;if(!da&&!db)return 0;if(!da)return 1;if(!db)return -1;return da.localeCompare(db);},
      headerTooltip:function(){return descTip(field,t('election'));},
      formatter:function(c){var d=c.getRow().getData(),dt=d.election_date;if(!dt)return numberCell(null,'-');var p=dt.split('-'),s=p[1]+'/'+p[2];return numberCell(d.election_rank,s);}};}

    // Special formatters for non-standard value types
    cols.forEach(function(col){
      if(col.field==="gdp") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gdp_rank,d.gdp?'$'+fmtNumber(d.gdp):'-');};
      if(col.field==="gdp_per_capita") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gdp_per_capita_rank,!N(d.gdp_per_capita)?'$'+I18N.formatNumber(d.gdp_per_capita):'-');};
      if(col.field==="hdi") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.hdi_rank,!N(d.hdi)?d.hdi.toFixed(3):'-');};
      if(col.field==="life_expectancy") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.life_expectancy_rank,!N(d.life_expectancy)?d.life_expectancy.toFixed(1):'-');};
      if(col.field==="happiness") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.happiness_rank,!N(d.happiness)?d.happiness.toFixed(2):'-');};
      if(col.field==="democracy") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.democracy_rank,!N(d.democracy)?d.democracy.toFixed(2):'-');};
      if(col.field==="press") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.press_rank,!N(d.press)?d.press.toFixed(1):'-');};
      if(col.field==="cpi") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.cpi_rank,!N(d.cpi)?d.cpi+'/100':'-');};
      if(col.field==="gpi") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gpi_rank,!N(d.gpi)?d.gpi.toFixed(3):'-');};
      if(col.field==="approval") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.approval_rank,!N(d.approval)?d.approval+'%':'-');};
      if(col.field==="unemp") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.unemp_rank,!N(d.unemp)?d.unemp.toFixed(1)+'%':'-');};
      if(col.field==="debt") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.debt_rank,!N(d.debt)?d.debt.toFixed(0)+'%':'-');};
      if(col.field==="poverty") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.poverty_rank,!N(d.poverty)?d.poverty.toFixed(1)+'%':'-');};
      if(col.field==="rd") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.rd_rank,!N(d.rd)?d.rd.toFixed(2)+'%':'-');};
      if(col.field==="patents") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.patents_rank,!N(d.patents)?fmtNumber(d.patents):'-');};
      if(col.field==="edu") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.edu_rank,!N(d.edu)?d.edu.toFixed(3):'-');};
      if(col.field==="english") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.english_rank,!N(d.english)?d.english:'-');};
      if(col.field==="internet_pct") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.internet_pct_rank,!N(d.internet_pct)?d.internet_pct+'%':'-');};
      if(col.field==="gender") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gender_rank,!N(d.gender)?d.gender.toFixed(3):'-');};
      if(col.field==="fertility") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.fertility_rank,!N(d.fertility)?d.fertility.toFixed(2):'-');};
      if(col.field==="health") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.health_rank,!N(d.health)?d.health.toFixed(1)+'%':'-');};
      if(col.field==="obesity") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.obesity_rank,!N(d.obesity)?d.obesity.toFixed(1)+'%':'-');};
      if(col.field==="alcohol") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.alcohol_rank,!N(d.alcohol)?d.alcohol.toFixed(1):'-');};
      if(col.field==="pm25") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.pm25_rank,!N(d.pm25)?d.pm25.toFixed(1):'-');};
      if(col.field==="co2") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.co2_rank,!N(d.co2)?d.co2.toFixed(1):'-');};
      if(col.field==="forest") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.forest_rank,!N(d.forest)?d.forest.toFixed(1)+'%':'-');};
      if(col.field==="renew") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.renew_rank,!N(d.renew)?d.renew.toFixed(0)+'%':'-');};
      if(col.field==="military_pct") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.military_pct_rank,!N(d.military_pct)?d.military_pct.toFixed(1)+'%':'-');};
      if(col.field==="nuclear") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.nuclear_rank,!N(d.nuclear)?fmtNumber(d.nuclear):'-');};
      if(col.field==="murder") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.murder_rank,!N(d.murder)?d.murder.toFixed(1):'-');};
      if(col.field==="tourism") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.tourism_rank,!N(d.tourism)?d.tourism.toFixed(1)+'M':'-');};
      if(col.field==="olympic") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.olympic_rank,!N(d.olympic)?fmtNumber(d.olympic):'-');};
      if(col.field==="fifa_ranking") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.fifa_ranking_rank,!N(d.fifa_ranking)?d.fifa_ranking:'-');};
      if(col.field==="fifa_w") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.fifa_w_rank,!N(d.fifa_w)?d.fifa_w:'-');};
      if(col.field==="basket") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.basket_rank,!N(d.basket)?d.basket:'-');};
      if(col.field==="cricket") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.cricket_rank,!N(d.cricket)?d.cricket:'-');};
      if(col.field==="rugby") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.rugby_rank,!N(d.rugby)?d.rugby:'-');};
      if(col.field==="nobel") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.nobel_rank,!N(d.nobel)?d.nobel:'-');};
    });

    var table = new Tabulator("#example-table", {
      height:"calc(100vh - 48px)",layout:"fitDataFill",data:[],initialSort:[{column:"news_score",dir:"desc"}],columns:cols,
      pagination:false,movableColumns:true,headerHozAlign:"center",tooltips:true,tooltipDelay:150,rowHover:true,headerVisible:true,
      placeholder:'<div style="padding:40px;text-align:center;color:#545d7a;"><div style="font-size:48px;">🌍</div><div style="font-size:16px;font-weight:600;">'+t('loading')+'</div></div>',
      sortMode:"single",selectable:false,selectableRows:false,selectableCells:false,clipboard:true,selectableRangeMode:"click",
      clipboardCopyConfig:{columnHeaders:false,columnGroups:false,rowGroups:false,columnCalcs:false},
      rowFormatter:function(row){row.getElement().dataset.needsColspan='1';}
    });

    // Column reorder helper — use native bulk API for performance
    function reorderColumns(targetFields) {
      try { table.setColumnOrder(targetFields); } catch(e) {}
    }

    // ── Colspan Engine: merge cells across columns using real widths ──
    var MERGE_GROUPS = [
      // News trend is single wide column (no merge, just width:300)
      // Ad slots: merge 4-5 cells to fit AdSense in-feed native ads
      {startField:'unemp', count:4, title:'📢', id:'ad1'},
      {startField:'nuclear', count:4, title:'📢', id:'ad2'},
      {startField:'divorce', count:4, title:'📢', id:'ad3'},
    ];
    function applyColspans() {
      var rows = table.getRows();
      if (!rows.length) return;
      MERGE_GROUPS.forEach(function(grp) {
        var cols = table.getColumns(), startIdx = -1;
        for (var i = 0; i < cols.length; i++) {
          if (cols[i].getField() === grp.startField) { startIdx = i; break; }
        }
        if (startIdx < 0) return;
        // Use actual column widths (not precomputed — handles resize/reorder)
        var mergeW = 0;
        for (var j = startIdx; j < startIdx + grp.count && j < cols.length; j++) {
          mergeW += cols[j].getWidth();
        }
        rows.forEach(function(row) {
          var cells = row.getCells();
          if (cells.length <= startIdx) return;
          var first = cells[startIdx].getElement();
          // Hide merged-over cells
          for (var k = startIdx + 1; k < startIdx + grp.count && k < cells.length; k++) {
            cells[k].getElement().style.display = 'none';
          }
          // Span the first cell
          first.style.width = mergeW + 'px';
          first.style.minWidth = mergeW + 'px';
          first.style.maxWidth = mergeW + 'px';
          first.style.flex = '0 0 ' + mergeW + 'px';
          first.classList.add('colspan-cell');
          first.dataset.colspanGroup = grp.id;
          // Ad slots: inject AdSense in-feed native ad
          if (grp.id.indexOf('ad') === 0 && !first.querySelector('.colspan-ad')) {
            var aw = document.createElement('div');
            aw.className = 'colspan-ad';
            aw.style.cssText = 'width:100%;height:100%;display:flex;align-items:center;justify-content:center;';
            aw.innerHTML = '<ins class="adsbygoogle" style="display:block;width:'+(mergeW-8)+'px;height:32px" '
              + 'data-ad-client="ca-pub-9060044387299153" data-ad-slot="9876543210" '
              + 'data-ad-format="fluid" data-ad-layout-key="-fb+5w+4e-db+86"></ins>';
            first.innerHTML = '';
            first.appendChild(aw);
          } else if (!first.querySelector('.colspan-inner')) {
            var wrapper = document.createElement('div');
            wrapper.className = 'colspan-inner';
            wrapper.style.cssText = 'width:100%;padding:2px 6px;overflow:hidden;';
            while (first.firstChild) wrapper.appendChild(first.firstChild);
            first.appendChild(wrapper);
          }
        });
      });
    }
    // Reapply after every render
    var colspanDebounce = null;
    function scheduleColspans() {
      if (colspanDebounce) clearTimeout(colspanDebounce);
      colspanDebounce = setTimeout(applyColspans, 50);
    }
    table.on('dataLoaded', scheduleColspans);
    table.on('dataSorted', scheduleColspans);
    table.on('columnResized', scheduleColspans);

    // 기존 컬럼 순서 복원 (검색빈도 반영은 applyColumnOrder에서)

    // ── 1행1열(국기헤더): 알파벳 컬럼 정렬 리셋 ──
    // ── 1행2열(국가명헤더): 국가명 A-Z 소팅 토글 ──
    var countryNameSortDir = "asc";  // A-Z 기본

    table.on("headerClick", function(e, column) {
      var field = column.getField();
      if (field === "country_code") {
        // 1행1열 Reset 클릭 → 알파벳순 행+열 리셋
        e.preventDefault(); e.stopPropagation();
        var allCols = table.getColumnDefinitions()
          .map(function(c){return c.field;})
          .filter(function(f){return typeof f==='string' && f.length>0;});
        allCols.sort();
        reorderColumns(allCols);
        table.setSort('country_name_en','asc');
        localStorage.setItem('rankerage_col_order',JSON.stringify(allCols));
        clearHighlight();
        return false;
      } else if (field === "country_name_en") {
        // 국가명 헤더 클릭 → A-Z 정순만
        e.preventDefault(); e.stopPropagation();
        table.setSort("country_name_en","asc");
        clearHighlight();
        return false;
      }
    });

    // ── 검색 빈도수 추적 (localStorage) → 자주 찾는 컬럼이 앞에 ──
    function trackSearchCount(field) {
      var counts = {};
      try { counts = JSON.parse(localStorage.getItem('rankerage_search_counts') || '{}'); } catch(e) {}
      counts[field] = (counts[field] || 0) + 1;
      localStorage.setItem('rankerage_search_counts', JSON.stringify(counts));

      // 검색 3회 이상인 컬럼들을 앞으로
      var freq = Object.keys(counts).filter(function(f) { return counts[f] >= 3; });
      if (freq.length > 0) {
        var allCols = table.getColumns().map(function(c) { return c.getField(); });
        // 자주 찾는 컬럼을 앞으로, 나머지는 현재 순서 유지
        var front = freq.filter(function(f) { return allCols.indexOf(f) >= 2; });
        var rest = allCols.filter(function(f) { return front.indexOf(f) < 0; });
        var newOrder = allCols.slice(0, 2).concat(front).concat(rest.filter(function(f) { return allCols.indexOf(f) >= 2; }));
        try { reorderColumns(newOrder); } catch(e) {}
      }
    }

    // 기존 컬럼 순서 복원 시 검색 빈도 반영
    function applyColumnOrder() {
      var savedOrder = localStorage.getItem('rankerage_col_order');
      var counts = {};
      try { counts = JSON.parse(localStorage.getItem('rankerage_search_counts') || '{}'); } catch(e) {}
      var freq = Object.keys(counts).filter(function(f) { return counts[f] >= 3; });

      if (!savedOrder && freq.length === 0) return;

      var allCols = table.getColumns().map(function(c) { return c.getField(); });
      var order = savedOrder ? JSON.parse(savedOrder) : allCols;

      // flag(0), country(1)는 무조건 앞에
      var front = freq.filter(function(f) { return f !== 'country_code' && f !== 'country_name_en' && order.indexOf(f) >= 0; });
      var rest = order.filter(function(f) { return f !== 'country_code' && f !== 'country_name_en' && front.indexOf(f) < 0; });
      var newOrder = ['country_code', 'country_name_en'].concat(front).concat(rest);

      try { reorderColumns(newOrder); } catch(e) {}
    }

    // 컬럼 순서 저장 (기존 + 검색빈도 반영)
    table.on('columnMoved', function() {
      var order = table.getColumns().map(function(c){return c.getField();});
      localStorage.setItem('rankerage_col_order', JSON.stringify(order));
    });
    // 검색 빈도수 기반 컬럼 재배치 — 데이터 로드 후 실행됨
    var searchInput = document.getElementById("search");
    var dropdown = document.getElementById("searchDropdown");
    var allColumns = cols;

    // Column aliases/synonyms for smarter matching
            var aliases = {
      "agri": "농업 농경지 agri Agricultural Land — 국토 중 농경지 비율, % (Source: World Bank)".split(" "),
      "airports": "공항 airports Airports — 공항 총 개수 (Source: CIA Factbook)".split(" "),
      "alcohol": "술 알코올 음주 alcohol Alcohol Consumption — 1인당 연간 알코올 소비량, L (Source: WHO)".split(" "),
      "apec_member": "APEC 아펙 apec member apec_member".split(" "),
      "approval": "지지율 대통령 approval Leader Approval Rating — 국가원수 지지율, % (Source: Morning Consult)".split(" "),
      "area": "면적 국토 크기 area Area (km²) — 국토 총면적 (Source: World Bank)".split(" "),
      "asean_member": "ASEAN 아세안 asean member asean_member".split(" "),
      "aviation": "항공 비행기 aviation Air Passengers — 항공여객수 백만명 (Source: ICAO)".split(" "),
      "basket": "basket FIBA Basketball Ranking — 국제농구연맹 랭킹".split(" "),
      "beds": "병상 병원 beds Hospital Beds — 1000명당 병상 수 (Source: WHO)".split(" "),
      "beer": "맥주 beer Beer Consumption — 1인당 연간 맥주소비량 L (Source: Kirin Beer Univ.)".split(" "),
      "birth_rate": "출생률 출산 birth rate Birth Rate — 1000명당 출생률 (Source: UN)".split(" "),
      "books": "도서 책 books Book Publications — 연간 신간 발행 수 (Source: IPA)".split(" "),
      "cancer": "암 cancer Cancer Incidence — 10만명당 암발생률 (Source: WHO)".split(" "),
      "car_density": "자동차 차량 car density Car Density — 1000명당 자동차 보유대수 (Source: OICA)".split(" "),
      "chess": "체스 chess Chess Grandmasters — 체스 그랜드마스터 수 (Source: FIDE)".split(" "),
      "child_labor": "아동노동 child labor Child Labor — 아동노동비율, 5-14세 (Source: UNICEF)".split(" "),
      "child_marriage": "조혼 child marriage Child Marriage — 조혼비율 % (Source: UNICEF)".split(" "),
      "chocolate": "초콜릿 chocolate Chocolate Consumption — 1인당 연간 초콜릿소비 kg (Source: Statista)".split(" "),
      "co2": "탄소배출 CO2 co2 CO₂ Emissions — 1인당 탄소배출량, 톤 (Source: World Bank)".split(" "),
      "coffee": "커피 coffee Coffee Consumption — 1인당 연간 커피소비량, kg (Source: ICO)".split(" "),
      "college_rate": "대학진학률 college rate College Enrollment — 대학진학률, % (Source: UNESCO)".split(" "),
      "cpi": "부패지수 CPI 청렴 cpi Corruption Perceptions Index — 부패인식지수, 0=부패 100=청렴 (Source: Transparency Intl.)".split(" "),
      "cricket": "크리켓 cricket ICC Cricket Ranking — 국제크리켓평의회 테스트 랭킹".split(" "),
      "death_penalty": "사형 death penalty Death Penalty — 사형제 유지=1, 폐지=0 (Source: Amnesty)".split(" "),
      "death_rate": "사망률 death rate Death Rate — 1000명당 사망률 (Source: UN)".split(" "),
      "debt": "부채 정부부채 debt Public Debt — 정부부채, GDP 대비 % (Source: IMF)".split(" "),
      "democracy": "민주주의 democracy Democracy Index — 민주주의 지수, 0~10 (Source: EIU)".split(" "),
      "diabetes": "당뇨병 diabetes Diabetes Prevalence % — 당뇨병유병률 (Source: WHO)".split(" "),
      "displaced_from": "displaced from Displaced From — 자국발난민, 백만명 (Source: UNHCR)".split(" "),
      "divorce": "이혼 divorce Divorce Rate — 1000명당 이혼율 (Source: UN)".split(" "),
      "doctors": "의사 doctors Doctors per Capita — 1000명당 의사 수 (Source: WHO)".split(" "),
      "domestic_viol": "가정폭력 domestic viol Domestic Violence — 가정폭력평생유병률 % (Source: WHO)".split(" "),
      "earthquake_count": "지진횟수 earthquake count Earthquake Frequency — 지진발생빈도, 규모 6.0+ (Source: USGS)".split(" "),
      "earthquakes": "지진 earthquakes Earthquake Frequency — 연간 유의지진 횟수 M4+ (Source: USGS)".split(" "),
      "edu": "교육 edu Education Index — 교육지수, 0~1 (Source: UN)".split(" "),
      "election_days": "election days Next Election — 차기 선거까지 남은 일수".split(" "),
      "electricity": "전력 전기 electricity Electricity Use — 1인당 전력소비 kWh (Source: IEA)".split(" "),
      "elevation": "고도 해발 elevation Average Elevation — 평균 해발고도, m (Source: CIA Factbook)".split(" "),
      "emigration": "해외이주 emigration Emigration Rate % — 이민유출비율 (Source: UN DESA)".split(" "),
      "energy_per_capita": "에너지소비 energy per capita Energy Use — 1인당 에너지소비 kgOE (Source: IEA)".split(" "),
      "english": "영어 english English Proficiency Index — 영어능력지수 (Source: EF EPI)".split(" "),
      "eu_member": "EU 유럽연합 eu member eu_member".split(" "),
      "exports": "수출 exports Exports — 수출액 10억 USD (Source: WTO)".split(" "),
      "extreme_poverty": "극빈곤 extreme poverty Extreme Poverty — 극빈층비율, <$2.15/일 (Source: World Bank)".split(" "),
      "fertility": "출산율 fertility Fertility Rate — 합계출산율, 여성 1인당 출생아 수 (Source: UN)".split(" "),
      "fifa_ranking": "FIFA 축구 fifa ranking FIFA Men's Ranking — 국제축구연맹 남자 랭킹".split(" "),
      "fifa_w": "여자축구 FIFA fifa w FIFA Women's Ranking — 국제축구연맹 여자 랭킹".split(" "),
      "forest": "산림 숲 forest Forest Area — 국토 대비 산림면적, % (Source: World Bank)".split(" "),
      "g20_member": "G20 g20 member g20_member".split(" "),
      "g7_member": "G7 g7 member g7_member".split(" "),
      "gas_price": "휘발유 기름값 gas price Gas Price — 휘발유 1L 가격 USD (Source: GlobalPetrolPrices)".split(" "),
      "gdp": "GDP 경제 gdp GDP (Gross Domestic Product) — 국가 총생산액, 백만$ (Source: IMF)".split(" "),
      "gdp_per_capita": "1인당GDP 소득 gdp per capita GDP per Capita — 1인당 국내총생산, $ (Source: IMF)".split(" "),
      "gender": "성평등 젠더 gender Gender Gap Index — 성평등지수, 0~1 (Source: WEF)".split(" "),
      "gini": "지니계수 불평등 gini Gini Coefficient — 소득불평등 지수, 0=완전평등 100=완전불평등 (Source: World Bank)".split(" "),
      "govern_spend": "정부지출 govern spend Government Spending — GDP대비 정부지출 % (Source: IMF)".split(" "),
      "gpi": "평화지수 gpi Global Peace Index — 세계평화지수, 낮을수록 평화로움 (Source: IEP)".split(" "),
      "happiness": "행복 웰빙 happiness World Happiness Report — 행복지수, 0~10. 설문 기반 (Source: UN SDSN)".split(" "),
      "hdi": "HDI 인간개발 hdi Human Development Index — 인간개발지수, 0~1. 교육+소득+기대수명 (Source: UNDP)".split(" "),
      "hdi_adj": "HDI조정 hdi adj Inequality-Adj HDI — 불평등조정 인간개발지수 (Source: UNDP)".split(" "),
      "health": "의료비 건강 health Healthcare Spending — 의료비지출, GDP 대비 % (Source: WHO)".split(" "),
      "heritage": "유네스코 세계유산 heritage UNESCO Heritage — 세계문화유산 등재 수 (Source: UNESCO)".split(" "),
      "hiv_prev": "HIV 에이즈 hiv prev HIV Prevalence % — HIV감염률, 15-49세 (Source: WHO)".split(" "),
      "imports": "수입 imports Imports — 수입액 10억 USD (Source: WTO)".split(" "),
      "independence": "independence Country Age — 독립/건국 후 경과년수 (2026 기준)".split(" "),
      "infant_mortality": "영아사망률 infant mortality Infant Mortality — 1000명당 영아사망률 (Source: WHO)".split(" "),
      "inflation": "인플레이션 물가 inflation Inflation Rate — 연간 소비자물가상승률 % (Source: IMF)".split(" "),
      "internet_pct": "인터넷 internet pct Internet Usage — 인터넷 사용률, % (Source: ITU)".split(" "),
      "languages": "언어 languages Linguistic Diversity — 사용 언어 수 (Source: Ethnologue)".split(" "),
      "leave": "휴가 leave Minimum Annual Leave — 법정 최소 연차일수, 일 (Source: Wikipedia)".split(" "),
      "life_expectancy": "기대수명 수명 life expectancy Life Expectancy — 평균 기대수명, 년 (Source: WHO)".split(" "),
      "line_length": "철도 line length Railway Network — 철도 총연장 km (Source: CIA Factbook)".split(" "),
      "literacy": "문해율 literacy Literacy Rate — 성인 문자해독률, % (Source: UNESCO)".split(" "),
      "maternal_mortality": "산모사망 maternal mortality Maternal Mortality — 출산 10만건당 산모사망률 (Source: WHO)".split(" "),
      "math_olympiad": "수학올림피아드 math olympiad Math Olympiad — 국제수학올림피아드 통산 메달 (Source: IMO)".split(" "),
      "mcdonalds": "맥도날드 mcdonalds McDonald's Density — 100만명당 맥도날드 매장 수 (Source: McDonald's Corp)".split(" "),
      "meat": "육류 고기 meat Meat Consumption — 1인당 연간 육류소비 kg (Source: FAO)".split(" "),
      "median_age": "중위연령 median age Median Age — 중위연령 (Source: UN)".split(" "),
      "mental_health": "정신건강 mental health Mental Health Index — 정신건강지수 1-10 (Source: Various)".split(" "),
      "military_pct": "군사비 국방비 military pct Military Spending — GDP 대비 국방비, % (Source: SIPRI)".split(" "),
      "military_personnel": "군인 military personnel Military Personnel — 현역 군인 수, 천명 (Source: IISS)".split(" "),
      "murder": "살인율 murder Murder Rate — 10만명당 살인범죄율 (Source: UNODC)".split(" "),
      "nato": "nato NATO Member — 북대서양조약기구 회원국 여부".split(" "),
      "nato_year": "NATO 나토 nato year nato_year".split(" "),
      "netspeed": "인터넷속도 netspeed Internet Speed — 평균 인터넷 속도, Mbps (Source: Speedtest Global Index)".split(" "),
      "nobel": "노벨상 nobel Nobel Prizes — 노벨상 총 수상자 수 (Source: Nobel Foundation)".split(" "),
      "nobel_per_capita": "1인당노벨상 nobel per capita Nobel per Capita — 백만명당 노벨상 수상자 (Source: Nobel Foundation)".split(" "),
      "nuclear": "핵무기 nuclear Nuclear Weapons — 추정 핵탄두 보유량 (Source: SIPRI)".split(" "),
      "nuclear_power": "원자력 원전 nuclear power Nuclear Power — 원자력발전 비중 % (Source: IAEA)".split(" "),
      "obesity": "비만 obesity Obesity Rate — 성인 비만율, % (Source: WHO)".split(" "),
      "oecd_member_order": "OECD 가입순서 oecd member order oecd_member_order".split(" "),
      "olympic": "올림픽 olympic Olympic Medals — 하계+동계 올림픽 통산 메달 수 (Source: IOC)".split(" "),
      "patents": "특허 patents Patent Applications — 백만명당 특허출원 수 (Source: WIPO)".split(" "),
      "penetration": "소셜미디어 penetration Social Penetration — 소셜미디어 보급률 % (Source: DataReportal)".split(" "),
      "pm25": "미세먼지 초미세먼지 pm25 PM2.5 Air Pollution — 초미세먼지 농도, μg/m³ (Source: IQAir)".split(" "),
      "police": "경찰 police Police per Capita — 10만명당 경찰 수 (Source: UNODC)".split(" "),
      "polit_kill": "정치적살인 polit kill Political Killings — 10만명당 정치적 살해 (Source: ACLED/UCDP)".split(" "),
      "population": "인구 population Population — 총 인구수 (Source: UN World Population Prospects)".split(" "),
      "population_density": "인구밀도 population density Population Density — 1km²당 인구수 (Source: UN)".split(" "),
      "poverty": "빈곤율 poverty Poverty Rate — 빈곤율, 국가빈곤선 기준 % (Source: World Bank)".split(" "),
      "press": "언론자유 press Press Freedom Index — 언론자유지수, 낮을수록 자유 (Source: RSF)".split(" "),
      "prison": "수감자 교도소 prison Incarceration Rate — 10만명당 수감자 수 (Source: World Prison Brief)".split(" "),
      "rd": "R&D 연구개발 rd R&D Spending — 연구개발비, GDP 대비 % (Source: UNESCO)".split(" "),
      "refugees": "난민 refugees Refugees Hosted — 난민수용자수, 천명 (Source: UNHCR)".split(" "),
      "religion_div": "religion div Religious Diversity — 종교다양성지수 0~10 (Source: Pew Research)".split(" "),
      "renew": "재생에너지 신재생 renew Renewable Energy — 전력 중 재생에너지 비중, % (Source: IRENA)".split(" "),
      "reserves": "외환보유고 reserves Foreign Reserves — 외환보유액 10억 USD (Source: IMF)".split(" "),
      "rugby": "럭비 rugby World Rugby Ranking — 세계럭비연맹 랭킹".split(" "),
      "salary": "임금 월급 salary Average Monthly Salary — 평균 월급, USD (Source: Various)".split(" "),
      "slavery": "slavery Modern Slavery — 노예지수, 1000명당 (Source: Walk Free)".split(" "),
      "smoking": "흡연 담배 smoking Cigarette Consumption — 1인당 연간 담배소비량, 개비 (Source: WHO)".split(" "),
      "startups": "startups Startup Ecosystem — 스타트업 생태계 점수 0~100 (Source: StartupBlink)".split(" "),
      "students_per_teacher": "students per teacher Students per Teacher — 초등교사 1인당 학생 수 (Source: UNESCO)".split(" "),
      "suicide": "자살율 suicide Suicide Rate — 10만명당 자살률 (Source: WHO)".split(" "),
      "tax_rev": "세수입 tax rev Tax Revenue — GDP대비 조세수입 % (Source: OECD/IMF)".split(" "),
      "teen_pregnancy": "십대임신 teen pregnancy Teen Pregnancy — 10대임신률, 1000명당 (Source: WHO)".split(" "),
      "tourism": "관광 여행 tourism Tourism Arrivals — 연간 관광객 수, 백만명 (Source: UNWTO)".split(" "),
      "trump_approval": "트럼프지지율 trump approval Trump Approval — 도널드 트럼프 지지율 % (Source: Gallup/Pew)".split(" "),
      "tz": "시간대 tz Timezone — UTC 기준 절대 시차, 시간 (Source: IANA)".split(" "),
      "unemp": "실업률 unemp Unemployment Rate — 실업률, % (Source: ILO)".split(" "),
      "union_rate": "노조 union rate Unionization — 노조조직화율 % (Source: OECD/ILO)".split(" "),
      "urban_pop": "도시인구 urban pop Urban Population — 도시거주비율 % (Source: UN)".split(" "),
      "volcanoes": "화산 volcanoes Volcanoes — 활화산 개수 (Source: Smithsonian GVP)".split(" "),
      "war_index": "war index War Involvement — 전쟁관여지수 0-10 (Source: ACLED/UCDP)".split(" "),
      "wine": "와인 wine Wine Consumption — 1인당 연간 와인소비량 L (Source: OIV)".split(" "),
      "women_parl": "여성의원 women parl Women in Parliament — 여성의원비율 % (Source: IPU)".split(" "),
      "workhours": "노동시간 근로시간 workhours Weekly Work Hours — 주당 평균 노동시간 (Source: ILO)".split(" "),
    };

    // ===== AI CLUSTERS: smart topic groupings =====
            var searchClusters = {
      "경제 경제력 GDP 소득 부자 무역 수출입 세금": ["gdp", "gdp_per_capita", "reserves", "exports", "imports", "salary", "tax_rev", "inflation", "debt", "govern_spend", "union_rate"],
      "건강 의료 병원 수명 질병 암 당뇨": ["health", "life_expectancy", "doctors", "beds", "cancer", "diabetes", "mental_health", "hiv_prev", "maternal_mortality", "infant_mortality", "obesity", "alcohol", "smoking"],
      "범죄 살인 절도 폭력 마약": ["murder", "prison", "police", "death_penalty", "domestic_viol", "polit_kill"],
      "교육 학교 대학 문해 PISA": ["edu", "college_rate", "literacy"],
      "환경 탄소 숲 재활용 공기 미세먼지": ["co2", "forest", "renew", "pm25", "nuclear_power"],
      "기술 인터넷 AI 5G 디지털": ["internet_pct", "netspeed", "penetration"],
      "스포츠 올림픽 축구 농구 야구": ["olympic", "fifa_ranking", "fifa_w", "basket", "cricket", "rugby", "chess"],
      "음식 커피 차 맥주 와인 고기": ["coffee", "beer", "wine", "alcohol", "meat", "chocolate"],
      "인권 자유 평등 여성 LGBTQ 성소수자": ["death_penalty", "gender", "women_parl", "democracy", "press"],
      "군사 전쟁 핵무기 국방 NATO": ["military_pct", "military_personnel", "nuclear", "nato_year", "war_index"],
      "인구 출생 사망 도시 연령": ["population", "population_density", "birth_rate", "death_rate", "infant_mortality", "fertility", "urban_pop", "median_age", "emigration", "refugees", "displaced_from"],
      "에너지 전기 석유 태양광 풍력": ["energy_per_capita", "electricity", "nuclear_power", "renew", "gas_price"],
      "자연재해 지진 쓰나미 홍수 화산": ["earthquake_count", "volcanoes", "earthquakes"],
      "문화 영화 축제 유산 문학": ["books"],
      "여행 관광 여권 공항 비자": ["tourism", "airports", "aviation"],
      "노인 연금 은퇴 고령 수명": ["life_expectancy", "median_age", "death_rate"],
      "성관계 섹스 피임 콘돔 데이트": ["teen_pregnancy"],
      "결혼 이혼 혼인 가족": ["divorce", "child_marriage", "divorce"],
      "노동 임금 실업 근로 파업": ["salary", "workhours", "unemp", "union_rate", "child_labor"],
      "국제기구 OECD EU G20 ASEAN NATO": ["oecd_member_order", "eu_member", "g20_member", "g7_member", "asean_member", "apec_member", "nato_year"],
      "생활 물가 집값 자동차 교통": ["car_density", "gas_price", "line_length", "electricity"],
      "과학 노벨상 특허 논문 우주": ["nobel", "nobel_per_capita", "patents", "rd", "math_olympiad"],
    };

    // AI-enhanced fuzzy score: searches clusters for related terms
    function fuzzyScore(field, query) {
      var title = ((colLabels[field]||'') + ' ' + (desc[field]||'')).toLowerCase();
      var q = query.toLowerCase();
      if (title.indexOf(q) >= 0) return 100;
      // Check aliases
      var al = aliases[field] || [];
      for (var i = 0; i < al.length; i++) {
        if (al[i].toLowerCase().indexOf(q) >= 0) return 80;
      }
      // AI cluster matching: search query against all clusters
      for (var ck in searchClusters) {
        if (ck.indexOf(q) >= 0 && searchClusters[ck].indexOf(field) >= 0) {
          return 75;
        }
        // Partial match: if query is part of any cluster keyword
        var cWords = ck.split(' ');
        for (var ci = 0; ci < cWords.length; ci++) {
          if (cWords[ci].indexOf(q) >= 0 && searchClusters[ck].indexOf(field) >= 0) {
            return 65;
          }
        }
      }
      // Word boundary match
      var words = title.split(/[\s\-\_\/]+/);
      for (var i = 0; i < words.length; i++) {
        if (words[i].indexOf(q) >= 0) return 60;
        if (words[i].length > 0 && q.indexOf(words[i]) >= 0) return 40;
      }
      if (title[0] === q[0]) return 20;
      return 0;
    }

    searchInput.addEventListener("input", function() {
      var q = this.value.trim().toLowerCase();
      if (q.length < 2) { dropdown.style.display = 'none'; return; }
      var html = '';
      
      // 1) 순위명 검색
      var cols = allColumns.filter(function(c) { return c.field && c.field !== 'country_code' && c.field !== 'country_name_en'; })
        .map(function(c) { return { col: c, score: fuzzyScore(c.field, q) }; })
        .filter(function(s) { return s.score > 0; })
        .sort(function(a, b) { return b.score - a.score; })
        .slice(0, 10);
      
      // 2) 국가명 검색 (English + local name)
      var cRows = table.getRows().filter(function(r){
        var d = r.getData();
        var n = (d.country_name_en || '').toLowerCase();
        var l = (d.country_name_local || '').toLowerCase();
        return n.indexOf(q) >= 0 || l.indexOf(q) >= 0;
      }).slice(0, 5);
      
      // 3) 파생 컬럼 제안 — 사용자가 없는 순위를 원하면 즉석 생성
      var derived = [];
      if (cols.length < 3) {
        // per capita: "nuclear per capita" → nuclear / population
        var pcMatch = q.match(/^(.+?)\s*(per capita|per person|per head|1인당|인당)\s*$/);
        // per area: "gdp per area" → gdp / area  
        var paMatch = q.match(/^(.+?)\s*(per area|per km|per sq|면적당|단위면적)\s*$/);
        // X/Y ratio: "nuclear vs gdp" or "nuclear/gdp"
        var vsMatch = q.match(/^(.+?)\s*(vs\.?|versus|\/)\s*(.+?)$/);
        var match = pcMatch || paMatch || vsMatch;
        if (match) {
          var term = (match[1]||'').trim();
          var divisor = paMatch ? 'area' : pcMatch ? 'population' : (match[3]||'').trim();
          // Find closest field to the search term
          var bestField = null, bestScore = 0;
          allColumns.forEach(function(c) {
            if (!c.field || c.field === 'country_code' || c.field === 'country_name_en') return;
            var s = fuzzyScore(c.field, term);
            if (s > bestScore) { bestScore = s; bestField = c.field; }
          });
          // Find divisor field
          var divField = null;
          allColumns.forEach(function(c) {
            if (!c.field) return;
            var s = fuzzyScore(c.field, divisor);
            if (s > 40) { divField = c.field; }
          });
          if (bestField && divField && bestField !== divField && bestScore > 20) {
            var op = (paMatch||pcMatch) ? '/' : 'vs';
            var label = (paMatch||pcMatch) ?
              (colLabels[bestField]||bestField) + ' per ' + (colLabels[divField]||divField) :
              (colLabels[bestField]||bestField) + ' vs ' + (colLabels[divField]||divField);
            derived.push({field1:bestField, field2:divField, op:op, label:label, id:'derived_'+bestField+'_'+op+'_'+divField});
          }
        }
      }
      
      if (!cols.length && !cRows.length && !derived.length) { dropdown.style.display = 'none'; return; }
      
      // 국가명 결과 먼저
      cRows.forEach(function(r){
        var d = r.getData(), name = d.country_name_en, code = d.country_code;
        var hl = name.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi'), '<strong>$1</strong>');
        html += '<div class="search-dropdown-item country-item" data-type="country" data-code="'+code+'" data-name="'+name+'">🏳️ '+hl+'</div>';
      });
      
      // 순위명 결과
      cols.forEach(function(s){
        var title = s.col.title;
        var hl = title.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\\]\\\\]/g,'\\\\$&')+')','gi'), '<strong>$1</strong>');
        html += '<div class="search-dropdown-item metric-item" data-type="metric" data-field="'+s.col.field+'" data-title="'+title+'">📊 '+hl+'</div>';
      });
      
      // 파생 컬럼 결과
      derived.forEach(function(d){
        html += '<div class="search-dropdown-item derived-item" data-type="derived" data-field1="'+d.field1+'" data-field2="'+d.field2+'" data-op="'+d.op+'" data-label="'+esc(d.label)+'" data-id="'+d.id+'">🧪 <strong>Create:</strong> '+esc(d.label)+'</div>';
      });
      
      dropdown.innerHTML = html;
      dropdown.style.display = 'block';
    });

    // ── 검색된 컬럼을 활성 정렬 컬럼으로 추적 ──
    var activeSortField = "population";  // 기본값
    var activeSortDir = "asc";  // 첫클릭 정순 기본값

    // ── Persistent highlight state ──
    var activeHighlight = null;
    var highlightTimer = null;

    function clearHighlight() {
      if (activeHighlight) {
        activeHighlight.classList.remove('highlight', 'highlight-pulse');
        var badge = activeHighlight.querySelector('.search-found-badge');
        if (badge) badge.remove();
        activeHighlight = null;
      }
      if (highlightTimer) { clearTimeout(highlightTimer); highlightTimer = null; }
    }

    function highlightColumn(field) {
      clearHighlight();
      activeSortField = field;
      activeSortDir = "desc";
      trackSearchCount(field);  // 검색 빈도 추적
      var header = document.querySelector('.tabulator-col[data-field="' + field + '"]');
      if (!header) {
        header = document.querySelector('.tabulator-col[tabulator-field="' + field + '"]');
      }
      if (!header) return;

      // 1) 강조 클래스 추가
      header.classList.add('highlight', 'highlight-pulse');

      // 2) 📍 배지
      var badge = document.createElement('span');
      badge.className = 'search-found-badge';
      badge.textContent = '📍';
      badge.title = '검색 결과 — 국가명 클릭으로 소팅';
      header.appendChild(badge);

      // 3) Tabulator API로 컬럼을 맨 왼쪽(국기 옆)으로 스크롤
      try {
        table.scrollToColumn(field, 'left', true);
      } catch (_) {
        header.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
      }

      // 4) 15초 후 펄스 멈춤
      highlightTimer = setTimeout(function() {
        if (header) header.classList.remove('highlight-pulse');
      }, 15000);

      activeHighlight = header;
    }

    // Clear highlight when user manually sorts or scrolls table
    table.on("columnMoved", clearHighlight);
    table.on("tableDestroyed", clearHighlight);

    dropdown.addEventListener("click", function(e) {
      var item = e.target.closest(".search-dropdown-item");
      if (!item) return;
      var type = item.getAttribute("data-type");
      
      if (type === "country") {
        // 국가 클릭 → 그 국가 + 동일 지역 국가들 최상단으로 + 강한 순위순 컬럼 재정렬
        var code = item.getAttribute("data-code");
        var name = item.getAttribute("data-name");
        
        // Find the country and its region
        var targetData = null, targetSub = null;
        var allData = table.getData();
        for (var i = 0; i < allData.length; i++) {
          if (allData[i].country_code === code) {
            targetData = allData[i];
            targetSub = targetData.subcontinent || targetData.continent || '';
            break;
          }
        }
        if (!targetData) return;
        
        // Save current sort state
        var saveSort = table.getSorters()[0];
        
        // Reorder rows: searched country first, then same subcontinent (A-Z), then rest
        var sameRegion = [], others = [];
        for (var i = 0; i < allData.length; i++) {
          if (allData[i].country_code === code) continue;
          var sub = allData[i].subcontinent || allData[i].continent || '';
          if (sub === targetSub) sameRegion.push(allData[i]);
          else others.push(allData[i]);
        }
        sameRegion.sort(function(a, b) { return (a.country_name_en||'').localeCompare(b.country_name_en||''); });
        var newData = [targetData].concat(sameRegion).concat(others);
        table.setData(newData);
        
        // Re-apply sort if there was one
        if (saveSort && saveSort.field) {
          table.setSort(saveSort.field, saveSort.dir);
        }
        
        // 컬럼 재정렬 (국가 강한 순)
        var d = targetData, ranks = [];
        table.getColumns().forEach(function(col){
          var f = col.getField();
          if (f && f !== 'country_code' && f !== 'country_name_en') {
            var rk = d[f + '_rank'];
            ranks.push({field: f, rank: rk != null ? parseInt(rk) : 9999});
          }
        });
        ranks.sort(function(a, b) { return a.rank - b.rank; });
        var order = ['country_code', 'country_name_en'].concat(ranks.map(function(rk) { return rk.field; }));
        reorderColumns(order);
        activeSortField = ranks[0].field;
        activeSortDir = 'asc';
        highlightColumn(activeSortField);
        searchInput.value = name;
      } else if (type === "derived") {
        // 파생 컬럼 생성 — 없는 순위를 즉석에서 만들어 선물
        var f1 = item.getAttribute("data-field1");
        var f2 = item.getAttribute("data-field2");
        var op = item.getAttribute("data-op");
        var label = item.getAttribute("data-label");
        var vid = item.getAttribute("data-id");
        // Compute values for all rows
        var rows = table.getData();
        rows.forEach(function(r) {
          var v1 = r[f1], v2 = r[f2];
          if (v1 == null || v1 >= NULL_SENTINEL || v1 <= NEG_SENTINEL) v1 = null;
          if (v2 == null || v2 >= NULL_SENTINEL || v2 <= NEG_SENTINEL) v2 = null;
          if (v1 != null && v2 != null && v2 !== 0) {
            r[vid] = op === '/' ? v1 / v2 : Math.abs(v1 - v2);
          } else {
            r[vid] = null;
          }
        });
        // Compute ranks
        var sorted = rows.slice().filter(function(r){return r[vid]!=null;}).sort(function(a,b){return b[vid]-a[vid];});
        sorted.forEach(function(r,i){r[vid+'_rank']=i+1;});
        // Add virtual column
        var vcol = {title:label, field:vid, width:90, sorter:S,
          formatter:function(c){var d=c.getRow().getData(),v=d[vid];return numberCell(d[vid+'_rank'],!N(v)?(op==='/'?v.toFixed(4):fmtNumber(v)):'-');}
        };
        try { table.addColumn(vcol, false, 'country_name_en'); } catch(e) {}
        table.setSort(vid, 'desc');
        highlightColumn(vid);
        searchInput.value = label;
      } else {
        // 순위명 클릭 → 컬럼 3열로 이동 + 소팅 + 하이라이트
        var field = item.getAttribute("data-field");
        var title = item.getAttribute("data-title");
        // 컬럼을 3열 위치로 이동
        var allCols = table.getColumnDefinitions().map(function(c){return c.field;}).filter(function(f){return f;});
        var idx = allCols.indexOf(field);
        if(idx >= 2){
          allCols.splice(idx,1);
          allCols.splice(2,0,field);
          reorderColumns(allCols);
        }
        table.setSort(field, "desc");
        highlightColumn(field);
        searchInput.value = title;
      }
      dropdown.style.display = 'none';
      searchInput.focus();
      searchInput.select();
    });

    searchInput.addEventListener("keydown", function(e) {
      if (e.key === 'Escape') { dropdown.style.display = 'none'; this.blur(); }
      if (e.key === 'Enter') {
        var first = dropdown.querySelector(".search-dropdown-item");
        if (first) first.click();
      }
    });

    searchInput.addEventListener("blur", function() {
      setTimeout(function() { dropdown.style.display = 'none'; }, 200);
    });

    // Search button: trigger sort on first dropdown item
    document.getElementById("searchBtn").addEventListener("click", function() {
      var first = dropdown.querySelector(".search-dropdown-item");
      if (first) first.click();
      else searchInput.focus();
    });

    // Load data - progressive rendering to avoid main-thread freeze
    fetch('data/countries.json').then(function(r){return r.json()}).then(function(data){
      // Replace null with two sentinels: desc fields use -999999, asc fields use 999999
      var fields = ["news_score","population","area","population_density","gdp","gdp_per_capita","hdi","life_expectancy","happiness","fifa_ranking","cpi","gpi","internet_pct","military_pct","democracy","press","unemp","debt","poverty","rd","patents","edu","english","gender","fertility","health","obesity","alcohol","pm25","co2","forest","renew","nuclear","murder","tourism","olympic","fifa_w","basket","cricket","rugby","nobel","approval","gini","suicide","tz","prison","literacy","netspeed","doctors","heritage","military_personnel","line_length","maternal_mortality","beer","wine","chocolate","airports","startups","chess","nobel_per_capita","earthquakes","hdi_adj","books","trump_approval","nato","nuclear_power","volcanoes","math_olympiad","birth_rate","death_rate","infant_mortality","urban_pop","median_age","energy_per_capita","inflation","gas_price","car_density","meat","govern_spend","tax_rev","reserves","exports","imports","penetration","divorce","aviation","religion_div","electricity","leave","independence","smoking","mcdonalds","elevation","agri","languages","coffee","police","beds","students_per_teacher","salary","workhours","earthquake_count","tsunami_risk","cyclone_freq","flood_risk","wildfire_freq","worldcup_parts","olympic_gold","olympic_per_cap","davis_cup","marathon_elite","burglary","drug_offense","assault","trafficking","gang_violence","cancer","diabetes","hiv_prev","vaccination","mental_health","startup_rate","cost_living","house_price","min_wage","pisa_math","pisa_science","pisa_reading","phd_per_cap","research_pub","recycling","plastic_waste","park_area","immigration","emigration","refugees","gender_gap","lgbtq_rights","g5_coverage","ai_research","space_launch","arms_export","peacekeeping","intangible","film_prod","michelin","game_market","tea_consume","rice_consume","food_waste","holidays","influencers","festivals","tanning","street_food","cat_own","dog_own"];
      var higherBetter = {"news_score": 1, "population": 1, "area": 1, "gdp": 1, "gdp_per_capita": 1, "hdi": 1, "life_expectancy": 1, "happiness": 1, "democracy": 1, "press": 1, "cpi": 1, "gpi": 1, "approval": 1, "internet_pct": 1, "edu": 1, "english": 1, "gender": 1, "fertility": 1, "health": 1, "renew": 1, "forest": 1, "rd": 1, "patents": 1, "tourism": 1, "nobel": 1, "netspeed": 1, "doctors": 1, "heritage": 1, "leave": 1, "independence": 1, "literacy": 1, "agri": 1, "languages": 1, "coffee": 1, "mcdonalds": 1, "elevation": 1, "police": 1, "beds": 1, "salary": 1, "meat": 1, "car_density": 1, "penetration": 1, "aviation": 1, "religion_div": 1, "beer": 1, "wine": 1, "chocolate": 1, "airports": 1, "startups": 1, "chess": 1, "nobel_per_capita": 1, "hdi_adj": 1, "books": 1, "nuclear_power": 1, "volcanoes": 1, "math_olympiad": 1, "urban_pop": 1, "median_age": 1, "energy_per_capita": 1, "electricity": 1, "reserves": 1, "exports": 1, "imports": 1, "govern_spend": 1, "tax_rev": 1, "military_personnel": 1, "line_length": 1, "olympic": 1, "basket": 1, "cricket": 1, "rugby": 1, "birth_rate": 1, "trump_approval": 1, "nato": 1, "worldcup_parts": 1, "olympic_gold": 1, "olympic_per_cap": 1, "davis_cup": 1, "marathon_elite": 1, "startup_rate": 1, "min_wage": 1, "pisa_math": 1, "pisa_science": 1, "pisa_reading": 1, "phd_per_cap": 1, "research_pub": 1, "recycling": 1, "park_area": 1, "immigration": 1, "refugees": 1, "lgbtq_rights": 1, "g5_coverage": 1, "ai_research": 1, "space_launch": 1, "arms_export": 1, "peacekeeping": 1, "intangible": 1, "film_prod": 1, "michelin": 1, "game_market": 1, "tea_consume": 1, "rice_consume": 1, "holidays": 1, "influencers": 1, "festivals": 1, "street_food": 1, "cat_own": 1, "dog_own": 1, "marriage_age_m": 1, "marriage_age_f": 1, "marriage_rate": 1, "tertiary": 1, "school_yrs": 1, "universities": 1, "onlyfans": 1, "adult_films": 1, "porn_search": 1, "welfare_spend": 1, "unemp_benefit": 1, "pension_rate": 1, "parental_leave": 1, "fortune500": 1, "unicorns": 1, "vc_funding": 1, "business_ease": 1, "stock_market": 1};
      data.forEach(function(row){
        fields.forEach(function(f){
          if(row[f]==null) row[f] = higherBetter[f] ? NEG_SENTINEL : NULL_SENTINEL;
        });
      });
      // Progressive rendering: load in chunks to avoid freezing browser
      var CHUNK = 20, idx = 0;
      // Clear initial sort during chunked load (addData triggers sort otherwise)
      table.setSort([]);
      function loadChunk() {
        var chunk = data.slice(idx, idx + CHUNK);
        if (idx === 0) {
          table.setData(chunk);
        } else {
          table.addData(chunk);
        }
        idx += CHUNK;
        if (idx < data.length) {
          requestAnimationFrame(loadChunk);
        } else {
          // All loaded — apply default sort (news_score desc)
          table.setSort('news_score','desc');
          setTimeout(function(){ var top = table.getRows()[0]; layoutColumns(top ? top.getData().news_columns : []); }, 500);
        }
      }
      loadChunk();

      // ── Live news polling: fetch fresh data every 30s, update in-place ──
      var LIVE_INTERVAL = 30000;
      var newsFields = ['news_score','news_title','news_url','news_image','news_source','news_age','news_columns'];
      function pollNews() {
        fetch('data/countries.json?t=' + Date.now())
          .then(function(r){return r.json()})
          .then(function(fresh) {
            var rows = table.getRows(), codeIdx = {};
            for (var i = 0; i < rows.length; i++) {
              codeIdx[(rows[i].getData().country_code||'').toUpperCase()] = i;
            }
            var changed = false;
            for (var j = 0; j < fresh.length; j++) {
              var code = (fresh[j].country_code||'').toUpperCase();
              var idx = codeIdx[code];
              if (idx === undefined) continue;
              var row = rows[idx], d = row.getData();
              for (var k = 0; k < newsFields.length; k++) {
                var f = newsFields[k];
                if (d[f] !== fresh[j][f]) { d[f] = fresh[j][f]; changed = true; }
              }
            }
            if (changed && !rotationPaused) {
              // Re-sort by news_score to reflect new rankings
              table.setSort('news_score', 'desc');
              setTimeout(function(){ var top = table.getRows()[0]; layoutColumns(top ? top.getData().news_columns : []); }, 500);
            }
          }).catch(function(){});
      }
      setInterval(pollNews, LIVE_INTERVAL);

    // ── Crosshair: column highlight on hover ──
    (function(){
      var lastCol = null;
      var tableEl = document.querySelector('#example-table');
      if(!tableEl) return;
      tableEl.addEventListener('mouseover', function(e){
        var cell = e.target.closest('.tabulator-cell');
        if(!cell) return;
        var field = cell.getAttribute('tabulator-field');
        if(!field || field === 'country_code' || field === lastCol) return;
        document.querySelectorAll('.tabulator-cell.col-hover').forEach(function(c){c.classList.remove('col-hover');});
        document.querySelectorAll('.tabulator-cell[tabulator-field="'+field+'"]').forEach(function(c){c.classList.add('col-hover');});
        lastCol = field;
      });
      tableEl.addEventListener('mouseleave', function(){
        document.querySelectorAll('.tabulator-cell.col-hover').forEach(function(c){c.classList.remove('col-hover');});
        lastCol = null;
      });
    })();
      
      // ── TOP 3 행 + 핫셀 하이라이트 (소팅 시마다 갱신) ──
      function refreshTopRows(){
        var rows=table.getRows(), sortField=(table.getSorters()[0]||{}).field;
        rows.forEach(function(r,i){
          var el=r.getElement();
          el.classList.remove('top-1','top-2','top-3');
          el.querySelectorAll('.hot-cell').forEach(function(c){c.classList.remove('hot-cell');});
          if(i<3){
            el.classList.add('top-'+(i+1));
            if(sortField){
              var cell=r.getCell(sortField);
              if(cell) cell.getElement().classList.add('hot-cell');
            }
          }
        });
      }
      table.on("dataSorted", refreshTopRows);
      table.on("dataLoaded", refreshTopRows);
      setTimeout(refreshTopRows, 800);
    }).catch(function(err){console.error(err);table.setData([]);});

    // Detail panel
    var detailOpen=false;
    function openDetail(data){var code=(data.country_code||'').toUpperCase(),name=data.country_name_en||'',isEntity=(name.indexOf('*')===0);if(isEntity){var prefixLen=name.match(/^\*+/)[0].length,cleanName=name.replace(/^\*+/,''),entityType=prefixLen===3?'단체':prefixLen===2?'인물':'기업',icon=prefixLen===3?'🏟️':prefixLen===2?'⭐':'🏢';var items=[['Type',icon+' '+entityType],['HQ',data.capital_en||'-']];if(data.country_summary)items.push(['Description',data.country_summary]);if(data.subcontinent)items.push(['Category',data.subcontinent]);if(data.independence)items.push(['Founded',data.independence]);if(data.head_of_state_en)items.push(['Leader',data.head_of_state_en]);var numFields=[['Population','population'],['GDP','gdp'],['GDP/capita','gdp_per_capita'],['Life Exp','life_expectancy'],['Patents','patents'],['R&D','rd'],['Tourism','tourism'],['Film','film_prod'],['Festivals','festivals'],['FIFA Rank','fifa_ranking'],['Olympic','olympic'],['Nobel','nobel']];for(var n=0;n<numFields.length;n++){var lb=numFields[n][0],f=numFields[n][1];if(!N(data[f])){var v=data[f],rk=data[f+'_rank'],vs=typeof v==='number'?(v>=1000?fmtNumber(v):v.toLocaleString()):v;items.push([lb,vs+(rk?' (#'+rk+')':'')]);}}var ih='';for(var i=0;i<items.length;i++)ih+='<div class="detail-item"><span class="detail-label">'+items[i][0]+'</span><span class="detail-value">'+items[i][1]+'</span></div>';document.getElementById('detailMap').innerHTML='';document.getElementById('detailMap').style.display='none';document.getElementById('detailBody').innerHTML='<div class="detail-country">'+cleanName+'</div><div class="detail-native" style="font-size:12px;color:var(--text-muted);">'+entityType+'</div><div class="detail-grid">'+ih+'</div><div class="detail-comments"><div class="comment-form"><input type="text" class="comment-nick" id="commentNick" placeholder="이름" maxlength="20"><input type="text" class="comment-input" id="commentInput" placeholder="댓글... Enter로 전송"><button class="comment-submit" id="commentSubmit">Post</button></div><div class="comments-list" id="commentsList"></div></div>';document.getElementById('detailPanel').style.display='block';detailOpen=true;return;}lat=data.lat,lon=data.lon,mapHtml='';if(lat!=null&&lon!=null){var bbox=(lon-8)+'%2C'+(lat-5)+'%2C'+(lon+8)+'%2C'+(lat+5);mapHtml='<div class="detail-map"><iframe width="100%" height="170" frameborder="0" scrolling="no" src="https://www.openstreetmap.org/export/embed.html?bbox='+bbox+'&amp;layer=mapnik&amp;marker='+lat+'%2C'+lon+'" style="border:none;border-radius:8px;"></iframe></div>';}else{mapHtml='<div class="detail-map" style="display:flex;align-items:center;justify-content:center;height:120px;background:var(--bg-secondary);border-radius:8px;color:var(--text-muted);">🗺️ Map unavailable</div>';}
    var items=[['Native Name',data.country_name_local||'-'],['Capital',data.capital_en+(data.capital_local?' / '+data.capital_local:'')],['Continent',data.continent+(data.subcontinent?', '+data.subcontinent:'')],['Population',(!N(data.population)?I18N.formatNumber(data.population):'-')+' (#'+(data.population_rank||'-')+')'],['Area',(data.area?I18N.formatNumber(data.area)+' km²':'-')+' (#'+(data.area_rank||'-')+')'],['Head of State',data.head_of_state_en||'-'],['OECD',data.oecd_member==='Yes'?'✓ '+data.oecd_year:'—'],['BRICS',data.brics_member==='Yes'?'✓ '+data.brics_year:'—'],['GDP',!N(data.gdp)?'$'+I18N.formatNumber(data.gdp/1e6)+'B':'-'],['HDI',!N(data.hdi)?data.hdi.toFixed(3):'-'],['Life Exp.',!N(data.life_expectancy)?data.life_expectancy.toFixed(1)+' yr':'-'],['Happiness',!N(data.happiness)?data.happiness.toFixed(2):'-'],['Ethnic',data.ethnic||'-'],['Anthem',data.national_anthem_en||'-']];
    var ih='';for(var i=0;i<items.length;i++)ih+='<div class="detail-item"><span class="detail-label">'+items[i][0]+'</span><span class="detail-value'+(items[i][0]==='Anthem'?' anthem-link':'')+'"'+(items[i][0]==='Anthem'?' data-code="'+code+'" style="cursor:pointer;text-decoration:underline;color:var(--accent);"':'')+'>'+items[i][1]+'</span></div>';
    // Layout: Country → Info → Map → Comments
    document.getElementById('detailMap').innerHTML='';
    document.getElementById('detailMap').style.display='none';
    document.getElementById('detailBody').innerHTML=
      '<div class="detail-country">'+(I18N.countryName(code)||data.country_name_en)+'</div><div class="detail-native">'+(data.country_name_local||'')+'</div>'+
      '<div class="detail-grid">'+ih+'</div>'+
      mapHtml+
      '<div class="detail-comments">'+
        '<div class="comment-form">'+
          '<input type="text" class="comment-nick" id="commentNick" placeholder="이름" maxlength="20">'+
          '<input type="text" class="comment-input" id="commentInput" placeholder="댓글... Enter로 전송">'+
          '<button class="comment-submit" id="commentSubmit">Post</button>'+
        '</div>'+
        '<div class="comments-list" id="commentsList"></div>'+
      '</div>';
    document.getElementById('detailPanel').style.display='block';detailOpen=true;}
    function closeDetail(){document.getElementById('detailPanel').style.display='none';document.getElementById('detailMap').style.display='';detailOpen=false;}
    document.getElementById('detailPanel').addEventListener('click',function(e){if(e.target===this)closeDetail();});
    document.getElementById('detailClose').addEventListener('click',closeDetail);
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){document.getElementById('anthemModal').style.display='none';closeDetail();}});
    table.on("cellClick",function(e,cell){
      var f=cell.getColumn().getField();
      if(f==='country_code'){
        var rowPos = cell.getRow().getPosition();
        if (rowPos === 0) {
          // Header click already handled by headerClick — skip
          return;
        } else {
          openDetail(cell.getRow().getData());
        }
      } else if(f==='country_name_en'){
        // 국가명 클릭 → 강한 순위순 컬럼 재정렬
        var d=cell.getRow().getData(), code=d.country_code;
        // 모든 열을 해당 국가의 rank 기준으로 정렬
        var cols=table.getColumnDefinitions().filter(function(c){
          return c.field && c.field!=='country_code' && c.field!=='country_name_en';
        });
        cols.sort(function(a,b){
          var ra=d[a.field+'_rank']!=null?parseInt(d[a.field+'_rank']):9999;
          var rb=d[b.field+'_rank']!=null?parseInt(d[b.field+'_rank']):9999;
          return ra-rb;
        });
        var fields=['country_code','country_name_en'].concat(cols.map(function(c){return c.field;}));
        reorderColumns(fields);
        // 소팅도 첫 컬럼 기준으로
        var topField=cols[0].field;
        table.setSort(topField,'asc');
        highlightColumn(topField);
        activeSortField=topField; activeSortDir='asc';
      }
    });

    // Anthem modal - open via event delegation
    var anthemsData = {};
    fetch('data/anthems.json').then(function(r){return r.json()}).then(function(d){anthemsData = d;});
    document.getElementById('detailBody').addEventListener('click', function(e) {
      var el = e.target.closest('.anthem-link');
      if (!el) return;
      var code = el.getAttribute('data-code');
      openAnthem(code);
    });
    function openAnthem(code) {
      var a = anthemsData[code];
      if (!a) return;
      document.getElementById('anthemHeader').innerHTML =
        '<div class="anthem-title">'+esc(a.title_en)+'</div>'+
        '<div class="anthem-sub">'+esc(a.title_local)+'</div>'+
        '<div class="anthem-meta">Language: '+esc(a.lang)+' | Adopted: '+a.year+'</div>';
      var body = '';
      if (a.lyrics && a.lyrics.length > 3) {
        var lines = a.lyrics.split('\n');
        var pLines = (a.pronunciation_ko || '').split('\n');
        var merged = '';
        for (var j = 0; j < Math.max(lines.length, pLines.length); j++) {
          if (lines[j]) merged += '<div class="anthem-lyrics">'+esc(lines[j])+'</div>';
          if (pLines[j]) merged += '<div class="anthem-pronounce">'+esc(pLines[j])+'</div>';
        }
        body += '<div class="anthem-section"><h4>📜 Lyrics / 🇰🇷 발음</h4>'+merged+'</div>';
      }
      if (a.youtube && a.youtube.includes('youtube')) {
        var vid = '';
        var m = a.youtube.match(/(?:v=|youtu\.be\/|embed\/)([^&\?\/]+)/);
        if (m) vid = m[1];
        if (vid) body += '<div class="anthem-section"><h4>🎬 Video</h4><iframe class="anthem-video" src="https://www.youtube.com/embed/'+vid+'" frameborder="0" allowfullscreen></iframe></div>';
        else body += '<div class="anthem-section"><h4>🎬 Video</h4><div style="text-align:center;padding:30px;"><a href="https://www.youtube.com/results?search_query='+encodeURIComponent(esc(a.title_en)+' '+esc(a.title_local)+' national anthem')+'" target="_blank" style="color:var(--accent);text-decoration:underline;">▶ YouTube에서 검색하기</a></div></div>';
      }
      document.getElementById('anthemBody').innerHTML = body;
      document.getElementById('anthemModal').style.display = 'block';
    }
    function closeAnthem(){document.getElementById('anthemModal').style.display='none';document.getElementById('anthemBody').innerHTML='';}
    document.getElementById('anthemClose').addEventListener('click',closeAnthem);
    document.getElementById('anthemOverlay').addEventListener('click',closeAnthem);

    // Comments: localStorage-based per-country
    var STORAGE_KEY = 'rankerage_comments_';
    var shadowProfiles = {};
    var trustLevels = {};
    fetch('data/shadows/shadow_index.json').then(function(r){return r.json()}).then(function(d){shadowProfiles = d;});
    fetch('data/shadows/trust_levels.json').then(function(r){return r.json()}).then(function(d){trustLevels = d;});
    
    function getShadowFingerprint(nick) {
      // Anonymous but consistent: hash of nickname + browser fingerprint
      var uid = localStorage.getItem('__rs_id') || (Date.now().toString(36) + Math.random().toString(36).substr(2));
      localStorage.setItem('__rs_id', uid);
      var hash = 0, str = nick + ':' + uid;
      for (var i = 0; i < str.length; i++) { hash = ((hash<<5)-hash)+str.charCodeAt(i); hash|=0; }
      return nick + ':' + Math.abs(hash).toString(36).substr(0,6);
    }
    
    function getShadowLevel(nick) {
      var fp = getShadowFingerprint(nick);
      var profile = shadowProfiles[fp];
      if (!profile) return {level:'visitor',badge:'🥉'};
      var comments = profile.comments || 0;
      var level = 'visitor', badge = '🥉';
      for (var l in trustLevels) {
        if (comments >= trustLevels[l].min) { level = l; badge = trustLevels[l].badge; }
      }
      return {level:level, badge:badge, comments:comments, countries:profile.countries_active||0, fixes:profile.data_fixes||0};
    }
    
    function shadowBadge(nick) {
      var s = getShadowLevel(nick);
      return '<span class="shadow-badge" title="'+s.level+' | '+s.comments+' comments, '+s.countries+' countries, '+s.fixes+' fixes">'+s.badge+'</span>';
    }

    function loadComments(code) {
      try { return JSON.parse(localStorage.getItem(STORAGE_KEY + code) || '[]'); } catch(e) { return []; }
    }
    function saveComments(code, arr) {
      localStorage.setItem(STORAGE_KEY + code, JSON.stringify(arr.slice(-50))); // keep last 50
    }
    function renderComments(code) {
      var html = '<div class="detail-comments"><div class="comments-title">💬 Comments</div><div class="comments-list" id="commentsList">';
      var comments = loadComments(code);
      if (!comments.length) html += '<div style="color:var(--text-muted);font-size:10px;padding:8px 0;">No comments yet — be the first!</div>';
      else comments.forEach(function(c) {
        var t = new Date(c.time);
        html += '<div class="comment-item"><span class="comment-nick-text">'+esc(c.nick)+'</span><span class="comment-time">'+fmtTime(t)+'</span><div class="comment-body">'+esc(c.text)+'</div></div>';
      });
      html += '</div><div class="comment-form">';
      html += '<input type="text" class="comment-nick" id="commentNick" placeholder="Nickname" maxlength="20">';
      html += '<textarea class="comment-input" id="commentInput" placeholder="Write a comment..." rows="2"></textarea>';
      html += '<button class="comment-submit" id="commentSubmit">Post</button>';
      html += '</div></div>';
      return html;
    }
    function esc(s) { return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
    function fmtTime(d) {
      var now = new Date(), diff = (now - d) / 1000;
      if (diff < 60) return 'just now';
      if (diff < 3600) return Math.floor(diff/60)+'m ago';
      if (diff < 86400) return Math.floor(diff/3600)+'h ago';
      return d.toLocaleDateString();
    }
    var currentCountry = null;
    // Refresh comments in the inline section
    var _openDetailOrig2 = openDetail;
    openDetail = function(data) {
      _openDetailOrig2(data);
      // Reset for new country
      var prev = currentCountry;
      currentCountry = (data.country_code||'').toUpperCase();
      if (prev !== currentCountry) {
        document.getElementById('commentsList').innerHTML = '';
        document.getElementById('commentInput').value = '';
      }
      refreshCommentList(currentCountry);
      document.getElementById('commentSubmit').onclick = function() {
        if (!currentCountry) return;
        var nick = document.getElementById('commentNick').value.trim() || 'Anonymous';
        var text = document.getElementById('commentInput').value.trim();
        if (!text) return;
        var comments = loadComments(currentCountry);
        comments.push({ nick: nick, text: text, time: Date.now(), reactions: {} });
        saveComments(currentCountry, comments);
        document.getElementById('commentInput').value = '';
        refreshCommentList(currentCountry);
        updateCommentBadge(currentCountry);
      };
      document.getElementById('commentInput').onkeydown = function(e) {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); document.getElementById('commentSubmit').click(); }
      };
      // Emoji reaction handler (delegated)
      document.getElementById('detailBody').addEventListener('click', function(e) {
        var btn = e.target.closest('.reaction-btn');
        if (!btn || !currentCountry) return;
        var idx = parseInt(btn.getAttribute('data-idx'));
        var emoji = btn.getAttribute('data-emoji');
        var comments = loadComments(currentCountry);
        if (comments[idx]) {
          comments[idx].reactions = comments[idx].reactions || {};
          comments[idx].reactions[emoji] = (comments[idx].reactions[emoji] || 0) + 1;
          saveComments(currentCountry, comments);
          refreshCommentList(currentCountry);
        }
      });
      updateCommentBadge(currentCountry);
    };
    function refreshCommentList(code) {
      var list = document.getElementById('commentsList');
      if (!list) return;
      var comments = loadComments(code);
      // Auto-seed: if no comments, generate one
      if (!comments.length) {
        seedComment(code);
        comments = loadComments(code);
      }
      var html = '';
      comments.forEach(function(c, i) {
        var t = new Date(c.time);
        var r = c.reactions || {};
        var rx = ['👍','❤️','😂','😮'].map(function(e) {
          var cnt = r[e] || 0;
          return '<span class="reaction-btn" data-idx="'+i+'" data-emoji="'+e+'" style="cursor:pointer;padding:1px 4px;margin-left:2px;border-radius:3px;font-size:11px;'+(cnt?'background:rgba(224,200,124,0.15);':'')+'">'+e+(cnt?' <span style="color:#8892b0;font-size:9px;">'+cnt+'</span>':'')+'</span>';
        }).join('');
        html += '<div class="comment-item"><span class="comment-nick-text">'+esc(c.nick)+'</span><span class="comment-time">'+fmtTime(t)+'</span><div class="comment-body">'+esc(c.text)+'</div><div style="margin-top:3px;">'+rx+'</div></div>';
      });
      list.innerHTML = html || '<div style="color:var(--text-muted);font-size:10px;padding:8px 0;">No comments yet — be the first!</div>';
    }
    function seedComment(code) {
      // Only seed if truly no comments exist
      var existing = loadComments(code);
      if (existing.length > 0) return;
      var row = table.getData().find(function(r) { return (r.country_code||'').toUpperCase() === code; });
      if (!row) return;
      var seeds = [];
      if (row.approval && row.approval_rank <= 5) seeds.push({nick:'DataBot',text:'와... 지도자 지지율이 세계 '+row.approval_rank+'위라니! 😮'});
      if (row.fifa_ranking && row.fifa_ranking_rank <= 5) seeds.push({nick:'DataBot',text:'축구 랭킹 세계 '+row.fifa_ranking_rank+'위! 이번 월드컵 기대된다 ⚽'});
      if (row.happiness && row.happiness_rank <= 5) seeds.push({nick:'DataBot',text:'행복지수 세계 '+row.happiness_rank+'위 🥰 여기 살고 싶다...'});
      if (row.hdi && row.hdi_rank <= 5) seeds.push({nick:'DataBot',text:'HDI 세계 '+row.hdi_rank+'위라니! 살기 좋은 나라네요 👏'});
      if (row.gdp && row.gdp_rank >= 150 && row.population && row.population_rank <= 30) seeds.push({nick:'DataBot',text:'인구는 많은데 GDP는... 경제 성장이 시급해 보이네요 📉'});
      if (!seeds.length) seeds.push({nick:'DataBot',text:'이 나라의 순위 데이터, 어떤 게 가장 놀라웠나요? 💬'});
      var s = seeds[Math.floor(Math.random() * seeds.length)];
      saveComments(code, [{ nick: s.nick, text: s.text, time: Date.now() - 86400000, reactions: {} }]);
    }
    function updateCommentBadge(code) {
      var comments = loadComments(code);
      var cnt = comments.length;
      // Update flag tooltip
      var row = table.getData().find(function(r) { return (r.country_code||'').toUpperCase() === code; });
      if (row) {
        var orig = row.country_summary || '';
        var badge = cnt ? ' 💬'+cnt : '';
        row.country_summary = orig.replace(/ 💬\d+/,'') + badge;
      }
    }

    // Language
    function buildLangSelectors(){var parts=I18N.buildSelectorHTML().split('|||');document.getElementById('locale1').innerHTML=parts[0];document.getElementById('locale2').innerHTML=parts[1];try{var s=JSON.parse(localStorage.getItem('rankerage_prefs')||'{}');if(s.email)document.getElementById('userEmail').value=s.email;}catch(e){}}
    buildLangSelectors();I18N.applyUI();
    document.getElementById('langBtn').addEventListener('click',function(){document.getElementById('langModal').style.display='flex';});
    document.getElementById('modalClose').addEventListener('click',function(){document.getElementById('langModal').style.display='none';});
    document.getElementById('langModal').addEventListener('click',function(e){if(e.target===this)this.style.display='none';});
    document.getElementById('saveLang').addEventListener('click',function(){I18N.setLocales(document.getElementById('locale1').value,document.getElementById('locale2').value);try{var p=JSON.parse(localStorage.getItem('rankerage_prefs')||'{}');p.email=document.getElementById('userEmail').value.trim();localStorage.setItem('rankerage_prefs',JSON.stringify(p));}catch(e){}I18N.applyUI();table.setColumns(cols);document.getElementById('langModal').style.display='none';});

    // Add tooltips to all data columns (with country name)
    cols.forEach(function(col) {
      if (col.field === 'country_code' || col.field === 'country_name_en') return;
      var field = col.field;
      var title = col.title;
      col.tooltip = function(e, cell) {
        var d = cell.getRow().getData();
        var code = d.country_code;
        var cname = I18N.countryName(code, I18N.getLocale2()) || I18N.countryName(code) || d.country_name_en || '';
        var rank = d[field + '_rank'];
        var val = d[field];
        var valStr = (val === null || val === undefined) ? 'no data' : (typeof val === 'number' ? val.toLocaleString() : val);
        var rankStr = rank ? ' (Rank #' + rank + ')' : '';
        return cname + ' · ' + title + ': ' + valStr + rankStr;
      };
    });

    // Header tooltips + mobile long-press
    table.on("tableBuilt",function(){
      document.querySelectorAll(".tabulator-col-title").forEach(function(el){
        var col = el.closest(".tabulator-col");
        var field = col ? col.getAttribute("tabulator-field") : "";
        var tip = desc[field] || el.textContent.trim();
        if (!el.getAttribute("title")) el.setAttribute("title", tip);
      });
    });

    // Trend chart for GDP, Population, Life Exp, GDP/cap
    var trendFields = {"gdp":1,"gdp_per_capita":1,"population":1,"life_expectancy":1,"urban_pop":1,"internet_pct":1,"military_pct":1,"health":1,"fertility":1,"forest":1,"edu":1,"rd":1,"poverty":1};
    var historyData = null;
    var chartInstance = null;
    var chartModal = document.getElementById("chartModal");
    var chartCanvas = document.getElementById("trendChart");
    var chartTitleEl = document.getElementById("chartTitle");
    var chartClose = document.getElementById("chartClose");
    var chartOverlay = document.getElementById("chartOverlay");

    chartClose.addEventListener("click", closeChart);
    chartOverlay.addEventListener("click", closeChart);
    document.addEventListener("keydown", function(e) { if (e.key === 'Escape') closeChart(); });

    function closeChart() {
      chartModal.style.display = 'none';
      if (chartInstance) { chartInstance.destroy(); chartInstance = null; }
    }

    function showTrend(field, rowData) {
      if (!historyData || !historyData[field]) return;
      var code = (rowData.country_code || '').toUpperCase();
      var hist = historyData[field][code.toLowerCase()];
      if (!hist) return;
      var years = Object.keys(hist).sort();
      var values = years.map(function(y) { return hist[y]; });
      var name = I18N.countryName(code) || rowData.country_name_en;
      
      // Compute rank change from history data
      var firstYear = years[0], lastYear = years[years.length-1];
      var allData = historyData[field];
      var rankFirst = 1, rankLast = 1;
      try {
        var sortedFirst = []; var sortedLast = [];
        for (var cc in allData) {
          if (allData[cc][firstYear] != null) sortedFirst.push({c:cc, v:allData[cc][firstYear]});
          if (allData[cc][lastYear] != null) sortedLast.push({c:cc, v:allData[cc][lastYear]});
        }
        var desc = (["fifa_ranking","unemp","debt","poverty","obesity","alcohol","pm25","co2","suicide","prison","tz","murder","nuclear","divorce","inflation","gas_price","death_rate","infant_mortality","maternal_mortality","earthquakes","students_per_teacher","workhours"]).indexOf(field) < 0;
        sortedFirst.sort(function(a,b){return desc ? b.v - a.v : a.v - b.v;});
        sortedLast.sort(function(a,b){return desc ? b.v - a.v : a.v - b.v;});
        rankFirst = sortedFirst.findIndex(function(x){return x.c === code.toLowerCase();}) + 1;
        rankLast = sortedLast.findIndex(function(x){return x.c === code.toLowerCase();}) + 1;
      } catch(e){ rankFirst = '-'; rankLast = '-'; }
      
      var rankChange = '';
      if (rankFirst && rankLast && typeof rankFirst === 'number') {
        var diff = rankFirst - rankLast;
        if (diff > 0) rankChange = ' ↑' + diff + ' (#' + rankFirst + '→#' + rankLast + ')';
        else if (diff < 0) rankChange = ' ↓' + Math.abs(diff) + ' (#' + rankFirst + '→#' + rankLast + ')';
        else rankChange = ' = #' + rankFirst;
      }
      var title = (colLabels[field] || field) + ': ' + name + ' ' + rankChange;
      
      chartTitleEl.textContent = title;
      chartModal.style.display = 'block';
      if (chartInstance) chartInstance.destroy();
      var ctx = chartCanvas.getContext('2d');
      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          labels: years,
          datasets: [{
            label: name,
            data: values,
            borderColor: '#e0c87c',
            backgroundColor: 'rgba(224,200,124,0.1)',
            borderWidth: 2,
            pointBackgroundColor: '#e0c87c',
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: true,
          plugins: { legend: { display: false } },
          scales: {
            x: { ticks: { color: '#8892b0', font: { size: 11 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
            y: { ticks: { color: '#8892b0', font: { size: 11 }, callback: function(v) { return v >= 1e9 ? (v/1e9).toFixed(1)+'B' : v >= 1e6 ? (v/1e6).toFixed(1)+'M' : v >= 1e3 ? (v/1e3).toFixed(0)+'K' : v; } }, grid: { color: 'rgba(255,255,255,0.08)' } }
          }
        }
      });
    }

    // Column labels for chart title
    var colLabels = {};
    cols.forEach(function(c) { colLabels[c.field] = c.title; });

    // Load history data and enable trend clicks
    fetch('data/history.json').then(function(r){return r.json()}).then(function(d){
      historyData = d;
      table.on("cellClick", function(e, cell) {
        var field = cell.getColumn().getField();
        if (trendFields[field]) showTrend(field, cell.getRow().getData());
      });
    });

    // Cell selection
    var isSelecting=false,startCell=null,lastCell=null,lastMouseY=0,SCROLL_SPEED=10,SCROLL_MARGIN=50;
    function autoScroll(){var h=document.querySelector(".tabulator-tableholder");if(!h)return;var r=h.getBoundingClientRect();if(lastMouseY<r.top+SCROLL_MARGIN)h.scrollTop-=SCROLL_SPEED;else if(lastMouseY>r.bottom-SCROLL_MARGIN)h.scrollTop+=SCROLL_SPEED;if(isSelecting)requestAnimationFrame(autoScroll);}
    document.querySelector("#example-table").addEventListener("mousedown",function(e){var c=e.target.closest(".tabulator-cell");if(!c)return;if(e.shiftKey||e.ctrlKey){e.preventDefault();e.stopPropagation();isSelecting=true;startCell=c;lastCell=c;clearSelection();requestAnimationFrame(autoScroll);}else{clearSelection();}});
    document.addEventListener("mousemove",function(e){if(!isSelecting||(!e.shiftKey&&!e.ctrlKey)){isSelecting=false;return;}lastMouseY=e.clientY;var c=document.elementFromPoint(e.clientX,e.clientY);if(c)c=c.closest(".tabulator-cell");if(c&&c!==lastCell){lastCell=c;updateSelection(startCell,c);}});
    document.addEventListener("mouseup",function(){isSelecting=false;startCell=null;lastCell=null;});
    function updateSelection(s,e){if(!s||!e)return;var rows=Array.from(document.querySelectorAll(".tabulator-row:not(.tabulator-header)"));var sr=s.closest(".tabulator-row"),er=e.closest(".tabulator-row");var si=rows.indexOf(sr),ei=rows.indexOf(er);var sc=Array.from(sr.children).indexOf(s),ec=Array.from(er.children).indexOf(e);var mr=Math.min(si,ei),Mr=Math.max(si,ei),mc=Math.min(sc,ec),Mc=Math.max(sc,ec);clearSelection();for(var i=mr;i<=Mr;i++){if(!rows[i])continue;var cells=Array.from(rows[i].children);for(var j=mc;j<=Mc;j++){if(cells[j])cells[j].classList.add("selected");}}}
    function clearSelection(){document.querySelectorAll(".tabulator-cell.selected").forEach(function(c){c.classList.remove("selected");});}
    document.addEventListener("keydown",function(e){if(e.ctrlKey&&e.key==="c"){var sel=document.querySelectorAll(".tabulator-cell.selected");if(!sel.length)return;var rows=new Map();sel.forEach(function(cell){var row=cell.closest(".tabulator-row");var idx=Array.from(row.parentElement.children).indexOf(row);if(!rows.has(idx))rows.set(idx,[]);rows.get(idx).push(cell.textContent.trim());});navigator.clipboard.writeText(Array.from(rows.values()).map(function(cells){return cells.join("\t");}).join("\n"));}else if(e.key==="Escape"){isSelecting=false;clearSelection();}});

    // ── 광고 행 삽입 (매 8행) ──
    var adInterval = 8;
    var adCount = 0;
    function insertAdRows() {
      // Remove old ad rows
      document.querySelectorAll('.tabulator-row.ad-row').forEach(function(r) { r.remove(); });
      var rows = table.getRows();
      if (rows.length < adInterval) return;
      for (var i = adInterval - 1; i < rows.length; i += adInterval + 1) {
        var refRow = rows[i];
        if (!refRow) break;
        var adRow = document.createElement('div');
        adRow.className = 'tabulator-row ad-row';
        adRow.style.cssText = 'height:90px;display:flex;align-items:center;justify-content:center;border-bottom:1px solid rgba(255,255,255,0.04);';
        adRow.innerHTML = '<div style="text-align:center;width:100%;padding:4px;">' +
          '<ins class="adsbygoogle" style="display:block;height:80px" ' +
          'data-ad-client="ca-pub-9060044387299153" ' +
          'data-ad-slot="9876543210" ' +
          'data-ad-format="horizontal" ' +
          'data-full-width-responsive="true"></ins></div>';
        refRow.getElement().after(adRow);
        adCount++;
      }
      // Trigger AdSense
      if (window.adsbygoogle && adCount > 0) {
        try { (window.adsbygoogle = window.adsbygoogle || []).push({}); } catch(e) {}
      }
    }

    // 소팅/데이터 변경 시마다 광고 재삽입
    var adDebounce = null;
    table.on("dataSorted", function() {
      if (adDebounce) clearTimeout(adDebounce);
      adDebounce = setTimeout(function() {
        insertAdRows();
        updateAdTargeting();
      }, 500);
    });
    table.on("dataLoaded", function() {
      setTimeout(insertAdRows, 500);
    });
    setTimeout(insertAdRows, 1000);

    // ── 타겟팅 키워드 업데이트 ──
    var currentMetric = 'population';
    var targetKeywords = {"gdp": "finance investing stocks economy business banking", "gdp_per_capita": "wealth income investing luxury", "population": "demographics census data analytics", "life_expectancy": "healthcare health insurance medical", "happiness": "wellness travel lifestyle happiness", "tourism": "travel tours flights hotels vacation", "edu": "education university online courses learning", "internet_pct": "internet broadband technology cloud", "coffee": "coffee cafe specialty coffee beans", "beer": "beer craft beer brewery alcohol", "olympic": "sports olympics fitness training", "fifa_ranking": "soccer football sports betting", "real_estate": "real estate property housing mortgage", "renew": "solar energy renewable green energy", "startup_rate": "startups business entrepreneurship venture capital", "military_pct": "defense military security aerospace", "forest": "environment nature conservation eco tourism"};
    var defaultKeywords = 'country comparison rankings data statistics world';

    function updateAdTargeting() {
      var sorter = table.getSorters()[0];
      var metric = sorter ? sorter.field : 'population';
      if (metric === currentMetric) return;
      currentMetric = metric;
      var keywords = targetKeywords[metric] || defaultKeywords;
      // 페이지 메타 키워드 업데이트 (AdSense 크롤러용)
      var metaKw = document.querySelector('meta[name="keywords"]');
      if (!metaKw) {
        metaKw = document.createElement('meta');
        metaKw.name = 'keywords';
        document.head.appendChild(metaKw);
      }
      metaKw.content = keywords;
      // GPT 패스백 (있는 경우)
      if (window.googletag) {
        window.googletag.pubads().setTargeting('metric', [metric]);
        window.googletag.pubads().setTargeting('keywords', keywords.split(' '));
      }
    }
  });
  // ── Unified column layout: single source of truth for column ordering ──
  var _reordering = false;
  function layoutColumns(focusCols) {
    // Move focus columns right after frozen cols (pos 3) using moveColumn
    focusCols = (focusCols||[]).filter(function(f){
      return table.getColumnDefinitions().some(function(c){return c.field===f;});
    });
    if (!focusCols.length) return;
    _reordering = true;
    var cols = table.getColumns();
    // Move in reverse so earlier columns stay earlier
    for (var i = focusCols.length - 1; i >= 0; i--) {
      var f = focusCols[i];
      var col = null;
      for (var j = 0; j < cols.length; j++) {
        if (cols[j].getField() === f) { col = cols[j]; break; }
      }
      if (col) {
        try { table.moveColumn(col, cols[2]); } catch(e) {}
        cols = table.getColumns();
      }
    }
    _reordering = false;
    localStorage.setItem('rankerage_col_order', JSON.stringify(cols.map(function(c){return c.getField();})));
  }
  function resetLayout() { if (_reordering) return; layoutColumns([]); }
  // Trigger on sort/load
  table.on('dataSorted', function() {
    var sf = (table.getSorters()[0]||{}).field;
    if (sf === 'news_score') {
      var top = table.getRows()[0];
      setTimeout(function(){ layoutColumns(top ? top.getData().news_columns : []); }, 400);
    } else {
      resetLayout();
    }
  });
  table.on('dataLoaded', function() {
    setTimeout(function(){ layoutColumns([]); }, 600);
  });

  // ── HARD TEST: move population to after Trend at t+3s to verify moveColumn API ──
  setTimeout(function(){
    var cols = table.getColumns();
    var newsCol = cols[2]; // news_score
    for (var i = 0; i < cols.length; i++) {
      if (cols[i].getField() === 'population') {
        table.moveColumn(cols[i], newsCol);
        break;
      }
    }
  }, 3000);

  // ── Auto-rotation: table comes alive ──
  var autoRotate = true;
  var rotationInterval = 45000;
  var rotationTimer = null;
  var rotationPaused = false;
  var rotationColumns = [];
  var rotationIdx = 0;

  setTimeout(function buildRotationList() {
    var defs = table.getColumnDefinitions();
    for (var i = 0; i < defs.length; i++) {
      var f = defs[i].field;
      if (f && f !== 'country_code' && f !== 'country_name_en' && f !== 'news_score' && f !== 'election_days') {
        rotationColumns.push(f);
      }
    }
    for (var i = rotationColumns.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var tmp = rotationColumns[i]; rotationColumns[i] = rotationColumns[j]; rotationColumns[j] = tmp;
    }
  }, 5000);

  function doRotate() {
    if (!autoRotate || rotationPaused || rotationColumns.length === 0) return;
    var field = rotationColumns[rotationIdx % rotationColumns.length];
    rotationIdx++;
    table.setSort(field, 'asc');
    var col = table.getColumnDefinitions().find(function(c){return c.field===field;});
    var title = col ? col.title : field;
    var h = document.getElementById('rotate-hint');
    if (!h) { h = document.createElement('div'); h.id = 'rotate-hint'; h.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:rgba(224,200,124,0.95);color:#0a0e1a;padding:6px 18px;border-radius:20px;font-size:12px;font-weight:700;z-index:9999;pointer-events:none;'; document.body.appendChild(h); }
    h.style.opacity = '1';
    h.textContent = '🔄 ' + title + ' 순으로 정렬';
    setTimeout(function(){ h.style.opacity = '0'; }, 3000);
  }

  setTimeout(function(){ rotationTimer = setInterval(doRotate, rotationInterval); }, 15000);

  function pauseRotation() {
    rotationPaused = true;
  }
  function resumeRotation() {
    rotationPaused = false;
    var top = table.getRows()[0];
    setTimeout(function(){ layoutColumns(top ? top.getData().news_columns : []); }, 300);
  }
  // Trend column click (header or any cell) resumes
  table.on("headerClick", function(e, column){
    if (column && column.getField() === 'news_score') resumeRotation();
    else pauseRotation();
  });
  table.on("cellClick", function(e, cell){
    if (cell.getColumn().getField() === 'news_score') resumeRotation();
  });
  document.getElementById("search").addEventListener("input", function(){ pauseRotation(); });

})();
