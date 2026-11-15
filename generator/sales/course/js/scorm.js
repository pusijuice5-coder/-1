/* Обёртка SCORM: работает с SCORM 1.2 (API) и SCORM 2004 (API_1484_11).
   Если LMS не найдена (курс открыт просто в браузере) — прогресс хранится в localStorage. */
(function (g) {
  var api = null, v2004 = false, ready = false, done = false, t0 = Date.now();
  var LS = 'iyb_sales_course_v1';

  function scan(w) {
    var n = 0;
    while (w && n < 15) {
      try {
        if (w.API) { v2004 = false; return w.API; }
        if (w.API_1484_11) { v2004 = true; return w.API_1484_11; }
      } catch (e) { /* чужой домен */ }
      if (!w.parent || w.parent === w) break;
      w = w.parent; n++;
    }
    return null;
  }
  function find() {
    var a = scan(g);
    try { if (!a && g.opener) a = scan(g.opener); } catch (e) {}
    try { if (!a && g.top && g.top.opener) a = scan(g.top.opener); } catch (e) {}
    return a;
  }
  function call(fn12, fn04, a, b) {
    if (!api) return '';
    try {
      var f = v2004 ? fn04 : fn12;
      if (b !== undefined) return api[f](a, b);
      return api[f](a === undefined ? '' : a);
    } catch (e) { return ''; }
  }
  function get(k) { return String(call('LMSGetValue', 'GetValue', k) || ''); }
  function set(k, v) { return call('LMSSetValue', 'SetValue', k, String(v)); }
  function commit() { call('LMSCommit', 'Commit', ''); }

  function time12(ms) {
    var s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
    function p(n, l) { n = String(n); while (n.length < l) n = '0' + n; return n; }
    return p(h, 4) + ':' + p(m, 2) + ':' + p(x, 2) + '.00';
  }
  function time04(ms) {
    var s = Math.floor(ms / 1000), h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), x = s % 60;
    return 'PT' + h + 'H' + m + 'M' + x + 'S';
  }

  var S = {
    connected: false,
    init: function () {
      api = find();
      if (api) {
        var r = call('LMSInitialize', 'Initialize', '');
        ready = String(r) === 'true' || r === true;
      }
      S.connected = !!(api && ready);
      if (S.connected) {
        var st = v2004 ? get('cmi.completion_status') : get('cmi.core.lesson_status');
        if (!st || st === 'not attempted' || st === 'unknown') {
          if (v2004) set('cmi.completion_status', 'incomplete'); else set('cmi.core.lesson_status', 'incomplete');
        }
        set(v2004 ? 'cmi.exit' : 'cmi.core.exit', 'suspend');
        commit();
      }
      return S.connected;
    },
    /* -> {loc:'', data:''} */
    load: function () {
      if (S.connected) {
        return { loc: get(v2004 ? 'cmi.location' : 'cmi.core.lesson_location'), data: get('cmi.suspend_data') };
      }
      try { return JSON.parse(g.localStorage.getItem(LS) || '{}'); } catch (e) { return {}; }
    },
    save: function (loc, data) {
      if (S.connected) {
        set(v2004 ? 'cmi.location' : 'cmi.core.lesson_location', loc);
        set('cmi.suspend_data', data);
        S.tick();
        commit();
      } else {
        try { g.localStorage.setItem(LS, JSON.stringify({ loc: String(loc), data: data })); } catch (e) {}
      }
    },
    tick: function () {
      if (!S.connected) return;
      if (v2004) set('cmi.session_time', time04(Date.now() - t0)); else set('cmi.core.session_time', time12(Date.now() - t0));
    },
    /* pct 0..100, passed true/false */
    score: function (pct, passed) {
      if (!S.connected) return;
      if (v2004) {
        set('cmi.score.min', 0); set('cmi.score.max', 100); set('cmi.score.raw', pct); set('cmi.score.scaled', (pct / 100).toFixed(2));
        if (passed) { set('cmi.success_status', 'passed'); set('cmi.completion_status', 'completed'); }
      } else {
        set('cmi.core.score.min', 0); set('cmi.core.score.max', 100); set('cmi.core.score.raw', pct);
        if (passed) set('cmi.core.lesson_status', 'passed');
      }
      S.tick(); commit();
    },
    finish: function () {
      if (!S.connected || done) return;
      done = true; S.tick(); commit();
      call('LMSFinish', 'Terminate', '');
    },
    reset: function () { try { g.localStorage.removeItem(LS); } catch (e) {} }
  };
  g.addEventListener('pagehide', S.finish);
  g.addEventListener('beforeunload', S.finish);
  g.SCORM = S;
})(window);
