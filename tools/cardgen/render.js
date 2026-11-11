// Renders every warning card in cards.json to square (1080x1080) and story (1080x1920) JPEGs.
// Usage: node render.js <outDir> [key]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const out = process.argv[2], only = process.argv[3];
  fs.mkdirSync(out, { recursive: true });
  const cards = JSON.parse(fs.readFileSync(path.join(__dirname, 'cards.json'), 'utf8')).filter(c => !only || c.key === only);
  const b = await chromium.launch();
  for (const c of cards) for (const story of [false, true]) {
    const p = await b.newPage({ viewport: { width: 1080, height: story ? 1920 : 1080 } });
    await p.goto('file://' + path.join(__dirname, 'template.html') + '?s=' + (story ? 1 : 0) + '&c=' + encodeURIComponent(JSON.stringify(c)));
    await p.waitForSelector('body[data-ready="1"]');
    const over = await p.evaluate(() => document.querySelector('.card').scrollHeight > document.querySelector('.card').clientHeight + 1);
    if (over) console.log('OVERFLOW', c.key, story ? 'story' : 'square');
    await p.screenshot({ path: path.join(out, `${c.key}-${story ? 'story' : 'square'}.jpg`), type: 'jpeg', quality: 88 });
    await p.close();
  }
  await b.close();
  console.log('rendered', cards.length * 2);
})();
