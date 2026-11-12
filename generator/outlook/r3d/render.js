// node render.js <outdir> <hue> obj1 obj2 ...   (needs a static server on :8765 serving this dir)
const { chromium } = require('playwright');
(async () => {
  const [outdir, hue, ...objs] = process.argv.slice(2);
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1100, height: 1100 }, deviceScaleFactor: 1 });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[error]', e.message));
  for (const o of objs) {
    await page.goto(`http://localhost:8765/render.html?obj=${o}&hue=${hue}`);
    await page.waitForFunction('window.__done === true', null, { timeout: 120000 });
    const data = await page.evaluate(() => document.querySelector('canvas').toDataURL('image/png'));
    require('fs').writeFileSync(`${outdir}/${o}_${hue}.png`, Buffer.from(data.split(',')[1], 'base64'));
    console.log('ok', o);
  }
  await browser.close();
})();
