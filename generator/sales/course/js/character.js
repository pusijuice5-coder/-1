/* Персонаж-наставник: иллюстрации «Варя» (mishakuz.ru/illustrations), PNG/WebP без фона.
   Лицензия автора: бесплатно для личных и коммерческих проектов; перепродажа и
   распространение набором запрещены.
   Файлы лежат в img/character/<поза>.webp */
(function (g) {
  var POSES = ['explain', 'celebrate', 'thumbs', 'stop', 'tada', 'phone', 'books', 'smile', 'think', 'curious', 'idea', 'doubt',
    'worry', 'proud', 'listen', 'wink', 'tasks', 'search', 'hear', 'full', 'point', 'ok', 'no', 'down', 'phonejoy'];
  g.Character = {
    poses: POSES,
    src: function (pose) { return 'img/character/' + (POSES.indexOf(pose) >= 0 ? pose : 'smile') + '.webp'; },
    /* flip — отразить по горизонтали (например, чтобы жест был направлен к тексту) */
    html: function (pose, flip) {
      return '<div class="char' + (flip ? ' flipx' : '') + '"><img src="' + this.src(pose) + '" alt="" draggable="false"></div>';
    }
  };
})(window);
