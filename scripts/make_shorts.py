#!/usr/bin/env python3
"""Generate YouTube Shorts from Rankerage data — Top 10 rankings with animated bar chart"""
import json, os, sys, subprocess, tempfile, textwrap

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'docs', 'data', 'countries.json')

# Config
WIDTH, HEIGHT = 1080, 1920  # Vertical 9:16 for Shorts
DURATION = 15  # seconds
FPS = 30
FONT = "Arial"

# Ranking templates: (field, title_kr, title_en, unit, ascending?)
RANKINGS = [
    ("population", "세계 인구 TOP 10", "World Population TOP 10", "명", False),
    ("gdp", "세계 GDP TOP 10", "World GDP TOP 10", "$", False),
    ("gdp_per_capita", "1인당 GDP TOP 10", "GDP per Capita TOP 10", "$", False),
    ("hdi", "인간개발지수 TOP 10", "HDI TOP 10", "", False),
    ("life_expectancy", "기대수명 TOP 10", "Life Expectancy TOP 10", "세", False),
    ("happiness", "행복지수 TOP 10", "Happiness TOP 10", "점", False),
    ("democracy", "민주주의 TOP 10", "Democracy TOP 10", "점", False),
    ("fifa_ranking", "FIFA 랭킹 TOP 10", "FIFA Ranking TOP 10", "위", True),
    ("nobel", "노벨상 TOP 10", "Nobel Prizes TOP 10", "개", False),
    ("coffee", "커피소비 TOP 10", "Coffee Consumption TOP 10", "kg", False),
]

def generate_html(field, title, top10):
    """Generate an HTML page with animated bar chart"""
    labels = [c['name'] for c in reversed(top10)]
    values = [c['value'] for c in reversed(top10)]
    
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0a0e1a;width:{WIDTH}px;height:{HEIGHT}px;overflow:hidden;font-family:Arial,sans-serif;display:flex;flex-direction:column;align-items:center;justify-content:center}}
h1{{color:#e0c87c;font-size:48px;text-align:center;padding:20px;animation:fadeIn 0.5s}}
h2{{color:#8892b0;font-size:24px;text-align:center;animation:fadeIn 0.8s}}
.chart{{width:900px;margin-top:40px}}
.bar-row{{display:flex;align-items:center;margin:12px 0;animation:slideIn 0.5s ease-out backwards}}
.bar-row:nth-child(1){{animation-delay:0.2s}}
.bar-row:nth-child(2){{animation-delay:0.4s}}
.bar-row:nth-child(3){{animation-delay:0.6s}}
.bar-row:nth-child(4){{animation-delay:0.8s}}
.bar-row:nth-child(5){{animation-delay:1.0s}}
.bar-row:nth-child(6){{animation-delay:1.2s}}
.bar-row:nth-child(7){{animation-delay:1.4s}}
.bar-row:nth-child(8){{animation-delay:1.6s}}
.bar-row:nth-child(9){{animation-delay:1.8s}}
.bar-row:nth-child(10){{animation-delay:2.0s}}
.rank{{width:50px;text-align:center;font-size:28px;font-weight:700}}
.rank.r1{{color:#f0a04b}} .rank.r2{{color:#a0b8d8}} .rank.r3{{color:#cd7f32}} .rank.rest{{color:#8892b0}}
.name{{width:250px;font-size:22px;color:#e0e8f0;text-align:right;padding-right:12px;overflow:hidden;white-space:nowrap}}
.bar-wrap{{flex:1;height:36px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;position:relative}}
.bar{{height:100%;background:linear-gradient(90deg,#e0c87c,#5b8def);border-radius:4px;animation:grow 1.5s ease-out backwards}}
.bar-label{{position:absolute;right:8px;top:50%;transform:translateY(-50%);font-size:18px;color:#fff;font-weight:700}}
@keyframes slideIn{{from{{opacity:0;transform:translateX(-30px)}}to{{opacity:1;transform:translateX(0)}}}}
@keyframes fadeIn{{from{{opacity:0}}to{{opacity:1}}}}
@keyframes grow{{from{{width:0}}}}
footer{{color:#545d7a;font-size:16px;margin-top:40px;animation:fadeIn 3s}}
</style></head><body>
<h1>{title}</h1>
<h2>Rankerage.com</h2>
<div class="chart">
'''
    max_val = max(values) or 1
    for i, (name, val) in enumerate(zip(labels, values)):
        rank_class = 'r1' if i < 3 else 'r2' if i < 5 else 'r3' if i < 8 else 'rest'
        pct = (val / max_val * 100)
        html += f'<div class="bar-row"><span class="rank {rank_class}">#{10-i}</span><span class="name">{name[:20]}</span><div class="bar-wrap"><div class="bar" style="animation-delay:{0.5+i*0.2}s;width:{pct}%"><span class="bar-label">{val:,.0f}</span></div></div></div>\n'
    
    html += f'''</div>
<footer>🌍 Rankerage.com — 202 Countries × 100 Rankings</footer>
</body></html>'''
    return html

def render_video(html_path, output_path):
    """Use Playwright or headless Chrome to render HTML to video"""
    # Try Playwright first
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": WIDTH, "height": HEIGHT})
            page.goto(f"file://{html_path}")
            page.wait_for_timeout(5000)  # Let animations play
            page.screenshot(path=output_path.replace('.mp4', '.png'), full_page=False)
            browser.close()
        print(f"  Screenshot saved: {output_path.replace('.mp4', '.png')}")
        return True
    except ImportError:
        pass
    
    # Fallback: just save HTML, user can screen record
    print(f"  HTML saved (no renderer available): {html_path}")
    print(f"  Install playwright: pip install playwright && playwright install chromium")
    return False

def main():
    with open(DATA, encoding='utf-8') as f:
        countries = json.load(f)
    
    video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'videos')
    os.makedirs(video_dir, exist_ok=True)
    
    for field, title_kr, title_en, unit, ascending in RANKINGS:
        # Get top 10
        ranked = [(c['country_name_en'], c.get(field)) for c in countries if c.get(field) is not None]
        ranked.sort(key=lambda x: x[1], reverse=not ascending)
        top10 = [{'name': n, 'value': v} for n, v in ranked[:10]]
        
        if not top10:
            continue
        
        print(f"Generating: {title_kr}")
        html = generate_html(field, title_kr, top10)
        
        html_path = os.path.join(video_dir, f'{field}_top10.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        output = os.path.join(video_dir, f'{field}_top10.mp4')
        render_video(html_path, output)
    
    print(f"\nDone! {len(RANKINGS)} videos generated in {video_dir}")

if __name__ == '__main__':
    main()
