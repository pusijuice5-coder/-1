/* Общие помощники для сцен видеороликов (используются курсами, собранными на этом плеере) */
(function (g) {
  var IMG = '../course/img/character/';
  var H = {
    img: IMG,
    hl: function (t) { return String(t).replace(/\*([^*]+)\*/g, '<span class="hl2">$1</span>'); },
    who: function (p, f, cls) { return '<img class="who a ' + (cls || '') + '" data-f="' + (f || 0.04) + '" src="' + IMG + p + '.webp" alt="">'; },
    h1: function (t, f, cls) { return '<h1 class="a ' + (cls || '') + '" data-f="' + (f || 0.03) + '">' + H.hl(t) + '</h1>'; },
    sub: function (t, f) { return '<p class="sub a" data-f="' + f + '">' + t + '</p>'; },
    tile: function (n, b, s, f, cls) { return '<div class="tile pp ' + (cls || '') + '" data-f="' + f + '">' + (n ? '<div class="n">' + n + '</div>' : '') + '<b>' + b + '</b>' + (s ? '<span>' + s + '</span>' : '') + '</div>'; },
    row: function (items, style) { return '<div class="row" style="' + (style || '') + '">' + items.join('') + '</div>'; },
    arrow: function (f) { return '<div class="arrow a" data-f="' + f + '">→</div>'; },
    chips: function (items, f0, df) { return '<div class="chipsv">' + items.map(function (c, i) { return '<span class="pp" data-f="' + ((f0 || 0.3) + i * (df || 0.08)) + '">' + c + '</span>'; }).join('') + '</div>'; },
    /* крупное число/год слева + заголовок и пункты справа */
    step: function (num, title, lis, pose, o) {
      o = o || {}; var left = o.left || (String(num).length > 2 ? 520 : String(num).length > 1 ? 410 : 250);
      return '<div class="big a ' + (o.cls || '') + '" data-f="0.02">' + num + '</div><div class="stepbox" style="left:' + left + 'px;width:' + (o.width || 560) + 'px">' + H.h1(title, 0.12) +
        '<ul>' + lis.map(function (l, i) { return '<li class="a" data-f="' + (0.38 + i * (o.df || 0.2)) + '">' + l + '</li>'; }).join('') + '</ul></div>' + H.who(pose, 0.05, 'sm');
    }
  };
  g.VH = H;
})(window);
