// Render Rankerage YouTube Shorts HTML → PNG screenshots
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const VIDEO_DIR = path.join(__dirname, '..', 'videos');
const WIDTH = 1080;
const HEIGHT = 1920;

async function render(htmlFile) {
  const htmlPath = path.join(VIDEO_DIR, htmlFile);
  const pngPath = htmlPath.replace('.html', '.png');
  
  if (!fs.existsSync(htmlPath)) {
    console.log(`  ⚠️ Not found: ${htmlFile}`);
    return;
  }
  
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  await page.setViewport({ width: WIDTH, height: HEIGHT });
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
  await new Promise(r => setTimeout(r, 2000));
  await page.screenshot({ path: pngPath, fullPage: false });
  await browser.close();
  
  console.log(`  ✅ ${pngPath}`);
}

(async () => {
  const files = fs.readdirSync(VIDEO_DIR).filter(f => f.endsWith('.html') && !f.includes('gdp_top10_video'));
  console.log(`Rendering ${files.length} videos...`);
  for (const f of files) {
    await render(f);
  }
  console.log('Done!');
})();
