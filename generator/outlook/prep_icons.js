// Rasterise Lucide line icons (lucide-static) to PNG in the theme colours.
// usage: node prep_icons.js <lucide-static/icons dir> <assets dir>
const { chromium } = require('playwright');
const fs = require('fs');
const ICONS = ['mail', 'mail-open', 'mail-plus', 'mail-check', 'mail-warning', 'mail-search', 'mails', 'inbox', 'send', 'reply', 'reply-all', 'forward',
  'paperclip', 'pen-line', 'signature', 'trash-2', 'archive', 'folder', 'folder-plus', 'folder-open', 'search', 'tag', 'flag', 'filter', 'list-filter',
  'bell', 'bell-ring', 'clock', 'timer', 'calendar', 'calendar-days', 'calendar-plus', 'calendar-check', 'calendar-clock', 'calendar-x', 'calendar-range',
  'users', 'user', 'user-check', 'user-plus', 'user-x', 'repeat', 'map-pin', 'door-open', 'video', 'eye', 'eye-off', 'lock', 'lock-keyhole', 'key-round',
  'shield-check', 'shield-alert', 'triangle-alert', 'octagon-alert', 'circle-alert', 'link', 'fish', 'bug', 'ban', 'siren', 'phone', 'globe',
  'check', 'x', 'circle-check', 'circle-x', 'circle-help', 'info', 'lightbulb', 'sparkles', 'star', 'zap', 'target', 'rocket', 'graduation-cap', 'trophy', 'award',
  'thumbs-up', 'heart', 'keyboard', 'mouse-pointer-click', 'arrow-right', 'arrow-left', 'chevron-right', 'chevron-left', 'at-sign', 'file-text', 'settings',
  'layout-panel-left', 'panel-left', 'panel-top', 'rows-3', 'layout-list', 'list-checks', 'list-ordered', 'message-square-text', 'message-square-reply', 'undo-2', 'copy',
  'book-open', 'share-2', 'plus', 'monitor', 'laptop', 'building-2', 'briefcase', 'handshake', 'pin', 'bookmark', 'upload', 'download', 'grid-2x2', 'plane', 'smile',
  'clipboard-list', 'clipboard-check', 'text', 'type', 'heading', 'align-left', 'hourglass', 'alarm-clock', 'coffee', 'palmtree', 'plane-takeoff', 'log-out', 'home',
  'circle-user', 'contact', 'users-round', 'notebook-pen', 'sticky-note', 'file-check', 'file-warning', 'file-lock', 'file-x', 'route', 'milestone', 'play', 'menu', 'ellipsis'];
const STATUS = ['circle-check', 'circle-x', 'check', 'x', 'triangle-alert', 'thumbs-up', 'ban', 'shield-check', 'shield-alert', 'circle-alert', 'circle-help', 'flag'];
const SCOLORS = { '_ok': '#3DDC84', '_bad': '#FF5C7A', '_warn': '#FFC53D' };
const COLORS = { '': '#FF00DB', '_w': '#FFFFFF', '_g': '#3DEB6C' };
(async () => {
  const [src, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 256, height: 256 }, deviceScaleFactor: 1 });
  let n = 0; const missing = [];
  for (const name of ICONS) {
    const f = `${src}/${name}.svg`;
    if (!fs.existsSync(f)) { missing.push(name); continue; }
    let svg = fs.readFileSync(f, 'utf8').replace(/<!--[\s\S]*?-->/g, '');
    for (const [suf, col] of Object.entries(COLORS)) {
      const s = svg.replace('width="24"', 'width="232"').replace('height="24"', 'height="232"').replace('stroke="currentColor"', `stroke="${col}"`).replace('stroke-width="2"', 'stroke-width="1.6"');
      await page.setContent(`<html><body style="margin:0;background:transparent"><div style="width:256px;height:256px;display:flex;align-items:center;justify-content:center">${s}</div></body></html>`);
      await page.screenshot({ path: `${out}/ic_${name}${suf}.png`, omitBackground: true });
    }
    if (STATUS.includes(name)) for (const [suf, col] of Object.entries(SCOLORS)) {
      const s = svg.replace('width="24"', 'width="232"').replace('height="24"', 'height="232"').replace('stroke="currentColor"', `stroke="${col}"`).replace('stroke-width="2"', 'stroke-width="1.8"');
      await page.setContent(`<html><body style="margin:0;background:transparent"><div style="width:256px;height:256px;display:flex;align-items:center;justify-content:center">${s}</div></body></html>`);
      await page.screenshot({ path: `${out}/ic_${name}${suf}.png`, omitBackground: true });
    }
    n++;
  }
  await browser.close();
  console.log('icons:', n, 'missing:', missing.join(' '));
})();
