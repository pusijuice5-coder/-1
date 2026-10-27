// Renders the generated HTML pages to PNG.
const { chromium } = require('playwright');
const path = require('path');

const dir = __dirname;
const jobs = [
  ['cover1', 1920, 1080], ['cover2', 1920, 1080],
  ['thumb1', 1080, 1080], ['thumb2', 1080, 1080],
];

(async () => {
  const browser = await chromium.launch();
  for (const [name, w, h] of jobs) {
    const page = await browser.newPage({ viewport: { width: w, height: h }, deviceScaleFactor: 1 });
    await page.goto('file://' + path.join(dir, name + '.html'));
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(300);
    await page.screenshot({ path: path.join(dir, 'out', name + '.png'), clip: { x: 0, y: 0, width: w, height: h } });
    await page.close();
  }
  await browser.close();
  console.log('rendered');
})();
