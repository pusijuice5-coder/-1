// Слайды для экрана: 24 штуки. timer — минуты обратного отсчёта на слайде.
import { WARMUP, RULES, SCORING, ROLES, ALIBI } from './forms.mjs';
import { METHOD, BIASES } from './guide.mjs';

const half = Math.ceil(WARMUP.items.length / 2);
const fvList = (withKey) => `
<div class="s-cols">
${[WARMUP.items.slice(0, half), WARMUP.items.slice(half)].map((col, c) => `<ol class="s-fv" start="${c * half + 1}">${col.map((it) => `<li>${withKey ? `<b class="s-badge s-${it[1] === 'Ф' ? 'f' : 'v'}">${it[1]}</b>` : ''}<span>${it[0]}</span></li>`).join('')}</ol>`).join('')}
</div>`;

const round = (n, name, docs, task, tip) => `
<p class="s-kicker">Раунд ${n}</p>
<h2 class="s-big">«${name}»</h2>
<p class="s-lead">Конверт ${n} · ${docs}</p>
<p class="s-task">${task}</p>
<p class="s-tip">${tip}</p>`;

const version = (n) => `
<p class="s-kicker">Протокол версий</p>
<h2 class="s-big">Версия № ${n}</h2>
<p class="s-task">Запишите в лист заключения: кого вы подозреваете и на сколько процентов уверены.</p>
<p class="s-tip">Вслух не говорим. Одна минута.</p>`;

