/* Плеер курса: навигация, интерактивы, тесты, сохранение прогресса через SCORM */
(function () {
  'use strict';
  var C = window.COURSE, CFG = window.COURSE_CONFIG || {};
  var PASS = CFG.PASS_SCORE || 80;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ---------- данные ---------- */
  var screens = [];
  C.modules.forEach(function (m, mi) {
    m.screens.forEach(function (s, si) { s.mod = m; s.mi = mi; s.si = si; s.idx = screens.length; screens.push(s); });
  });
  var GATED = { quiz: 1, classify: 1, sort: 1, dialog: 1, exam: 1 };
  var st = { i: 0, v: [], e: -1, p: 0 };
  screens.forEach(function () { st.v.push(0); });

  function load() {
    var s = SCORM.load();
    if (s && s.data) {
      try {
        var d = JSON.parse(s.data);
        if (d.v && d.v.length === screens.length) st.v = d.v.split('').map(Number);
        if (typeof d.e === 'number') st.e = d.e;
        st.p = d.p ? 1 : 0;
      } catch (e) {}
    }
    var loc = parseInt(s && s.loc, 10);
    if (!isNaN(loc) && loc >= 0 && loc < screens.length) st.i = Math.min(loc, reach());
  }
  function save() { SCORM.save(String(st.i), JSON.stringify({ v: st.v.join(''), e: st.e, p: st.p })); }
  function locked(i) { return GATED[screens[i].type] && st.v[i] < 2; }
  /* самый дальний экран, на который можно перейти */
  function reach() {
    for (var i = 0; i < screens.length; i++) { if (st.v[i] === 0 || locked(i)) return i; }
    return screens.length - 1;
  }
  function done(i) { if (st.v[i] < 2) { st.v[i] = 2; save(); } nav(); }

  /* ---------- утилиты ---------- */
  function hl(t) { return String(t || '').replace(/\*([^*]+)\*/g, '<span class="hl">$1</span>'); }
  function shuffle(a) { a = a.slice(); for (var i = a.length - 1; i > 0; i--) { var j = Math.floor(Math.random() * (i + 1)); var t = a[i]; a[i] = a[j]; a[j] = t; } return a; }
  function eqSet(a, b) { if (a.length !== b.length) return false; a = a.slice().sort(); b = b.slice().sort(); for (var i = 0; i < a.length; i++) if (a[i] !== b[i]) return false; return true; }
  function plural(n, a, b, c) { var m = n % 100, k = n % 10; return (m > 10 && m < 20) ? c : k === 1 ? a : (k > 1 && k < 5) ? b : c; }

  var IC = {
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    users: '<circle cx="9" cy="8" r="3.5"/><path d="M2 20c0-3.5 3.5-5 7-5s7 1.5 7 5"/><path d="M16 4.5a3.5 3.5 0 0 1 0 7M18 15c2.5.5 4 2 4 5"/>',
    chart: '<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-7"/>',
    shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    chat: '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9h8M8 12h5"/>',
    target: '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1"/>',
    bulb: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.8.8 1 1.5 1 2.5h6c0-1 .2-1.7 1-2.5A6 6 0 0 0 12 3z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    layers: '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12l9 5 9-5M3 16l9 5 9-5"/>',
    phone: '<rect x="7" y="2" width="10" height="20" rx="2.5"/><path d="M11 18h2"/>',
    heart: '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>',
    check: '<circle cx="12" cy="12" r="9"/><path d="M8 12l3 3 5-6"/>',
    link: '<path d="M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1"/><path d="M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1"/>',
    cog: '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
    star: '<path d="M12 3l2.7 5.6 6.3.900-4.5 4.4 1 6.1-5.5-2.9-5.5 2.9 1-6.1L3 9.5l6.3-.900z"/>',
    doc: '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    building: '<path d="M4 21V5l8-2v18M12 9l8 2v10M2 21h20"/><path d="M7 9h2M7 13h2M7 17h2M15 14h2M15 18h2"/>',
    coins: '<ellipse cx="9" cy="7" rx="6" ry="3"/><path d="M3 7v5c0 1.7 2.7 3 6 3s6-1.3 6-3V7"/><path d="M15 11c3 .2 6 1.4 6 3v3c0 1.7-2.7 3-6 3s-6-1.3-6-3v-2"/>',
    route: '<circle cx="6" cy="18" r="2.5"/><circle cx="18" cy="6" r="2.5"/><path d="M8.5 18H15a3.5 3.5 0 0 0 0-7H9a3.5 3.5 0 0 1 0-7h6.5"/>',
    ear: '<path d="M7 9a5 5 0 0 1 10 0c0 3-3 4-3 7a3 3 0 0 1-6 0"/><path d="M10 9a2 2 0 0 1 4 0c0 1.5-1.5 2-2 3"/>',
    question: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 .9-1 1.7M12 17h.01"/>',
    flag: '<path d="M5 21V4M5 4h12l-2 4 2 4H5"/>',
    lock: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    spark: '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"/>',
    hand: '<path d="M3 12l4-4 4 3 3-3 7 6-4 4-3-2-3 3-3-2-2 1z"/>',
    eye: '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    repeat: '<path d="M4 9a8 8 0 0 1 14-3l2 2M20 15a8 8 0 0 1-14 3l-2-2"/><path d="M20 4v4h-4M4 20v-4h4"/>',
    scale: '<path d="M12 3v18M6 21h12M5 7h14"/><path d="M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
    bolt: '<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>'
  };
  function ico(n) { return '<svg viewBox="0 0 24 24" aria-hidden="true">' + (IC[n] || IC.spark) + '</svg>'; }
  var ARROW_R = '<svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>';
  var ARROW_L = '<svg viewBox="0 0 24 24"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>';

  function head(s, big) {
    var m = s.mod, k = '';
    if (s.kicker !== false) {
      k = '<div class="kicker rv">' + (s.kicker || ((m.num ? 'Модуль ' + m.num + ' · ' : '') + m.title)) +
        (m.track ? ' <span class="tag">' + m.track + '</span>' : '') + '</div>';
    }
    return k + (s.title ? '<' + (big ? 'h1' : 'h2') + ' class="t rv" style="--i:1">' + hl(s.title) + '</' + (big ? 'h1' : 'h2') + '>' : '') +
      (s.lead ? '<p class="lead rv" style="--i:2">' + s.lead + '</p>' : '');
  }
  function say(s) {
    if (!s.say) return '';
    return '<div class="say rv" style="--i:9">' + Character.html(s.say.pose || 'explain', s.say.flip) +
      '<div class="bubble"><span class="who">' + (CFG.MENTOR_NAME || 'Наставник') + '</span>' + s.say.text + '</div></div>';
  }
  function list(items, cls) { return '<ul class="' + (cls || 'plus') + '">' + items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul>'; }

  /* ---------- рендеры экранов ---------- */
  var R = {};

  R.hero = function (s) {
    return {
      html: '<div class="hero"><div style="display:grid;gap:22px">' +
        '<div class="kicker rv">' + s.kicker + '</div>' +
        '<h1 class="t rv" style="--i:1">' + hl(s.title) + '</h1>' +
        '<p class="lead rv" style="--i:2">' + s.lead + '</p>' +
        '<div class="chips rv" style="--i:3">' + s.chips.map(function (c) { return '<span class="chip">' + c + '</span>'; }).join('') + '</div>' +
        '<div class="hero-cta rv" style="--i:4"><button class="btn primary" data-next>' + (st.v[1] ? 'Продолжить' : 'Начать курс') + ARROW_R + '</button>' +
        '<span class="src">Листайте кнопками внизу или стрелками ← → на клавиатуре</span></div></div>' +
        '<div class="rv" style="--i:3">' + Character.html(s.pose || 'explain') + '</div></div>',
      mount: function (el) { $('[data-next]', el).onclick = function () { go(st.i + 1); }; }
    };
  };

  R.module = function (s) {
    var m = s.mod;
    return {
      html: '<div class="mod"><div class="n rv">' + m.num + '</div><div style="display:grid;gap:18px">' +
        '<div class="modtop rv" style="--i:1"><div class="kicker">Модуль ' + m.num + (m.track ? ' <span class="tag">' + m.track + '</span>' : '') + '</div>' +
        '<div class="chips">' + (s.meta || []).map(function (c) { return '<span class="chip">' + c + '</span>'; }).join('') + '</div></div>' +
        '<h1 class="t rv" style="--i:2;font-size:clamp(26px,3.8vw,50px)">' + hl(s.title || m.title) + '</h1>' +
        (s.lead ? '<p class="lead rv" style="--i:3">' + s.lead + '</p>' : '') +
        '<div class="card rv" style="--i:4"><h3>После модуля вы сможете</h3>' + list(s.goals) + '</div>' +
        '</div></div>' + say(s)
    };
  };

  R.text = function (s) {
    var main = (s.blocks || []).map(function (b, i) { return '<p class="p rv" style="--i:' + (3 + i) + '">' + b + '</p>'; }).join('') +
      (s.list ? '<div class="rv" style="--i:5">' + list(s.list) + '</div>' : '');
    var aside = '';
    if (s.aside) {
      aside = '<div class="card ' + (s.aside.cls || 'glow brk') + ' rv" style="--i:6">' + (s.aside.big ? '<div class="bignum">' + s.aside.big + '</div>' : '') +
        (s.aside.h ? '<h3>' + s.aside.h + '</h3>' : '') + (s.aside.t ? '<p>' + s.aside.t + '</p>' : '') + (s.aside.list ? list(s.aside.list, 'dot') : '') +
        (s.aside.src ? '<p class="src" style="margin-top:10px">' + s.aside.src + '</p>' : '') + '</div>';
    }
    return {
      html: head(s) + (aside ? '<div class="grid" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);align-items:start">' +
        '<div style="display:grid;gap:12px">' + main + '</div>' + aside + '</div>' : main) + say(s)
    };
  };

  R.cards = function (s) {
    var cols = s.cols || Math.min(s.items.length, 3);
    return {
      html: head(s) + '<div class="grid g' + cols + '">' + s.items.map(function (c, i) {
        return '<div class="card ' + (c.cls || s.variant || '') + ' rv" style="--i:' + (3 + i) + '">' +
          (c.ico ? '<div class="ico">' + ico(c.ico) + '</div>' : '') + (c.num ? '<span class="num">' + c.num + '</span>' : '') +
          (c.big ? '<div class="bignum">' + c.big + '</div>' : '') +
          '<h3>' + c.h + '</h3>' + (c.t ? '<p>' + c.t + '</p>' : '') + (c.list ? list(c.list, 'dot') : '') +
          (c.ex ? '<span class="ex">' + c.ex + '</span>' : '') + '</div>';
      }).join('') + '</div>' + (s.src ? '<p class="src rv" style="--i:9">' + s.src + '</p>' : '') + say(s)
    };
  };

  R.flip = function (s) {
    var cols = s.cols || Math.min(s.items.length, 4);
    return {
      html: head(s) + '<div class="grid g' + cols + '">' + s.items.map(function (c, i) {
        return '<button class="flip rv" style="--i:' + (3 + i) + ';min-height:' + (s.h || 220) + 'px" aria-label="' + c.h.replace(/<[^>]+>/g, '') + '"><span class="in">' +
          '<span class="f"><small>' + (c.sub || '') + '</small><h3>' + c.h + '</h3><span class="pl">+</span></span>' +
          '<span class="b">' + c.back + '</span></span></button>';
      }).join('') + '</div><p class="src rv" style="--i:9">Нажмите на карточку, чтобы перевернуть её</p>' + say(s),
      mount: function (el) { $$('.flip', el).forEach(function (b) { b.onclick = function () { b.classList.toggle('on'); b.classList.add('seen'); }; }); }
    };
  };

  R.accordion = function (s) {
    return {
      html: head(s) + '<div class="acc">' + s.items.map(function (c, i) {
        return '<div class="it rv' + (i === 0 && s.open !== false ? ' open' : '') + '" style="--i:' + (3 + i) + '"><button class="hd" aria-expanded="' + (i === 0) + '">' +
          '<span class="k">' + (c.k || (i + 1)) + '</span><span>' + c.h + '</span><span class="x">+</span></button>' +
          '<div class="bd"><div><div class="c">' + c.body + '</div></div></div></div>';
      }).join('') + '</div>' + say(s),
      mount: function (el) {
        $$('.it', el).forEach(function (it) {
          $('.hd', it).onclick = function () {
            var was = it.classList.contains('open');
            $$('.it', el).forEach(function (o) { o.classList.remove('open'); $('.hd', o).setAttribute('aria-expanded', 'false'); });
            if (!was) { it.classList.add('open'); $('.hd', it).setAttribute('aria-expanded', 'true'); }
          };
        });
      }
    };
  };

  R.tabs = function (s) {
    return {
      html: head(s) + '<div class="tabs rv" style="--i:3" role="tablist">' + s.tabs.map(function (t, i) {
        return '<button class="tab' + (i ? '' : ' on') + '" role="tab">' + t.label + '</button>';
      }).join('') + '</div>' + s.tabs.map(function (t, i) {
        var inner = t.html || '';
        if (t.rows) inner = '<div class="tblwrap"><table class="tbl"><tr>' + t.head.map(function (h) { return '<th>' + h + '</th>'; }).join('') + '</tr>' +
          t.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></div>';
        if (t.acc) inner = '<div class="acc">' + t.acc.map(function (c, j) {
          return '<div class="it"><button class="hd"><span class="k">' + (j + 1) + '</span><span>' + c.h + '</span><span class="x">+</span></button>' +
            '<div class="bd"><div><div class="c">' + c.body + '</div></div></div></div>';
        }).join('') + '</div>';
        return '<div class="tabpane' + (i ? '' : ' on') + '">' + inner + '</div>';
      }).join('') + say(s),
      mount: function (el) {
        var tabs = $$('.tab', el), panes = $$('.tabpane', el);
        tabs.forEach(function (t, i) { t.onclick = function () { tabs.forEach(function (x, j) { x.classList.toggle('on', i === j); panes[j].classList.toggle('on', i === j); }); }; });
        $$('.acc .it', el).forEach(function (it) { $('.hd', it).onclick = function () { it.classList.toggle('open'); }; });
      }
    };
  };

  R.steps = function (s) {
    return {
      html: head(s) + '<div class="steps rv" style="--i:3">' + s.items.map(function (c, i) {
        return '<button class="step' + (i ? '' : ' on seen') + '"><span class="sn">' + (c.n || ('0' + (i + 1)).slice(-2)) + '</span><span class="st">' + c.h + '</span></button>';
      }).join('') + '</div><div class="stephost rv" style="--i:4"></div>' + say(s),
      mount: function (el) {
        var host = $('.stephost', el), btns = $$('.step', el);
        function show(i) {
          var c = s.items[i];
          btns.forEach(function (b, j) { b.classList.toggle('on', i === j); });
          btns[i].classList.add('seen');
          host.innerHTML = '<div class="stepbody"><div class="card"><h3>' + (c.full || c.h) + '</h3>' + c.body + '</div>' +
            '<div class="card glow brk">' + c.side + '</div></div>';
        }
        btns.forEach(function (b, i) { b.onclick = function () { show(i); }; });
        show(0);
      }
    };
  };

  R.compare = function (s) {
    function col(c, cls) { return '<div class="card col ' + cls + ' rv" style="--i:' + (cls === 'old' ? 3 : 4) + '"><h3>' + c.h + '</h3><ul>' + c.items.map(function (x) { return '<li>' + x + '</li>'; }).join('') + '</ul></div>'; }
    return { html: head(s) + '<div class="cmp' + (s.bad ? ' bad' : '') + '">' + col(s.left, 'old') + col(s.right, 'new') + '</div>' + say(s) };
  };

  R.table = function (s) {
    return {
      html: head(s) + '<div class="tblwrap rv" style="--i:3"><table class="tbl"><tr>' + s.head.map(function (h) { return '<th>' + h + '</th>'; }).join('') + '</tr>' +
        s.rows.map(function (r) { return '<tr>' + r.map(function (c) { return '<td>' + c + '</td>'; }).join('') + '</tr>'; }).join('') + '</table></div>' + say(s)
    };
  };

  R.video = function (s) {
    return {
      html: head(s) + '<div class="vid"><div class="vbox rv" style="--i:3"><video controls playsinline preload="metadata" poster="' + s.poster + '">' +
        '<source src="' + s.src + '" type="video/mp4">Ваш браузер не поддерживает видео.</video></div>' +
        '<div class="vside rv" style="--i:4"><h3>Текст ролика</h3><div class="tr">' + s.transcript.map(function (p) { return '<p>' + p + '</p>'; }).join('') + '</div></div></div>' + say(s)
    };
  };

  /* вопрос(ы) с проверкой: используется и в quiz, и в exam */
  function askOne(host, q, opt) {
    var multi = Array.isArray(q.a), right = multi ? q.a : [q.a];
    var order = shuffle(q.opts.map(function (_, i) { return i; }));
    host.innerHTML = '<div class="q"><div class="qn">' + opt.label + (multi ? ' · выберите все верные варианты' : '') + '</div>' +
      '<div class="qt">' + q.q + '</div><div class="opts">' + order.map(function (oi) {
        return '<button class="opt' + (multi ? ' multi' : '') + '" data-i="' + oi + '"><span class="mk">✓</span><span>' + q.opts[oi] + '</span></button>';
      }).join('') + '</div><div class="fbhost"></div><div class="row"><button class="btn primary" data-check disabled>' + (opt.exam ? 'Ответить' : 'Проверить') + '</button>' +
      '<div class="dots">' + opt.dots + '</div></div></div>';
    var btns = $$('.opt', host), chk = $('[data-check]', host), answered = false;
    btns.forEach(function (b) {
      b.onclick = function () {
        if (answered) return;
        if (!multi) btns.forEach(function (x) { x.classList.remove('sel'); });
        b.classList.toggle('sel', multi ? !b.classList.contains('sel') : true);
        chk.disabled = !$$('.opt.sel', host).length;
      };
    });
    chk.onclick = function () {
      if (answered) { opt.next(); return; }
      var sel = $$('.opt.sel', host).map(function (b) { return +b.dataset.i; });
      var ok = eqSet(sel, right);
      answered = true;
      if (opt.exam) { opt.result(ok); opt.next(); return; }
      btns.forEach(function (b) {
        var i = +b.dataset.i; b.disabled = true; b.classList.remove('sel');
        if (right.indexOf(i) >= 0) b.classList.add('ok'); else if (sel.indexOf(i) >= 0) { b.classList.add('no'); $('.mk', b).textContent = '✕'; }
      });
      $('.fbhost', host).innerHTML = '<div class="fb ' + (ok ? 'ok' : 'no') + '"><b>' + (ok ? 'Верно. ' : 'Не совсем. ') + '</b>' + q.why + '</div>';
      opt.result(ok);
      chk.innerHTML = opt.last ? 'Готово' : 'Следующий вопрос ' + ARROW_R;
      if (opt.last) { chk.disabled = true; opt.next(); }
    };
  }

  R.quiz = function (s) {
    return {
      html: head(s) + '<div class="qhost rv" style="--i:3"></div>' + say(s),
      mount: function (el) {
        var host = $('.qhost', el), res = [], n = s.questions.length;
        function run(k) {
          if (k >= n) { done(s.idx); return; }
          var dots = s.questions.map(function (_, j) { return '<i class="' + (j < k ? (res[j] ? 'ok' : 'no') : j === k ? 'cur' : '') + '"></i>'; }).join('');
          askOne(host, s.questions[k], {
            label: 'Вопрос ' + (k + 1) + ' из ' + n, dots: dots, last: k === n - 1,
            result: function (ok) { res[k] = ok; }, next: function () { run(k + 1); }
          });
        }
        run(0);
      }
    };
  };

  R.classify = function (s) {
    return {
      html: head(s) + '<div class="cls">' + s.items.map(function (it, i) {
        return '<div class="ci rv" style="--i:' + (3 + i) + '" data-a="' + it.a + '"><p>' + it.t + '</p><div class="cb">' +
          s.cats.map(function (c, j) { return '<button data-j="' + j + '">' + c + '</button>'; }).join('') + '</div><div class="why">' + (it.why || '') + '</div></div>';
      }).join('') + '</div>' + say(s),
      mount: function (el) {
        var left = s.items.length;
        $$('.ci', el).forEach(function (ci) {
          $$('button', ci).forEach(function (b) {
            b.onclick = function () {
              if (ci.classList.contains('done')) return;
              if (b.dataset.j === ci.dataset.a) {
                b.classList.add('ok'); ci.classList.add('done'); $$('button', ci).forEach(function (x) { x.disabled = true; });
                if (--left === 0) done(s.idx);
              } else { b.classList.remove('no'); void b.offsetWidth; b.classList.add('no'); }
            };
          });
        });
      }
    };
  };

  R.sort = function (s) {
    return {
      html: head(s) + '<div class="sort rv" style="--i:3"><div><h3>Варианты</h3><div class="pool"></div></div><div><h3>Правильный порядок</h3><div class="line"></div></div></div>' + say(s),
      mount: function (el) {
        var pool = $('.pool', el), line = $('.line', el), k = 0, n = s.items.length;
        var ord = shuffle(s.items.map(function (_, i) { return i; }));
        function ph() { var p = $('.ph', line); if (p) p.remove(); if (k < n) { line.insertAdjacentHTML('beforeend', '<div class="ph">Шаг ' + (k + 1) + ' — выберите слева</div>'); } }
        ord.forEach(function (i) {
          var b = document.createElement('button'); b.innerHTML = s.items[i]; pool.appendChild(b);
          b.onclick = function () {
            if (i === k) {
              var p = $('.ph', line); if (p) p.remove();
              line.insertAdjacentHTML('beforeend', '<div><b>' + (k + 1) + '</b><span>' + s.items[i] + '</span></div>');
              b.remove(); k++; ph(); if (k === n) done(s.idx);
            } else { b.classList.remove('no'); void b.offsetWidth; b.classList.add('no'); }
          };
        });
        ph();
      }
    };
  };

  R.dialog = function (s) {
    var c = s.client;
    return {
      html: head(s) + '<div class="dlg"><div class="card client rv" style="--i:3"><div class="ava">' + c.ini + '</div><h3>' + c.name + '</h3><div class="role">' + c.role + '</div>' +
        '<p class="ctx">' + c.ctx + '</p><div class="meter"></div><p class="src" style="margin-top:8px">Шкала показывает качество ваших ответов</p></div>' +
        '<div class="talk rv" style="--i:4"></div></div>',
      mount: function (el) {
        var talk = $('.talk', el), meter = $('.meter', el), score = [], n = s.steps.length;
        function drawMeter() { meter.innerHTML = s.steps.map(function (_, i) { return '<i class="' + (score[i] === 2 ? 'g' : score[i] === 1 ? 'm' : score[i] === 0 ? 'b' : '') + '"></i>'; }).join(''); }
        function step(k) {
          drawMeter();
          if (k >= n) { finish(); return; }
          var sp = s.steps[k];
          talk.innerHTML = '<div class="msg c"><small>' + c.name + '</small>' + sp.c + '</div><div class="q"><div class="qn">Шаг ' + (k + 1) + ' из ' + n + ' · выберите ваш ответ</div><div class="opts">' +
            shuffle(sp.opts.map(function (_, i) { return i; })).map(function (i) { return '<button class="opt" data-i="' + i + '"><span class="mk">✓</span><span>' + sp.opts[i].t + '</span></button>'; }).join('') + '</div></div>';
          $$('.opt', talk).forEach(function (b) {
            b.onclick = function () {
              var o = sp.opts[+b.dataset.i]; score[k] = o.s; drawMeter();
              var cls = o.s === 2 ? 'g' : o.s === 1 ? 'm' : 'b';
              talk.innerHTML = '<div class="msg c"><small>' + c.name + '</small>' + sp.c + '</div><div class="msg me"><small>Вы</small>' + o.t + '</div>' +
                '<div class="msg note ' + cls + '"><b>' + (o.s === 2 ? 'Отличный ход. ' : o.s === 1 ? 'Можно лучше. ' : 'Неудачно. ') + '</b>' + o.fb + '</div>' +
                '<div class="row"><button class="btn primary" data-n>' + (k === n - 1 ? 'Итог диалога' : 'Дальше') + ARROW_R + '</button></div>';
              $('[data-n]', talk).onclick = function () { step(k + 1); };
              talk.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            };
          });
        }
        function finish() {
          var sum = score.reduce(function (a, b) { return a + b; }, 0), pct = Math.round(sum / (2 * n) * 100);
          var e = pct >= 80 ? s.end.good : pct >= 50 ? s.end.mid : s.end.bad;
          talk.innerHTML = '<div class="card glow brk"><div class="bignum">' + pct + '%</div><h3>' + e.h + '</h3><p>' + e.t + '</p></div>' +
            '<div class="row"><button class="btn" data-again>Пройти диалог ещё раз</button></div>';
          $('[data-again]', talk).onclick = function () { score = []; step(0); };
          done(s.idx);
        }
        step(0);
      }
    };
  };

  R.exam = function (s) {
    return {
      html: head(s) + '<div class="qhost rv" style="--i:3"></div>',
      mount: function (el) {
        var host = $('.qhost', el), qs, res, n = s.questions.length;
        function intro() {
          var prev = st.e >= 0 ? '<p class="p">Ваш лучший результат: <b>' + st.e + '%</b>' + (st.p ? ' — тест сдан.' : '') + '</p>' : '';
          host.innerHTML = '<div class="grid g3">' +
            '<div class="card"><div class="bignum">' + n + '</div><h3>вопросов</h3><p>По всем модулям курса: общая часть, розница и корпоративный бизнес.</p></div>' +
            '<div class="card"><div class="bignum">' + PASS + '%</div><h3>проходной балл</h3><p>Нужно ответить верно минимум на ' + Math.ceil(n * PASS / 100) + ' ' + plural(Math.ceil(n * PASS / 100), 'вопрос', 'вопроса', 'вопросов') + '.</p></div>' +
            '<div class="card"><div class="bignum">∞</div><h3>попыток</h3><p>Если не получилось — вернитесь к модулям через меню и попробуйте снова.</p></div></div>' + prev +
            '<div class="row" style="margin-top:6px"><button class="btn primary" data-go>' + (st.e >= 0 ? 'Пройти тест заново' : 'Начать тест') + ARROW_R + '</button></div>';
          $('[data-go]', host).onclick = start;
        }
        function start() { qs = shuffle(s.questions); res = []; run(0); }
        function run(k) {
          if (k >= n) { result(); return; }
          var dots = '<span class="src">' + (k + 1) + ' / ' + n + '</span>';
          askOne(host, qs[k], { label: 'Вопрос ' + (k + 1) + ' из ' + n, dots: dots, exam: true, result: function (ok) { res[k] = ok; }, next: function () { run(k + 1); } });
        }
        function result() {
          var right = res.filter(Boolean).length, pct = Math.round(right / n * 100), ok = pct >= PASS;
          if (pct > st.e) st.e = pct;
          if (ok) st.p = 1;
          SCORM.score(st.e, !!st.p);
          var wrong = qs.filter(function (_, i) { return !res[i]; });
          host.innerHTML = '<div class="res"><div class="ring' + (ok ? '' : ' fail') + '" style="--p:' + pct + '"><b>' + pct + '%</b></div><div style="flex:1;min-width:260px;display:grid;gap:10px">' +
            '<h2 class="t" style="font-size:clamp(22px,2.6vw,34px)">' + (ok ? 'Тест *сдан*' : 'Пока *не сдан*').replace(/\*([^*]+)\*/g, '<span class="hl">$1</span>') + '</h2>' +
            '<p class="p">Верных ответов: <b>' + right + ' из ' + n + '</b>. ' + (ok ? 'Результат передан в систему обучения. Переходите к завершению курса.' : 'Для зачёта нужно ' + PASS + '%. Посмотрите разбор ошибок ниже, повторите нужные модули и попробуйте снова.') + '</p>' +
            '<div class="row">' + (ok ? '<button class="btn primary" data-fin>К завершению' + ARROW_R + '</button>' : '') + '<button class="btn" data-go>Пройти заново</button></div></div></div>' +
            (wrong.length ? '<div class="acc" style="margin-top:8px">' + wrong.map(function (q, j) {
              var a = (Array.isArray(q.a) ? q.a : [q.a]).map(function (i) { return q.opts[i]; }).join('; ');
              return '<div class="it"><button class="hd"><span class="k">!</span><span>' + q.q + '</span><span class="x">+</span></button><div class="bd"><div><div class="c"><p><b>Верный ответ:</b> ' + a + '</p><p>' + q.why + '</p></div></div></div></div>';
            }).join('') + '</div>' : '');
          $$('.it', host).forEach(function (it) { $('.hd', it).onclick = function () { it.classList.toggle('open'); }; });
          $('[data-go]', host).onclick = start;
          if (ok) { $('[data-fin]', host).onclick = function () { go(st.i + 1); }; done(s.idx); } else { save(); }
        }
        intro();
      }
    };
  };

  R.finish = function (s) {
    return {
      html: '<div class="hero fin"><div style="display:grid;gap:14px"><div class="kicker rv">Курс пройден</div>' +
        '<h1 class="t rv" style="--i:1;font-size:clamp(26px,3.6vw,48px)">' + hl(s.title) + '</h1>' +
        '<p class="lead rv" style="--i:2">' + s.lead + '</p>' +
        '<div class="res rv" style="--i:3"><div class="ring" style="--p:' + Math.max(st.e, 0) + ';width:150px;height:150px"><b style="font-size:36px">' + Math.max(st.e, 0) + '%</b></div>' +
        '<div style="flex:1;min-width:240px"><h3 style="font-family:var(--head);margin-bottom:8px">' + s.planTitle + '</h3><div class="check">' +
        s.plan.map(function (p) { return '<label><input type="checkbox"><span>' + p + '</span></label>'; }).join('') + '</div></div></div>' +
        '<div class="row rv" style="--i:4"><button class="btn primary" data-end>Завершить курс</button><span class="src endmsg"></span></div></div>' +
        '<div class="rv" style="--i:3">' + Character.html('celebrate') + '</div></div>',
      mount: function (el) {
        done(s.idx);
        $('[data-end]', el).onclick = function () {
          SCORM.score(Math.max(st.e, 0), !!st.p); SCORM.finish();
          $('.endmsg', el).textContent = 'Результат сохранён. Окно курса можно закрыть.';
          this.disabled = true;
        };
      }
    };
  };

  /* ---------- оболочка ---------- */
  var stage, crumbB, crumbS, pbar, ptxt, bPrev, bNext, count, hint;

  function shell() {
    var bars = '';
    for (var i = 0; i < 18; i++) {
      var a = (Math.sin(i * 12.9898) * 43758.5453) % 1; a = Math.abs(a);
      var b = Math.abs((Math.sin(i * 78.233) * 12543.123) % 1);
      var edge = Math.abs(i - 8.5) / 8.5;
      var h = .12 + edge * .5 + a * .22, h2 = Math.min(1, h + .12 + b * .3);
      bars += '<i style="--h:' + h.toFixed(2) + ';--h2:' + h2.toFixed(2) + ';--d:' + (6 + a * 8).toFixed(1) + 's;--dl:-' + (b * 9).toFixed(1) + 's"></i>';
    }
    document.body.innerHTML =
      '<div id="bg"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div><div class="blob b4"></div><div class="bars">' + bars + '</div><div class="vignette"></div><div class="grain"></div></div>' +
      '<div id="app"><header class="top"><img class="logo" src="img/logo-dark.png" alt="Ipak Yuli Bank">' +
      '<div class="crumb"><b></b><span></span></div><div class="prog"><div class="bar"><i></i></div><small></small></div>' +
      '<button class="iconbtn" id="mbtn" aria-label="Содержание курса"><svg viewBox="0 0 24 24"><path d="M4 7h16M4 12h16M4 17h10"/></svg></button></header>' +
      '<main id="stage"></main>' +
      '<footer class="nav"><button class="btn" id="prev">' + ARROW_L + '<span class="lbl">Назад</span></button>' +
      '<div class="count"><span id="cnt"></span><span class="hint" id="hint"></span></div>' +
      '<button class="btn primary" id="next"><span class="lbl">Далее</span>' + ARROW_R + '</button></footer></div>' +
      '<div id="shade"></div><aside id="menu" aria-label="Содержание"><header><b>Содержание</b><button class="iconbtn" id="mclose" aria-label="Закрыть"><svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6L6 18"/></svg></button></header><div class="list"></div></aside>';
    stage = $('#stage'); crumbB = $('.crumb b'); crumbS = $('.crumb span'); pbar = $('.prog .bar i'); ptxt = $('.prog small');
    bPrev = $('#prev'); bNext = $('#next'); count = $('#cnt'); hint = $('#hint');
    bPrev.onclick = function () { go(st.i - 1); };
    bNext.onclick = function () { go(st.i + 1); };
    $('#mbtn').onclick = function () { menu(true); };
    $('#mclose').onclick = $('#shade').onclick = function () { menu(false); };
    document.addEventListener('keydown', function (e) {
      if (e.target && /INPUT|TEXTAREA|VIDEO/.test(e.target.tagName)) return;
      if (e.key === 'ArrowRight' && !bNext.disabled) go(st.i + 1);
      if (e.key === 'ArrowLeft') go(st.i - 1);
      if (e.key === 'Escape') menu(false);
    });
  }

  function menu(on) {
    $('#menu').classList.toggle('on', on); $('#shade').classList.toggle('on', on);
    if (!on) return;
    var r = reach(), h = '';
    C.modules.forEach(function (m) {
      h += '<div class="mh">' + (m.num ? m.num + ' · ' : '') + m.title + '</div>';
      m.screens.forEach(function (s) {
        var ok = st.v[s.idx] > 0 && !locked(s.idx);
        h += '<button class="mi' + (s.idx === st.i ? ' cur' : '') + (ok ? ' done' : '') + '" data-i="' + s.idx + '"' + (s.idx > r ? ' disabled' : '') + '><i>✓</i><span>' + (s.menu || String(s.title || m.title).replace(/\*/g, '')) + '</span></button>';
      });
    });
    if (CFG.PRESENTATION) h += '<div class="mh">Материалы</div><a class="mi dl" href="' + CFG.PRESENTATION + '" download target="_blank" rel="noopener"><i>↓</i><span>Скачать презентацию курса (PowerPoint)</span></a>';
    var l = $('#menu .list'); l.innerHTML = h;
    $$('button.mi', l).forEach(function (b) { b.onclick = function () { menu(false); go(+b.dataset.i); }; });
    var cur = $('.mi.cur', l); if (cur) cur.scrollIntoView({ block: 'center' });
  }

  function nav() {
    var i = st.i, last = i === screens.length - 1, lk = locked(i);
    bPrev.disabled = i === 0;
    bNext.disabled = last || lk;
    bNext.style.visibility = last ? 'hidden' : '';
    count.textContent = (i + 1) + ' / ' + screens.length;
    hint.textContent = lk ? (screens[i].type === 'exam' ? 'Сдайте тест, чтобы завершить курс' : 'Выполните задание, чтобы продолжить') : '';
    var seen = st.v.filter(function (x, j) { return x > 0 && !locked(j); }).length, pct = Math.round(seen / screens.length * 100);
    pbar.style.width = pct + '%'; ptxt.textContent = pct + '% пройдено';
  }

  function go(i) {
    if (i < 0 || i >= screens.length) return;
    if (i > st.i && locked(st.i)) return;
    if (i > reach()) i = reach();
    st.i = i;
    var s = screens[i];
    if (st.v[i] === 0) st.v[i] = 1;
    var r = (R[s.type] || R.text)(s);
    stage.innerHTML = '<section class="screen" tabindex="-1"><div class="wrap' + (s.top || /quiz|exam|dialog|classify|sort|accordion|tabs|steps/.test(s.type) ? ' topalign' : '') + '">' + r.html + '</div></section>';
    document.body.classList.toggle('calm', !/hero|module|finish/.test(s.type));
    crumbB.textContent = C.title; crumbS.textContent = (s.mod.num ? 'Модуль ' + s.mod.num + ' · ' : '') + s.mod.title;
    if (r.mount) r.mount($('.screen', stage));
    nav(); save();
  }

  document.addEventListener('DOMContentLoaded', function () {
    SCORM.init(); load(); shell(); go(st.i);
    setInterval(function () { SCORM.tick(); }, 60000);
  });
  window.__course = { go: go, screens: screens, state: st };
})();
