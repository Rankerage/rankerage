// ============================================
// Rankerage.com — Main Table
// ============================================
(function() {
  'use strict';

  I18N.init().then(function() {
    var t = I18N.t;
    var desc = {};

    // Load descriptions
    fetch('data/descriptions.json').then(function(r){return r.json()}).then(function(d){desc = d;});

    var S = function(a,b){return a-b;};
    var NULL_SENTINEL = 999999;
    function N(v) { return v === null || v === undefined || v === NULL_SENTINEL; }
    function fmtNumber(n) { if (N(n)) return '-'; if (n >= 1e9) return (n / 1e9).toFixed(1)+'B'; if (n >= 1e6) return (n / 1e6).toFixed(1)+'M'; if (n >= 1e3) return (n / 1e3).toFixed(1)+'K'; return I18N.formatNumber(n); }
    function rankBadge(r) { if(!r)return'<span style="display:inline-block;width:26px;"></span>';var n=parseInt(r),c='#8892b0';if(n<=3)c='#f0a04b';else if(n<=10)c='#5b8def';else if(n<=20)c='#3fb68b';return'<span style="color:'+c+';font-weight:700;font-size:11px;">#'+n+'</span>'; }
    function numberCell(r,v) { return'<div style="display:flex;align-items:center;width:100%;"><span style="flex:0 0 26px;text-align:left;">'+(r?rankBadge(r):'')+'</span><span style="flex:1;text-align:right;font-family:\'JetBrains Mono\',Consolas,monospace;font-size:10.5px;white-space:nowrap;">'+v+'</span></div>'; }
    function suffix(n) { n=parseInt(n);if(!n)return'';return['th','st','nd','rd'][(n%100>10&&n%100<14)?0:(n%10>3?0:n%10)]||'th'; }

    var cols = [
      // Flag
      { title:"",field:"country_code",width:44,frozen:true,headerHozAlign:"center",hozAlign:"center",
        formatter:function(c){var code=(c.getValue()||'??').toUpperCase(),hash=0;for(var i=0;i<code.length;i++)hash=code.charCodeAt(i)+((hash<<5)-hash);var hue=Math.abs(hash)%360,sat=40+(Math.abs(hash>>4)%50),lit=25+(Math.abs(hash>>12)%25),bg='hsl('+hue+','+sat+'%,'+lit+'%)';return'<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;"><span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:15px;border-radius:3px;overflow:hidden;background:'+bg+';box-shadow:0 1px 2px rgba(0,0,0,0.3);flex-shrink:0;"><img src="https://flagcdn.com/16x12/'+code.toLowerCase()+'.png" width="16" height="12" style="display:block;" onerror="this.remove();"></span></div>';},
        tooltip:function(e,c){return c.getRow().getData().country_summary;}},
      // Country
      { title:t('country'),field:"country_name_en",width:120,frozen:true,
        formatter:function(c){var d=c.getRow().getData(),code=d.country_code,name=I18N.countryName(code);return'<span style="display:inline-block;max-width:105px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">'+(name||d.country_name_en)+'</span>';},
        tooltip:function(e,c){var d=c.getRow().getData(),code=d.country_code,n2=I18N.countryName(code,I18N.getLocale2()),lo=d.country_name_local,p=[];if(n2&&n2!==d.country_name_en)p.push(n2);if(lo&&lo!==n2)p.push(lo);return p.join(' · ')||d.country_name_en;}},
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
      A(t('nobel'),"nobel",72),
    ];

    function A(title,field,w){return{title:title,field:field,width:w,sorter:S,
      headerTooltip:function(){return (desc[field]||title);},
      formatter:function(c){var d=c.getRow().getData(),v=d[field];return numberCell(d[field+'_rank'],!N(v)?fmtNumber(v):'-');}};}
    function H(title,field,w){return{title:title,field:field,width:w,sorter:S,
      headerTooltip:function(){return (desc[field]||title);},
      formatter:function(c){var d=c.getRow().getData(),v=d[field];return numberCell(d[field+'_rank'],!N(v)?fmtNumber(v):'-');}};}
    function E(field,w){return{title:t('election'),field:field,width:w,sorter:S,
      headerTooltip:function(){return (desc[field]||t('election'));},
      formatter:function(c){var d=c.getRow().getData(),dt=d.election_date;if(!dt)return numberCell(null,'-');var p=dt.split('-'),s=p[1]+'/'+p[2];if(d.election_days<0)return numberCell(null,'✓');return numberCell(d.election_rank,s);}};}

    // Special formatters for non-standard value types
    cols.forEach(function(col){
      if(col.field==="gdp") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gdp_rank,d.gdp?'$'+fmtNumber(d.gdp):'-');};
      if(col.field==="gdp_per_capita") col.formatter=function(c){var d=c.getRow().getData();return numberCell(d.gdp_per_capita_rank,d.gdp_per_capita?'$'+I18N.formatNumber(d.gdp_per_capita):'-');};
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
      height:"100vh",layout:"fitDataFill",data:[],initialSort:[{column:"population",dir:"desc"}],columns:cols,
      pagination:false,movableColumns:false,virtualDom:true,tooltips:true,tooltipDelay:150,rowHover:true,headerVisible:true,
      placeholder:'<div style="padding:40px;text-align:center;color:#545d7a;"><div style="font-size:48px;">🌍</div><div style="font-size:16px;font-weight:600;">'+t('loading')+'</div></div>',
      sortMode:"single",selectable:false,selectableRows:false,selectableCells:false,clipboard:true,selectableRangeMode:"click",
      clipboardCopyConfig:{columnHeaders:false,columnGroups:false,rowGroups:false,columnCalcs:false}
    });

    // Search: find ranking by name
    var searchInput = document.getElementById("search");
    var dropdown = document.getElementById("searchDropdown");
    var allColumns = cols;

    searchInput.addEventListener("input", function() {
      var q = this.value.trim().toLowerCase();
      if (q.length < 1) { dropdown.style.display = 'none'; return; }
      var matches = allColumns.filter(function(c) {
        var title = (c.title || '').toLowerCase();
        return title.indexOf(q) !== -1;
      });
      if (!matches.length) { dropdown.style.display = 'none'; return; }
      dropdown.innerHTML = matches.map(function(c, i) {
        var title = c.title;
        var hl = title.replace(new RegExp('('+q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'), '<strong>$1</strong>');
        return '<div class="search-dropdown-item" data-field="'+c.field+'">'+hl+'</div>';
      }).join('');
      dropdown.style.display = 'block';
    });

    dropdown.addEventListener("click", function(e) {
      var item = e.target.closest(".search-dropdown-item");
      if (!item) return;
      var field = item.getAttribute("data-field");
      // Sort by that column
      table.setSort(field, "desc");
      // Scroll to make the column visible
      var header = document.querySelector('.tabulator-col[data-field="'+field+'"]');
      if (header) header.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      dropdown.style.display = 'none';
      searchInput.value = item.textContent.replace(/<[^>]*>/g,'').trim();
    });

    searchInput.addEventListener("keydown", function(e) {
      if (e.key === 'Escape') { dropdown.style.display = 'none'; this.blur(); }
      if (e.key === 'Enter') {
        var first = dropdown.querySelector(".search-dropdown-item");
        if (first) first.click();
      }
    });

    searchInput.addEventListener("blur", function() {
      setTimeout(function() { dropdown.style.display = 'none'; }, 150);
    });

    // Load data
    fetch('data/countries.json').then(function(r){return r.json()}).then(function(data){
      // Replace null with sentinel so Tabulator's number sorter puts them last
      var fields = ["population","area","population_density","gdp","gdp_per_capita","hdi",
        "life_expectancy","happiness","fifa_ranking","cpi","gpi","internet_pct","military_pct",
        "democracy","press","unemp","debt","poverty","rd","patents","edu","english","gender",
        "fertility","health","obesity","alcohol","pm25","co2","forest","renew","nuclear","murder",
        "tourism","olympic","fifa_w","basket","cricket","rugby","nobel","approval"];
      data.forEach(function(row){fields.forEach(function(f){if(row[f]==null)row[f]=NULL_SENTINEL;});});
      table.setData(data);setTimeout(function(){var h=document.querySelector('.scroll-hint');if(h){h.style.opacity='0';setTimeout(function(){if(h)h.remove();},500);}},6000);
    }).catch(function(err){console.error(err);table.setData([]);});

    // Detail panel
    var detailOpen=false;
    function openDetail(data){var code=(data.country_code||'').toUpperCase(),lat=data.lat,lon=data.lon,mapHtml='';if(lat!=null&&lon!=null){var bbox=(lon-8)+'%2C'+(lat-5)+'%2C'+(lon+8)+'%2C'+(lat+5);mapHtml='<iframe width="100%" height="220" frameborder="0" scrolling="no" src="https://www.openstreetmap.org/export/embed.html?bbox='+bbox+'&amp;layer=mapnik&amp;marker='+lat+'%2C'+lon+'" style="border:none;border-radius:12px 12px 0 0;"></iframe>';}else{mapHtml='<div style="display:flex;align-items:center;justify-content:center;height:100%;color:var(--text-muted);">🗺️ Map unavailable</div>';}var items=[['Native Name',data.country_name_local||'-'],['Capital',data.capital_en+(data.capital_local?' / '+data.capital_local:'')],['Continent',data.continent+(data.subcontinent?', '+data.subcontinent:'')],['Head of State',data.head_of_state_en||'-'],['Anthem',data.national_anthem_en||'-'],['OECD',data.oecd_member==='Yes'?'✓ '+data.oecd_year:'—'],['BRICS',data.brics_member==='Yes'?'✓ '+data.brics_year:'—'],['Population',(!N(data.population)?I18N.formatNumber(data.population):'-')+' (#'+(data.population_rank||'-')+')'],['Area',(data.area?I18N.formatNumber(data.area)+' km²':'-')+' (#'+(data.area_rank||'-')+')'],['GDP',!N(data.gdp)?'$'+I18N.formatNumber(data.gdp/1e6)+'B':'-'],['HDI',!N(data.hdi)?data.hdi.toFixed(3):'-'],['Life Exp.',!N(data.life_expectancy)?data.life_expectancy.toFixed(1)+' yr':'-'],['Happiness',!N(data.happiness)?data.happiness.toFixed(2):'-']];var ih='';for(var i=0;i<items.length;i++)ih+='<div class="detail-item"><span class="detail-label">'+items[i][0]+'</span><span class="detail-value">'+items[i][1]+'</span></div>';document.getElementById('detailMap').innerHTML=mapHtml;document.getElementById('detailBody').innerHTML='<div class="detail-country">'+(I18N.countryName(code)||data.country_name_en)+'</div><div class="detail-native">'+(data.country_name_local||'')+'</div><div class="detail-grid">'+ih+'</div>';document.getElementById('detailPanel').style.display='block';detailOpen=true;}
    function closeDetail(){document.getElementById('detailPanel').style.display='none';detailOpen=false;}
    document.getElementById('detailClose').addEventListener('click',closeDetail);document.getElementById('detailOverlay').addEventListener('click',closeDetail);
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&detailOpen)closeDetail();});
    table.on("cellClick",function(e,cell){var f=cell.getColumn().getField();if(f==='country_code'||f==='country_name_en')openDetail(cell.getRow().getData());});

    // Language
    function buildLangSelectors(){var parts=I18N.buildSelectorHTML().split('|||');document.getElementById('locale1').innerHTML=parts[0];document.getElementById('locale2').innerHTML=parts[1];try{var s=JSON.parse(localStorage.getItem('rankerage_prefs')||'{}');if(s.email)document.getElementById('userEmail').value=s.email;}catch(e){}}
    buildLangSelectors();I18N.applyUI();
    document.getElementById('langBtn').addEventListener('click',function(){document.getElementById('langModal').style.display='flex';});
    document.getElementById('modalClose').addEventListener('click',function(){document.getElementById('langModal').style.display='none';});
    document.getElementById('langModal').addEventListener('click',function(e){if(e.target===this)this.style.display='none';});
    document.getElementById('saveLang').addEventListener('click',function(){I18N.setLocales(document.getElementById('locale1').value,document.getElementById('locale2').value);try{var p=JSON.parse(localStorage.getItem('rankerage_prefs')||'{}');p.email=document.getElementById('userEmail').value.trim();localStorage.setItem('rankerage_prefs',JSON.stringify(p));}catch(e){}I18N.applyUI();table.setColumns(cols);document.getElementById('langModal').style.display='none';});

    // Add tooltips to all data columns
    cols.forEach(function(col) {
      if (col.field === 'country_code' || col.field === 'country_name_en') return;
      var field = col.field;
      var title = col.title;
      col.tooltip = function(e, cell) {
        var d = cell.getRow().getData();
        var rank = d[field + '_rank'];
        var val = d[field];
        if (val === null || val === undefined) return title + ': no data';
        return title + ': ' + (typeof val === 'number' ? val.toLocaleString() : val) + (rank ? ' (Rank #' + rank + ')' : '');
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
    var trendFields = {"gdp":1,"population":1,"life_expectancy":1,"gdp_per_capita":1};
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
      var title = (colLabels[field] || field) + ': ' + name;
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
  });
})();
