(function () {
  var TABS = ['overview', 'prep', 'script', 'screen', 'case', 'key', 'debrief'];
  var current = 'overview';
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* хранилище недоступно — страница работает без него */ } }
  };
  function $(s, r) { return (r || document).querySelector(s); }
  function $$(s, r) { return [].slice.call((r || document).querySelectorAll(s)); }

  /* ---------- Вкладки ---------- */
  function show(name, scroll) {
    if (TABS.indexOf(name) < 0) name = 'overview';
    TABS.forEach(function (t) {
      $('#v-' + t).hidden = t !== name;
      var b = $('[data-tab="' + t + '"]');
      b.setAttribute('aria-selected', t === name ? 'true' : 'false');
      b.tabIndex = t === name ? 0 : -1;
    });
    current = name;
    if (scroll) window.scrollTo(0, 0);
    var active = $('[data-tab="' + name + '"]');
    if (active && active.scrollIntoView) active.scrollIntoView({ block: 'nearest', inline: 'nearest' });
  }
  function route() { show((location.hash || '').replace('#', '') || 'overview', false); }
  $$('[data-tab]').forEach(function (b) {
    b.addEventListener('click', function () {
      var name = b.getAttribute('data-tab');
      show(name, true);
      try { if (location.hash !== '#' + name) location.hash = name; } catch (e) { /* без адресной строки тоже работает */ }
    });
  });
  $$('[data-go]').forEach(function (b) {
    b.addEventListener('click', function () { $('[data-tab="' + b.getAttribute('data-go') + '"]').click(); });
  });
  window.addEventListener('hashchange', route);
  route();

  /* ---------- Чек-листы ---------- */
  var ticks = {};
  try { ticks = JSON.parse(store.get('sherlock-checks') || '{}') || {}; } catch (e) { ticks = {}; }
  $$('ul.check').forEach(function (ul) {
    var key = ul.getAttribute('data-key');
    ul.classList.add('live');
    $$('li', ul).forEach(function (li, i) {
      var id = 'ck-' + key + '-' + i;
      var label = document.createElement('label');
      var input = document.createElement('input');
      var span = document.createElement('span');
      input.type = 'checkbox'; input.id = id; input.checked = !!ticks[id];
      span.innerHTML = li.innerHTML;
      label.appendChild(input); label.appendChild(span);
      li.innerHTML = ''; li.appendChild(label);
      input.addEventListener('change', function () {
        if (input.checked) ticks[id] = 1; else delete ticks[id];
        store.set('sherlock-checks', JSON.stringify(ticks));
      });
    });
  });

  /* ---------- Копирование текстов ---------- */
  $$('.copybox').forEach(function (box) {
    var pre = $('pre', box);
    var btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'btn'; btn.textContent = 'Скопировать текст';
    box.appendChild(btn);
    function selectText() {
      var range = document.createRange(); range.selectNodeContents(pre);
      var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
      btn.textContent = 'Текст выделен — скопируйте';
    }
    btn.addEventListener('click', function () {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(pre.textContent).then(function () {
          btn.textContent = 'Скопировано';
          setTimeout(function () { btn.textContent = 'Скопировать текст'; }, 1800);
        }, selectText);
      } else { selectText(); }
    });
  });

  /* ---------- Разгадка под замком ---------- */
  var gate = $('#gate'), keyBody = $('#key-body');
  $('#gate-open').addEventListener('click', function () { gate.hidden = true; keyBody.hidden = false; });

  /* ---------- Фильтр конвертов ---------- */
  var fbtns = $$('[data-env-filter]');
  fbtns.forEach(function (b) {
    b.addEventListener('click', function () {
      var env = b.getAttribute('data-env-filter');
      fbtns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      $$('#docs .sheet').forEach(function (s) { s.hidden = env !== '0' && s.getAttribute('data-env') !== env; });
    });
  });

  /* ---------- Экран: слайды и таймер ---------- */
  var stage = $('#stage');
  var slides = $$('.slide', stage);
  var idx = 0, timers = {}, audio = null;
  var count = $('#s-count'), jump = $('#s-jump'), tctl = $('#t-ctl'), tval = $('#t-val'), go = $('#t-go'), full = $('#s-full');

  function fmt(s) { var m = Math.floor(s / 60), x = s % 60; return (m < 10 ? '0' : '') + m + ':' + (x < 10 ? '0' : '') + x; }
  function tstate(i) {
    if (!timers[i]) { var total = (+slides[i].getAttribute('data-timer') || 0) * 60; timers[i] = { total: total, left: total, end: 0, run: false, beeped: false }; }
    return timers[i];
  }
  function leftOf(t) { return t.run ? Math.max(0, Math.ceil((t.end - Date.now()) / 1000)) : t.left; }
  function beep() {
    if (!audio) return;
    try {
      [0, 0.35, 0.7].forEach(function (d) {
        var o = audio.createOscillator(), g = audio.createGain();
        o.frequency.value = 880; o.connect(g); g.connect(audio.destination);
        g.gain.setValueAtTime(0.0001, audio.currentTime + d);
        g.gain.exponentialRampToValueAtTime(0.3, audio.currentTime + d + 0.02);
        g.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + d + 0.25);
        o.start(audio.currentTime + d); o.stop(audio.currentTime + d + 0.27);
      });
    } catch (e) { /* звук не обязателен */ }
  }
  function settle(t) {
    if (t.run && leftOf(t) === 0) { t.run = false; t.left = 0; if (!t.beeped) { t.beeped = true; beep(); } }
  }
  function paintTimer() {
    var t = tstate(idx); settle(t);
    var l = leftOf(t), el = $('.s-timer', slides[idx]);
    el.textContent = fmt(l); tval.textContent = fmt(l);
    el.classList.toggle('warn', l > 0 && l <= Math.min(300, t.total / 3));
    el.classList.toggle('over', l === 0);
    go.textContent = t.run ? 'Пауза' : 'Старт';
  }
  function paint() {
    slides.forEach(function (s, i) { s.hidden = i !== idx; });
    count.textContent = (idx + 1) + ' / ' + slides.length;
    jump.value = String(idx);
    var has = slides[idx].hasAttribute('data-timer');
    tctl.hidden = !has;
    if (has) paintTimer();
  }
  function move(d) { idx = Math.max(0, Math.min(slides.length - 1, idx + d)); paint(); }
  function toggleTimer() {
    if (!slides[idx].hasAttribute('data-timer')) return;
    var t = tstate(idx);
    if (t.run) { t.left = leftOf(t); t.run = false; }
    else {
      if (t.left === 0) t.left = t.total;
      t.end = Date.now() + t.left * 1000; t.run = true; t.beeped = false;
      try { audio = audio || new (window.AudioContext || window.webkitAudioContext)(); if (audio.state === 'suspended') audio.resume(); } catch (e) { audio = null; }
      try { if (navigator.wakeLock) navigator.wakeLock.request('screen').catch(function () {}); } catch (e) { /* не страшно */ }
    }
    paintTimer();
  }
  $('#s-prev').addEventListener('click', function () { move(-1); });
  $('#s-next').addEventListener('click', function () { move(1); });
  jump.addEventListener('change', function () { idx = +jump.value; paint(); });
  go.addEventListener('click', toggleTimer);
  $('#t-reset').addEventListener('click', function () { var t = tstate(idx); t.run = false; t.left = t.total; t.beeped = false; paintTimer(); });
  $('#t-plus').addEventListener('click', function () { var t = tstate(idx); if (t.run) t.end += 60000; else t.left += 60; paintTimer(); });
  full.addEventListener('click', function () {
    try {
      if (document.fullscreenElement) document.exitFullscreen();
      else if (stage.requestFullscreen) { var p = stage.requestFullscreen(); if (p && p.catch) p.catch(function () {}); }
    } catch (e) { /* полноэкранный режим доступен не везде */ }
  });
  document.addEventListener('fullscreenchange', function () { full.textContent = document.fullscreenElement ? 'Свернуть' : 'На весь экран'; });
  document.addEventListener('keydown', function (e) {
    if (current !== 'screen') return;
    var tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'select' || tag === 'input' || tag === 'textarea') return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown') { move(1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft' || e.key === 'PageUp') { move(-1); e.preventDefault(); }
    else if (e.key === ' ' && tag !== 'button') { toggleTimer(); e.preventDefault(); }
  });
  setInterval(function () {
    Object.keys(timers).forEach(function (i) { settle(timers[i]); });
    if (slides[idx].hasAttribute('data-timer')) paintTimer();
  }, 250);
  paint();
})();