export const SLIDES = [
  { name: 'Титул', kind: 'cover', body: `
<p class="s-kicker">Бизнес-игра</p>
<h1 class="s-hero">Шерлок</h1>
<p class="s-sub">Дело о платеже № 318</p>
<p class="s-stamp">870 000 000 сум</p>` },

  { name: 'Что тренируем', title: 'Что мы сегодня тренируем', body: `
<ol class="s-three">
<li><b>Отделять факты от версий</b><span>Что написано в документе, а что мы додумали сами</span></li>
<li><b>Замечать детали</b><span>И сводить их из разных источников в одну картину</span></li>
<li><b>Доказывать выводы</b><span>Утверждение, доказательство, источник</span></li>
</ol>
<p class="s-strip">3 часа · 3 конверта · 15 документов · 1 виновный</p>` },

  { name: 'Разминка', title: 'Разминка: факт или версия?', timer: 3, body: `
<p class="s-story">${WARMUP.story}</p>
<p class="s-legend"><b class="s-badge s-f">Ф</b> факт: прямо следует из текста &nbsp;&nbsp; <b class="s-badge s-v">В</b> версия: в тексте этого нет</p>
${fvList(false)}` },

  { name: 'Разминка: ответы', title: 'Фактов всего четыре', body: `
${fvList(true)}
<p class="s-strip">Остальное мы достроили сами. Весь день спрашивайте себя: в каком документе это написано?</p>` },

  { name: 'Легенда', title: 'Пятница, 14 марта, 16:59', body: `
<p class="s-task">Со счёта ООО «Гранд Текстиль» уходит 870 000 000 сум. В понедельник клиент заявляет: такого платежа он не отправлял. Деньги уже обналичены.</p>
<p class="s-lead">Вы — рабочая группа служебного расследования «Чинор Банка». Директор филиала ждёт ответы:</p>
<ol class="s-four">
<li>Кто это сделал?</li>
<li>Как именно?</li>
<li>Почему не сработали контроли?</li>
<li>Что изменить?</li>
</ol>` },

  { name: 'Правила', title: 'Шесть правил', body: `
<ol class="s-rules">${RULES.map((r) => `<li>${r}</li>`).join('')}</ol>` },

  { name: 'Роли', title: 'Роли в команде', body: `
<div class="s-cards">${ROLES.map((r) => `<div><b>${r[0]}</b><span>${r[2]}</span></div>`).join('')}</div>
<p class="s-strip">Распределите карточки ролей за одну минуту</p>` },

  { name: 'Баллы', title: 'Как считаются баллы', body: `
<div class="s-score">${SCORING.map((s) => `<div><b>${s[2]}</b><span>${s[0]}</span></div>`).join('')}</div>
<p class="s-task">Оценивается только то, что записано в листе заключения.</p>
<p class="s-tip">Подсказка: минус 5 баллов, не больше трёх. Минута опоздания: минус 5 баллов.</p>` },

  { name: 'Раунд 1', kind: 'round', timer: 25, body: round(1, 'Сигнал', '6 документов', 'Поймите, что произошло, и постройте первую версию.', 'Записывайте факты с номером документа.') },
  { name: 'Версия № 1', kind: 'round', timer: 1, body: version(1) },
  { name: 'Раунд 2', kind: 'round', timer: 25, body: round(2, 'Следы', '5 документов', 'Проверьте версию. Что её подтверждает? Что опровергает?', 'Запись в журнале и человек — не одно и то же.') },
  { name: 'Версия № 2', kind: 'round', timer: 1, body: version(2) },
  { name: 'Раунд 3', kind: 'round', timer: 30, body: round(3, 'Развязка', '4 документа', '20 минут на анализ, 10 минут на заключение.', 'Заключение сдаётся ровно по таймеру.') },

  { name: 'Перерыв', kind: 'round', timer: 10, body: `
<p class="s-kicker">Заключения сданы</p>
<h2 class="s-big">Перерыв</h2>
<p class="s-task">Ведущий считает баллы. Встречаемся через 10 минут.</p>` },

  { name: 'Вердикты команд', title: 'Вердикты команд', body: `
<p class="s-task">Одна минута на команду:</p>
<ol class="s-four">
<li>Кого вы назвали?</li>
<li>Какое доказательство считаете главным?</li>
</ol>` },

  { name: 'Разгадка: кто где был', kind: 'dense', title: 'Кто мог сидеть за компьютером?', body: `
<table class="s-table">
<thead><tr><th>Сотрудник</th><th>11 марта, 13:12 · смена телефона</th><th>14 марта, 16:51–16:53 · ввод платежа</th></tr></thead>
<tbody>${ALIBI.map((a, i) => `<tr${i === ALIBI.length - 1 ? ' class="hit"' : ''}><td>${a[0]}</td><td>${a[1]}</td><td>${a[3]}</td></tr>`).join('')}</tbody>
</table>` },

  { name: 'Разгадка: схема', kind: 'dense', title: 'Как это было сделано', body: `
<ol class="s-timeline">
<li><b>7 марта</b><span>Алиев диктует Рахимовой свой пароль по телефону</span></li>
<li><b>11 марта, 13:12</b><span>С незаблокированного компьютера стажёра она меняет телефон клиента на номер брата</span></li>
<li><b>14 марта, 16:40</b><span>Алиев ушёл. Стажёра она отправляет в архив</span></li>
<li><b>16:45</b><span>Звонит брату со своего рабочего телефона</span></li>
<li><b>16:51–16:53</b><span>Входит под паролем Алиева, вводит платёж, подкладывает поддельное поручение</span></li>
<li><b>16:56</b><span>Контролёр звонит по подменённому номеру. «Директор» подтверждает</span></li>
</ol>` },

  { name: 'Разгадка: доказательства', title: 'Что её выдало', body: `
<ol class="s-three">
<li><b>Звонок в 16:45</b><span>С номера 114 на подменённый номер. Платежа в системе ещё не было</span></li>
<li><b>Рахимов Д. А.</b><span>Директор «Вега Трейд» и её экстренный контакт: брат</span></li>
<li><b>Две неправды</b><span>«Разбирала очередь» — операций нет. «Не говорила по телефону» — говорила</span></li>
</ol>
<p class="s-strip">Лучший сотрудник квартала. Взысканий нет.</p>` },

  { name: 'Что не сработало', title: 'Каждое правило нарушено чуть-чуть', body: `
<ol class="s-rules">
<li>Пароль продиктован вслух</li>
<li>Компьютер оставлен незаблокированным</li>
<li>Изменение утверждено без заявления</li>
<li>Звонок по номеру, который сменили три дня назад</li>
<li>Поручение принято без отметки «Принято»</li>
<li>Подпись проверена в спешке перед отсечкой</li>
</ol>` },

  { name: 'Дебриф', title: 'Давайте разберём', body: `
<ol class="s-four">
<li>Кого вы подозревали после первого раунда? Что заставило передумать?</li>
<li>Какой документ оказался важнее, чем выглядел?</li>
<li>Что в работе команды помогало, а что мешало?</li>
<li>Где это встречается в вашей работе?</li>
</ol>` },

  { name: 'Метод Шерлока', title: 'Метод Шерлока', body: `
<ol class="s-method">${METHOD.map((m) => `<li><b>${m[0]}</b><span>${m[1]}</span></li>`).join('')}</ol>` },

  { name: 'Ловушки мышления', title: 'Ловушки мышления', body: `
<ol class="s-method">${BIASES.map((m) => `<li><b>${m[0]}</b><span>${m[1]}</span></li>`).join('')}</ol>` },

  { name: 'С понедельника я…', kind: 'round', timer: 5, body: `
<p class="s-kicker">Перенос в работу</p>
<h2 class="s-big">С понедельника я…</h2>
<p class="s-task">Одно действие, которое вы начнёте делать в работе. Что, когда, в какой ситуации.</p>
<p class="s-tip">3 минуты на карточку, затем расскажите соседу.</p>` },

  { name: 'Дело закрыто', kind: 'cover', body: `
<p class="s-kicker">Спасибо за работу</p>
<h1 class="s-hero">Дело закрыто</h1>
<p class="s-sub">Заполните, пожалуйста, анкету</p>` },
];

export function renderSlide(s, i, total) {
  return `
<div class="slide" data-i="${i}"${s.timer ? ` data-timer="${s.timer}"` : ''}>
  <div class="slide-in ${s.kind ? `k-${s.kind}` : ''}">
    <div class="s-top"><span>Шерлок · дело № 27-Р</span><span>${i + 1} / ${total}</span></div>
    ${s.title ? `<h2 class="s-title">${s.title}</h2>` : ''}
    <div class="s-body">${s.body}</div>
    ${s.timer ? `<div class="s-timer" aria-live="off">${String(s.timer).padStart(2, '0')}:00</div>` : ''}
  </div>
</div>`;
}
