#!/usr/bin/env python3
"""
setup_adsense.py — rankerage.com Google AdSense + 타겟팅 광고 세팅

이 스크립트는:
1. index.html의 placeholder AdSense 코드를 실제 코드로 교체
2. 테이블 행 사이에 광고 유닛 삽입 (매 8행마다)
3. 현재 정렬된 컬럼 기반 타겟팅 키워드 자동 설정
"""

import json, re

REPO = "/mnt/c/Users/mathe/Desktop/rankerage"

# ── ⚠️ 여기에 실제 AdSense 퍼블리셔 ID 입력 ──
PUB_ID = "ca-pub-XXXXXXXXXXXXXXXX"  # ← 구글 AdSense에서 받은 ID로 교체

# ── 컬럼별 타겟팅 키워드 ──
TARGET_KEYWORDS = {
    "gdp": "finance investing stocks economy business banking",
    "gdp_per_capita": "wealth income investing luxury",
    "population": "demographics census data analytics",
    "life_expectancy": "healthcare health insurance medical",
    "happiness": "wellness travel lifestyle happiness",
    "tourism": "travel tours flights hotels vacation",
    "edu": "education university online courses learning",
    "internet_pct": "internet broadband technology cloud",
    "coffee": "coffee cafe specialty coffee beans",
    "beer": "beer craft beer brewery alcohol",
    "olympic": "sports olympics fitness training",
    "fifa_ranking": "soccer football sports betting",
    "real_estate": "real estate property housing mortgage",
    "renew": "solar energy renewable green energy",
    "startup_rate": "startups business entrepreneurship venture capital",
    "military_pct": "defense military security aerospace",
    "forest": "environment nature conservation eco tourism",
}
DEFAULT_KEYWORDS = "country comparison rankings data statistics world"

# ── 광고 삽입 JS ──
AD_ROW_JS = """
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
          'data-ad-client="PUB_ID_PLACEHOLDER" ' +
          'data-ad-slot="AD_SLOT_PLACEHOLDER" ' +
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
    table.on("dataSorted", function() {
      setTimeout(insertAdRows, 200);
      updateAdTargeting();
    });
    table.on("dataLoaded", function() {
      setTimeout(insertAdRows, 500);
    });
    setTimeout(insertAdRows, 1000);

    // ── 타겟팅 키워드 업데이트 ──
    var currentMetric = 'POPULATION_PLACEHOLDER';
    var targetKeywords = TARGET_PLACEHOLDER;
    var defaultKeywords = 'DEFAULT_KW_PLACEHOLDER';

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
"""

# ── 적용 ──
def main():
    print("🚀 rankerage.com 광고 세팅")
    print("=" * 50)

    # 1. index.html 업데이트
    with open(f"{REPO}/docs/index.html", "r") as f:
        html = f.read()

    # Sticky footer ad
    if 'sticky-footer-ad' not in html:
        footer_ad = """
    <!-- Sticky Footer Ad -->
    <div id="sticky-footer-ad" style="position:fixed;bottom:0;left:0;right:0;z-index:999;text-align:center;background:rgba(10,14,26,0.95);padding:4px;border-top:1px solid rgba(255,255,255,0.06);">
        <ins class="adsbygoogle" style="display:inline-block;width:728px;height:90px"
             data-ad-client="PUB_ID_PLACEHOLDER"
             data-ad-slot="FOOTER_SLOT_PLACEHOLDER"></ins>
        <span style="position:absolute;top:2px;right:8px;font-size:10px;color:rgba(255,255,255,0.3);cursor:pointer;" onclick="this.parentElement.remove();">✕</span>
    </div>"""
        html = html.replace("</body>", footer_ad + "\n</body>")

    # Replace placeholder with actual pub ID
    html = html.replace("PUB_ID_PLACEHOLDER", PUB_ID)
    html = html.replace("AD_SLOT_PLACEHOLDER", "9876543210")  # 실제 슬롯 ID로 교체 필요
    html = html.replace("FOOTER_SLOT_PLACEHOLDER", "1234567890")

    with open(f"{REPO}/docs/index.html", "w") as f:
        f.write(html)
    print("✅ index.html 광고 코드 업데이트")

    # 2. Ads targeting JS 추가
    ad_js = AD_ROW_JS.replace("PUB_ID_PLACEHOLDER", PUB_ID)
    ad_js = ad_js.replace("AD_SLOT_PLACEHOLDER", "9876543210")
    ad_js = ad_js.replace("POPULATION_PLACEHOLDER", "population")
    ad_js = ad_js.replace("TARGET_PLACEHOLDER", json.dumps(TARGET_KEYWORDS))
    ad_js = ad_js.replace("DEFAULT_KW_PLACEHOLDER", DEFAULT_KEYWORDS)

    # Remove old table.js ad code if any, then append
    with open(f"{REPO}/docs/js/table.js", "r") as f:
        js = f.read()

    js = re.sub(r'// ── 광고[\s\S]*?// ── 타겟팅[\s\S]*?}', '', js)
    js = js.rstrip() + "\n" + ad_js + "\n"

    with open(f"{REPO}/docs/js/table.js", "w") as f:
        f.write(js)
    print("✅ table.js 광고/타겟팅 코드 삽입")

    # 3. Ad CSS
    css_extra = """
/* ── 광고 행 ── */
.tabulator-row.ad-row {
  background: rgba(22,28,46,0.5) !important;
  cursor: default !important;
  min-height: 90px !important;
}
.tabulator-row.ad-row:hover {
  background: rgba(22,28,46,0.7) !important;
  box-shadow: none !important;
}
.tabulator-row.ad-row .tabulator-cell {
  display: none !important;
}

/* ── 광고 로딩 애니메이션 ── */
.ad-placeholder {
  display: flex; align-items: center; justify-content: center;
  height: 80px; color: rgba(255,255,255,0.1); font-size: 11px;
  letter-spacing: 2px;
}
"""
    with open(f"{REPO}/docs/css/style.css", "a") as f:
        f.write(css_extra)
    print("✅ style.css 광고 CSS 추가")

    print(f"\n📋 다음 단계:")
    print(f"   1. {REPO}/scripts/setup_adsense.py 에서 PUB_ID 수정")
    print(f"   2. Google AdSense에서 광고 슬롯 생성 후 AD_SLOT_PLACEHOLDER 교체")
    print(f"   3. git add + commit + push")


if __name__ == "__main__":
    main()
