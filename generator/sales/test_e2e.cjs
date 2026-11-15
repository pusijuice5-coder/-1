/* Сквозная проверка курса в заглушке LMS (SCORM 1.2).
   1) cd generator/sales && python3 -m http.server 8766
   2) node test_e2e.cjs [папка_для_скриншотов] */
const { chromium } = require('playwright');
(async () => {
  const shots = process.argv[2];
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1366, height: 768 } });
  const errs = [];
  p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
  p.on('pageerror', e => errs.push('PAGEERR ' + e.message));
  // предзагрузка видео прерывается при перелистывании — это не ошибка
  p.on('requestfailed', r => { if (!/\.mp4$/.test(r.url())) errs.push('REQFAIL ' + r.url()); });
  p.on('response', r => { if (r.status() >= 400) errs.push(r.status() + ' ' + r.url()); });
  await p.goto('http://localhost:8766/test_lms.html');
  const f = p.frames().find(x => x.url().includes('course/index.html'));
  await f.waitForSelector('#next');
  const total = await f.evaluate(() => window.__course.screens.length);
  let gatedChecked = 0;
  for (let i = 0; i < total; i++) {
    const info = await f.evaluate(() => { const c = window.__course; return { i: c.state.i, type: c.screens[c.state.i].type }; });
    if (info.i !== i) throw new Error('ожидался экран ' + i + ', открыт ' + info.i);
    if (/quiz|classify|sort|dialog|exam/.test(info.type)) {
      if (!(await f.evaluate(() => document.querySelector('#next').disabled))) throw new Error('экран ' + i + ' не заблокирован до выполнения');
      gatedChecked++;
    }
    if (shots && [0, 3, 26, 39, 60].includes(i)) await p.screenshot({ path: `${shots}/e2e_${i}.png` });
    if (info.type === 'quiz' || info.type === 'exam') {
      if (info.type === 'exam') await f.click('[data-go]');
      for (;;) {
        const more = await f.evaluate(() => {
          const c = window.__course, s = c.screens[c.state.i], qt = document.querySelector('.qt');
          if (!qt) return false;
          const q = s.questions.find(x => x.q === qt.innerHTML); if (!q) throw new Error('вопрос не найден: ' + qt.textContent);
          const right = [].concat(q.a);
          document.querySelectorAll('.opt').forEach(o => { if (right.includes(+o.dataset.i)) o.click(); });
          const chk = document.querySelector('[data-check]'); chk.click();           // проверить / ответить
          if (s.type === 'quiz' && !chk.disabled) chk.click();                         // следующий вопрос
          return !!document.querySelector('.qt') && c.state.v[c.state.i] < 2;
        });
        if (!more) break;
      }
    } else if (info.type === 'classify') {
      await f.evaluate(() => document.querySelectorAll('.ci').forEach(ci => ci.querySelector('button[data-j="' + ci.dataset.a + '"]').click()));
    } else if (info.type === 'sort') {
      await f.evaluate(() => { const c = window.__course, s = c.screens[c.state.i]; s.items.forEach(t => { [...document.querySelectorAll('.pool button')].find(x => x.innerHTML === t).click(); }); });
    } else if (info.type === 'dialog') {
      await f.evaluate(() => {
        const c = window.__course, s = c.screens[c.state.i];
        s.steps.forEach(sp => { const best = sp.opts.findIndex(o => o.s === 2); document.querySelector('.opt[data-i="' + best + '"]').click(); document.querySelector('[data-n]').click(); });
      });
    } else if (info.type === 'finish') {
      await p.waitForTimeout(300);
      if (shots) await p.screenshot({ path: `${shots}/e2e_finish.png` });
      await f.click('[data-end]');
    }
    if (info.type === 'exam' && shots) { await p.waitForTimeout(400); await p.screenshot({ path: `${shots}/e2e_exam_result.png` }); }
    if (i < total - 1) {
      if (await f.evaluate(() => document.querySelector('#next').disabled)) throw new Error('экран ' + i + ' (' + info.type + ') не разблокировался');
      await f.click('#next');
    }
  }
  const res = await p.evaluate(() => ({ data: window.DATA, log: window.LOG.length, fin: window.LOG.filter(x => x === 'Finish').length, init: window.LOG.filter(x => x === 'Initialize').length }));
  console.log('экранов пройдено:', total, '| заблокированных заданий проверено:', gatedChecked);
  console.log('lesson_status:', res.data['cmi.core.lesson_status'], '| score.raw:', res.data['cmi.core.score.raw'], '| location:', res.data['cmi.core.lesson_location']);
  console.log('suspend_data (' + res.data['cmi.suspend_data'].length + ' симв.):', res.data['cmi.suspend_data']);
  console.log('session_time:', res.data['cmi.core.session_time'], '| Initialize:', res.init, '| Finish:', res.fin);
  // возобновление: перезагрузка фрейма должна вернуть на последний экран
  await p.evaluate(() => { document.getElementById('f').src = 'course/index.html?r=1'; });
  await p.waitForTimeout(1200);
  const f2 = p.frames().find(x => x.url().includes('course/index.html'));
  console.log('после повторного входа открыт экран:', await f2.evaluate(() => window.__course.state.i));
  console.log('ошибки:', errs.length ? '\n' + errs.join('\n') : 'нет');
  await b.close();
  if (res.data['cmi.core.lesson_status'] !== 'passed' || errs.length) process.exit(1);
})().catch(e => { console.error('FAIL', e.message); process.exit(1); });
