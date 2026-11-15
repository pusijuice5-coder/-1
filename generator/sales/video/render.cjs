/* Покадровый рендер ролика: node render.cjs v1 out.mp4 audio.mp3 [fps]
   Режим проверки: node render.cjs v1 --shots dir t1,t2,... */
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
(async () => {
  const id = process.argv[2];
  const url = 'file://' + path.join(__dirname, 'player.html') + '?v=' + id;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.error('PAGEERR', e.message));
  await p.goto(url);
  await p.waitForFunction('window.READY === true');
  const total = await p.evaluate('window.TOTAL');
  if (process.argv[3] === '--shots') {
    for (const t of process.argv[5].split(',').map(Number)) {
      await p.evaluate(t => window.seek(t), t);
      await p.screenshot({ path: path.join(process.argv[4], `${id}_${String(t).replace('.', '_')}.jpg`), type: 'jpeg', quality: 88 });
    }
    await b.close(); return;
  }
  const out = process.argv[3], audio = process.argv[4], fps = +(process.argv[5] || 25);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-', '-i', audio,
    '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-ac', '2', '-af', 'apad',
    '-t', total.toFixed(2), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.ceil(total * fps);
  for (let i = 0; i < n; i++) {
    await p.evaluate(t => window.seek(t), i / fps);
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await b.close();
  console.log(id, 'frames', n, 'seconds', total.toFixed(1));
})();
