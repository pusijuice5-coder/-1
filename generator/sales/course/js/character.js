/* Персонаж-наставник «Камила» — оригинальная векторная иллюстрация.
   Чтобы подставить своего персонажа (PNG с прозрачным фоном), положите файлы
   img/character/<поза>.png и включите CHARACTER_IMAGES в js/config.js.
   Позы: hello, point, idea, thumbs, think, celebrate */
(function (g) {
  var SKIN = '#F2C4A0', SKIN2 = '#E0A982', HAIR = '#2A1B14', JACKET = '#10A575', LAPEL = '#0A7D59', DARK = '#075E44', SHIRT = '#F4FAF7';

  function hand(type, x, y, rot, flip) {
    var s = '';
    var st = 'stroke="' + SKIN + '" stroke-linecap="round" fill="none"';
    if (type === 'open') {
      s = '<circle r="17" fill="' + SKIN + '"/>' +
        '<path d="M-10-8L-14-31M-3-13L-4-38M5-13L6-36M12-8L16-28" ' + st + ' stroke-width="8.5"/>' +
        '<path d="M-13 3L-27-7" ' + st + ' stroke-width="9"/>';
    } else if (type === 'point') {
      s = '<circle r="16" fill="' + SKIN + '"/>' +
        '<path d="M2-8L2-40" ' + st + ' stroke-width="10"/>' +
        '<path d="M-12 1L-22-9" ' + st + ' stroke-width="9"/>' +
        '<path d="M9-10q7 3 6 12" stroke="' + SKIN2 + '" stroke-width="2.5" fill="none" stroke-linecap="round"/>';
    } else if (type === 'thumb') {
      s = '<rect x="-17" y="-13" width="34" height="30" rx="13" fill="' + SKIN + '"/>' +
        '<path d="M-7-10L-9-34" ' + st + ' stroke-width="11"/>' +
        '<path d="M-2-2h14M-2 6h14" stroke="' + SKIN2 + '" stroke-width="2.5" stroke-linecap="round"/>';
    } else if (type === 'chin') {
      s = '<circle r="16" fill="' + SKIN + '"/>' +
        '<path d="M-4-8L-10-32" ' + st + ' stroke-width="9.5"/>' +
        '<path d="M8-9q6 4 5 12" stroke="' + SKIN2 + '" stroke-width="2.5" fill="none" stroke-linecap="round"/>';
    } else {
      s = '<circle r="16" fill="' + SKIN + '"/>';
    }
    return '<g transform="translate(' + x + ' ' + y + ') rotate(' + (rot || 0) + ')' + (flip ? ' scale(-1 1)' : '') + '">' + s + '</g>';
  }

  // рука: плечо -> локоть -> запястье, толстая линия-рукав + манжета + кисть
  function arm(p, cls, origin) {
    var d = 'M' + p.s[0] + ' ' + p.s[1] + 'L' + p.e[0] + ' ' + p.e[1];
    var f = 'M' + p.e[0] + ' ' + p.e[1] + 'L' + p.w[0] + ' ' + p.w[1];
    var dx = p.w[0] - p.e[0], dy = p.w[1] - p.e[1], L = Math.sqrt(dx * dx + dy * dy) || 1;
    var ux = dx / L, uy = dy / L;
    var cx = p.w[0] + ux * 6, cy = p.w[1] + uy * 6;
    var hx = p.w[0] + ux * 26, hy = p.w[1] + uy * 26;
    var rot = Math.atan2(dy, dx) * 180 / Math.PI + 90;
    var style = origin ? ' style="--ox:' + origin[0] + 'px;--oy:' + origin[1] + 'px;transform-origin:' + origin[0] + 'px ' + origin[1] + 'px"' : '';
    return '<path d="' + d + '" stroke="' + JACKET + '" stroke-width="42" stroke-linecap="round" fill="none"/>' +
      '<g' + (cls ? ' class="' + cls + '"' : '') + style + '>' +
      '<path d="' + f + '" stroke="' + JACKET + '" stroke-width="40" stroke-linecap="round" fill="none"/>' +
      '<path d="M' + p.w[0] + ' ' + p.w[1] + 'L' + cx + ' ' + cy + '" stroke="' + SHIRT + '" stroke-width="34" stroke-linecap="butt" fill="none"/>' +
      hand(p.h, hx, hy, rot + (p.hr || 0), p.flip) + '</g>';
  }

  var REST_L = { s: [112, 284], e: [92, 356], w: [100, 440], h: 'rest' };
  var REST_R = { s: [248, 284], e: [268, 356], w: [260, 440], h: 'rest' };
  var POSES = {
    hello: { l: REST_L, r: { s: [248, 284], e: [300, 312], w: [318, 236], h: 'open', flip: 1 }, rc: 'wave', ro: [300, 312], mouth: 'open' },
    point: { l: REST_L, r: { s: [248, 284], e: [296, 322], w: [334, 268], h: 'point', flip: 1, hr: 14 }, mouth: 'smile' },
    idea: { l: REST_L, r: { s: [248, 284], e: [300, 326], w: [304, 248], h: 'point', flip: 1 }, mouth: 'open', extra: 'bulb' },
    thumbs: { l: REST_L, r: { s: [248, 284], e: [298, 328], w: [296, 262], h: 'thumb', flip: 1 }, mouth: 'open' },
    think: { l: { s: [112, 284], e: [100, 352], w: [206, 352], h: 'rest' }, r: { s: [248, 284], e: [276, 352], w: [226, 250], h: 'chin', hr: -6 }, mouth: 'hm', eyes: 'up', front: 'r' },
    celebrate: { l: { s: [112, 284], e: [58, 262], w: [42, 186], h: 'open' }, r: { s: [248, 284], e: [302, 262], w: [318, 186], h: 'open', flip: 1 }, mouth: 'open', extra: 'confetti' }
  };

  function svg(pose) {
    var P = POSES[pose] || POSES.hello;
    var mouth = P.mouth === 'open'
      ? '<path d="M160 170Q181 198 202 170Q181 176 160 170Z" fill="#8E2F2A"/><path d="M165 172Q181 178 197 172Q181 181 165 172Z" fill="#fff"/>'
      : P.mouth === 'hm'
        ? '<path d="M168 176Q181 182 196 173" stroke="#A8483F" stroke-width="4" stroke-linecap="round" fill="none"/>'
        : '<path d="M162 171Q181 190 200 171" stroke="#A8483F" stroke-width="4.5" stroke-linecap="round" fill="none"/>';
    var ey = P.eyes === 'up' ? -3 : 0, ex = P.eyes === 'up' ? 3 : 0;
    var eyes = '<g class="blink"><ellipse cx="' + (159 + ex) + '" cy="' + (143 + ey) + '" rx="6.5" ry="8.5" fill="#1D2925"/><ellipse cx="' + (203 + ex) + '" cy="' + (143 + ey) + '" rx="6.5" ry="8.5" fill="#1D2925"/>' +
      '<circle cx="' + (161.5 + ex) + '" cy="' + (140 + ey) + '" r="2.2" fill="#fff"/><circle cx="' + (205.5 + ex) + '" cy="' + (140 + ey) + '" r="2.2" fill="#fff"/></g>';
    var extra = '';
    if (P.extra === 'bulb') {
      extra = '<g class="floaty"><circle cx="318" cy="128" r="30" fill="#34D399" opacity=".18"/><path d="M318 104a20 20 0 0 1 11 37v8h-22v-8a20 20 0 0 1 11-37z" fill="#FDE68A"/><rect x="309" y="151" width="18" height="9" rx="3" fill="#D6E4DD"/>' +
        '<path d="M318 86v-9M290 100l-7-6M346 100l7-6" stroke="#FDE68A" stroke-width="4" stroke-linecap="round"/></g>';
    } else if (P.extra === 'confetti') {
      var c = [[20, 110, '#6EE7B7'], [70, 70, '#4CEA4C'], [120, 40, '#FDE68A'], [240, 36, '#6EE7B7'], [296, 78, '#FDE68A'], [344, 112, '#4CEA4C'], [180, 16, '#34D399'], [8, 200, '#FDE68A'], [352, 204, '#6EE7B7']];
      extra = '<g class="floaty">' + c.map(function (q, i) { return '<rect x="' + q[0] + '" y="' + q[1] + '" width="10" height="10" rx="2.5" fill="' + q[2] + '" transform="rotate(' + (i * 37) + ' ' + q[0] + ' ' + q[1] + ')"/>'; }).join('') + '</g>';
    }
    var armL = arm(P.l, P.lc, P.lo), armR = arm(P.r, P.rc, P.ro);
    return '<svg viewBox="-20 0 400 430" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Наставник Камила">' +
      '<defs><clipPath id="cut"><rect x="-20" y="0" width="400" height="430"/></clipPath>' +
      '<linearGradient id="jk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14B884"/><stop offset="1" stop-color="#0B8F66"/></linearGradient></defs>' +
      '<g clip-path="url(#cut)">' + extra +
      // волосы сзади
      '<path d="M112 150C104 78 142 40 181 40C222 40 258 78 250 150C254 196 252 226 244 250L118 250C110 226 108 196 112 150Z" fill="' + HAIR + '"/>' +
      (P.front === 'r' ? armL : armL + armR) +
      // шея
      '<path d="M163 196h36v40q-18 14-36 0z" fill="' + SKIN2 + '"/>' +
      // жакет
      '<path d="M90 440C88 340 100 268 150 250L181 242L212 250C262 268 274 340 272 440Z" fill="url(#jk)"/>' +
      // блузка
      '<path d="M157 244L181 318L205 244Q181 256 157 244Z" fill="' + SHIRT + '"/>' +
      // лацканы
      '<path d="M150 250L181 318L170 344L136 282Z" fill="' + LAPEL + '"/><path d="M212 250L181 318L192 344L226 282Z" fill="' + LAPEL + '"/>' +
      '<circle cx="181" cy="372" r="5.5" fill="' + DARK + '"/>' +
      // бейдж
      '<rect x="218" y="318" width="30" height="20" rx="4" fill="#F4FAF7"/><rect x="223" y="324" width="12" height="3" rx="1.5" fill="' + JACKET + '"/><rect x="223" y="330" width="20" height="3" rx="1.5" fill="#B7CEC4"/>' +
      // голова
      '<circle cx="123" cy="148" r="10" fill="' + SKIN2 + '"/><circle cx="239" cy="148" r="10" fill="' + SKIN2 + '"/>' +
      '<circle cx="121" cy="162" r="4" fill="#34D399"/><circle cx="241" cy="162" r="4" fill="#34D399"/>' +
      '<ellipse cx="181" cy="140" rx="58" ry="66" fill="' + SKIN + '"/>' +
      // чёлка
      '<path d="M121 138C114 84 150 56 188 58C228 60 248 98 241 140C232 112 214 94 186 90C170 108 146 122 121 138Z" fill="' + HAIR + '"/>' +
      '<path d="M146 124q12-8 25-3M191 121q13-5 25 3" stroke="' + HAIR + '" stroke-width="4" stroke-linecap="round" fill="none"/>' +
      eyes +
      '<circle cx="146" cy="166" r="10" fill="#F28B79" opacity=".38"/><circle cx="216" cy="166" r="10" fill="#F28B79" opacity=".38"/>' +
      '<path d="M181 150q-4 10 2 13" stroke="' + SKIN2 + '" stroke-width="3" stroke-linecap="round" fill="none"/>' +
      mouth +
      (P.front === 'r' ? armR : '') +
      '</g></svg>';
  }

  g.Character = {
    poses: Object.keys(POSES),
    svg: svg,
    html: function (pose) {
      if (g.COURSE_CONFIG && g.COURSE_CONFIG.CHARACTER_IMAGES) {
        return '<div class="char"><img src="img/character/' + pose + '.png" alt="Наставник"></div>';
      }
      return '<div class="char">' + svg(pose) + '</div>';
    }
  };
})(window);
