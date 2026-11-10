# -*- coding: utf-8 -*-
"""Раздаточные материалы игры «Экспансия». Запуск: python3 pdf_handouts.py -> ../2_Razdatochnye_materialy.pdf"""
import os
import game as G
from content import texts as T
from pdf_common import *

OUT = os.path.join(HERE, '..', '2_Razdatochnye_materialy.pdf')
T.check()
P = G.P


def lines(n):
    return '<div class="lines">%s</div>' % ('<div></div>' * n)


def fmt(v):
    s = ('%.1f' % v).replace('.', ',')
    return s[:-2] if s.endswith(',0') else s


EXTRA = """
.tag { font-size: 8pt; font-weight: 700; color: #02691A; text-transform: none; margin-bottom: 1.5mm }
.big { font-size: 24pt; font-weight: 700; color: #02691A; line-height: 1 }
.facts { display: grid; grid-template-columns: repeat(4, 1fr); gap: 3mm }
.facts .card { padding: 3.4mm 3.8mm }
.facts .card p { margin: 1.2mm 0 0; font-size: 9pt; color: #3D4C43 }
.news { display: grid; gap: 2.6mm }
.news .card { display: grid; grid-template-columns: 52mm 1fr; gap: 4mm; align-items: center; padding: 3.4mm 4.6mm }
.news b { font-size: 10.5pt; line-height: 1.25 }
.news span { color: #3D4C43 }
.roles { display: grid; grid-template-columns: 1fr 1fr; gap: 0 }
.roles .rc { border: 0.3mm dashed #8A988F; padding: 7mm 7mm; height: 68mm; margin: -0.15mm }
.roles h3 { font-size: 14pt; margin: 0 0 3mm; color: #02691A }
.roles p { font-size: 11pt; line-height: 1.4 }
.fieldrow { display: flex; gap: 8mm; align-items: flex-end; margin-bottom: 4mm; font-size: 10.5pt }
.fieldrow .fill { flex: 1 }
.q { font-weight: 700; margin: 4.5mm 0 0.5mm; font-size: 10.5pt }
.q small { font-weight: 400; color: #5E6E64; font-size: 8.5pt }
.opts { display: flex; gap: 9mm; margin: 2mm 0 1mm; font-size: 10.5pt }
.calc td { height: 9mm }
.calc td.lab { width: auto }
.calc td.val { width: 26mm }
.scale { font-feature-settings: "tnum"; letter-spacing: 0.25em; white-space: nowrap; text-align: center; width: 44mm }
.half { height: 119mm; display: flex; flex-direction: column }
.memo { border: 0.35mm solid #02691A; border-radius: 2.5mm; padding: 6mm 7mm; flex: 1 }
.memo h2 { margin-top: 0; font-size: 15pt }
.memo li { font-size: 10.5pt; margin-bottom: 2.2mm }
.stamp { display: inline-block; border: 0.35mm solid #02691A; color: #02691A; border-radius: 1.2mm; padding: 0.6mm 2.4mm; font-size: 8pt; font-weight: 700 }
.pers { height: 113mm; padding: 1mm 0 }
.kv td { font-size: 9.2pt }
.obs td { height: 9.5mm }
.compact td { padding: 1.05mm 2.2mm; font-size: 9pt }
.compact th { padding: 1.4mm 2.2mm }
.eq { table-layout: fixed }
.eq th:first-child, .eq td:first-child { width: 46mm }
.tight td { padding: 1.4mm 2.2mm }
.tight h2 { margin-top: 4.5mm }
"""

pages = []        # (секция, html)


def add(section, label, body):
    pages.append((section, label, body))


# ---------------------------------------------------------------- Досье рынка
rows = ''.join('<tr><td><b>%s</b></td><td>%s</td><td class="n"><b>%d</b></td><td>%s</td></tr>' % (
    G.REGION_FULL[r], T.REGION_INFO[r]['text'], G.POOL[r][0], T.REGION_INFO[r]['outlook']) for r in G.REGIONS)
start_profit = P['start_offices'] * (G.POOL['CAP'][0] / P['start_offices']) - P['start_offices'] * (P['upkeep'] + P['base_loss'])
add('dossier', 'Досье рынка · лист 1 из 2', """<div class="tight">
<h1>Досье рынка</h1>
<p class="lead" style="margin-bottom:3mm">Вы — правление банка. Банк работает только в Столице: у него два офиса и 100 млрд сум на развитие. Акционеры ждут, что за четыре года вы выйдете в регионы и вырастите стоимость банка. Того же хотят конкуренты.</p>
<h2>Пять регионов</h2>
<table><tr><th style="width:36mm">Регион</th><th>Что за рынок</th><th class="n" style="width:24mm">Объём рынка, год 1</th><th style="width:60mm">Чего ждать</th></tr>%s</table>
<p class="small" style="margin-top:2.5mm">Объём рынка — доход, который за год получат все банки региона вместе. В таблице он указан в млрд сум в расчёте на один банк-участник: если в игре четыре банка, объём рынка Столицы равен 4 × 60 = 240. Цифры для вашей игры ведущий показывает на табло.</p>
<h2>Ваш банк на старте</h2>
<div class="facts">
<div class="card"><div class="big">2</div><p>офиса, оба в Столице</p></div>
<div class="card"><div class="big">100</div><p>млрд сум — бюджет развития</p></div>
<div class="card"><div class="big">1-й</div><p>уровень всех четырёх функций</p></div>
<div class="card"><div class="big">%s</div><p>млрд сум — прибыль прошлого года</p></div>
</div>
<h2>Что будет на табло после каждого года</h2>
<ul>
<li>Итоги всех банков: доход, расходы, прибыль, бюджет и стоимость.</li>
<li>Карта рынка: сколько офисов у каждого банка в каждом регионе и сколько офисов рынок региона может загрузить.</li>
<li>Уровни функций всех банков.</li>
<li>Прогноз объёма рынка на следующий год: от и до.</li>
</ul></div>""" % (rows, fmt(start_profit)))

news1 = ''.join('<div class="card"><b>%s</b><span>%s</span></div>' % n for n in T.NEWS[1])
add('dossier', 'Досье рынка · лист 2 из 2', """
<h1>Что известно о рынке сейчас</h1>
<p class="lead">Новости перед первым годом. Что из этого важно для вашей стратегии, решать вам.</p>
<div class="news">%s</div>
<h2>Словарь</h2>
<table class="kv">
<tr><td style="width:44mm"><b>Объём рынка</b></td><td>Доход, который за год получат все банки региона вместе.</td></tr>
<tr><td><b>Теснота</b></td><td>Офисов в регионе больше, чем рынок может загрузить. Объём рынка делится между банками, и каждый офис зарабатывает меньше 45.</td></tr>
<tr><td><b>Кредитные потери</b></td><td>Кредиты, которые не вернули. В обычный год — 3 на офис. В год спада в регионе — намного больше.</td></tr>
<tr><td><b>Норма управляемости</b></td><td>Сколько офисов банк ведёт без потери качества. Зависит от уровня функции «Команда»: 4, 6, 8 или 10 офисов.</td></tr>
<tr><td><b>Бюджет</b></td><td>Деньги банка на развитие. Каждый год он уменьшается на стоимость решений и увеличивается на прибыль.</td></tr>
<tr><td><b>Стоимость банка</b></td><td>Бюджет на конец года плюс две прибыли этого года. По ней определяется победитель.</td></tr>
</table>
<h2>Совет правлению</h2>
<p>Прежде чем открывать офис, прикиньте, сколько банков придут в тот же регион. Рынок, который сегодня просторен, через год может оказаться тесным.</p>""" % news1)

# ---------------------------------------------------------------- Правила
frows = ''.join('<tr><td style="width:42mm"><b>%s</b></td><td>%s</td></tr>' % f for f in T.FUNC_INFO)
add('rules', 'Правила игры · лист 1 из 2', """
<h1>Правила игры</h1>
<div class="card dark" style="margin-bottom:4mm"><b>Цель.</b> Через четыре года у вашего банка должна быть самая высокая стоимость.<br>Стоимость банка = бюджет на конец 4-го года + две прибыли 4-го года.</div>
<h2 style="margin-top:3mm">Каждый год правление принимает четыре решения</h2>
<table><tr><th style="width:40mm">Решение</th><th>Что выбираете</th><th style="width:58mm">Цена, млрд сум</th></tr>
<tr><td><b>Сеть</b></td><td>Где открыть офисы и какие закрыть</td><td>Открыть офис — %(open)d. Закрыть — бесплатно</td></tr>
<tr><td><b>Функции</b></td><td>Какие из четырёх функций поднять на уровень</td><td>До 2-го уровня — %(l2)d, до 3-го — %(l3)d, до 4-го — %(l4)d</td></tr>
<tr><td><b>Кредитная политика</b></td><td>Осторожная, сбалансированная или агрессивная</td><td>Бесплатно</td></tr>
<tr><td><b>Аналитический обзор</b></td><td>Покупать ли точный прогноз на год. Со 2-го года</td><td>%(an)d</td></tr></table>
<p class="small" style="margin-top:2mm">Потратить больше, чем есть в бюджете, нельзя. Непотраченное остаётся на следующий год.</p>
<h2>Офисы</h2>
<ul>
<li>Офис зарабатывает до %(cap)d в год. В год открытия — половину.</li>
<li>Содержание офиса — %(up)d в год.</li>
<li>Кредитные потери — %(bl)d на офис в обычный год. В год спада в регионе потери намного выше.</li>
<li>У региона есть объём рынка. Пока офисов мало, каждый зарабатывает свои %(cap)d. Когда офисов больше, чем рынок может загрузить, объём делится между банками по числу офисов.</li>
<li>Офис можно закрыть. С начала года он перестаёт приносить доход и расходы. Деньги, потраченные на открытие, не возвращаются.</li>
</ul>
<h2>Функции банка</h2>
<table><tr><th>Функция</th><th>Что даёт</th></tr>%(frows)s</table>
<p class="small" style="margin-top:2mm">У каждой функции четыре уровня. За год можно подняться на один уровень. Функция, оставшаяся на 1-м уровне, — слабое место банка: на рынке случаются события, которые бьют именно по слабым местам.</p>
""" % dict(open=P['open_cost'], l2=P['level_cost'][2], l3=P['level_cost'][3], l4=P['level_cost'][4], an=P['analytics'], cap=P['capacity'], up=P['upkeep'], bl=P['base_loss'], frows=frows))

ex = T.example_year()
prow = ''.join('<tr><td><b>%s — %s</b></td><td>%s</td><td>%s</td></tr>' % (p[0], p[1].lower(), p[2], p[3]) for p in T.POLICY_INFO)
add('rules', 'Правила игры · лист 2 из 2', """<div class="tight">
<h1>Как считается год</h1>
<h2 style="margin-top:2mm">Кредитная политика</h2>
<table><tr><th style="width:52mm">Политика</th><th>Доход</th><th>Кредитные потери</th></tr>%(prow)s</table>
<p class="small" style="margin-top:2mm">Политика выбирается на год и действует на все офисы банка. В следующем году её можно сменить.</p>
<h2>Две формулы</h2>
<div class="grid2">
<div class="card"><b>Прибыль года</b> = доход − содержание офисов − кредитные потери − ущерб от событий</div>
<div class="card"><b>Бюджет на конец года</b> = бюджет на начало − стоимость решений + прибыль года</div>
</div>
<h2>Пример</h2>
<p>В игре четыре банка. Ваш банк в первом году открывает офис на Севере и поднимает цифровые каналы до 2-го уровня. Остальные банки ничего не меняют.</p>
<table>
<tr><th>Строка расчёта</th><th>Как получилось</th><th class="r" style="width:26mm">Млрд сум</th></tr>
<tr><td>Стоимость решений</td><td>Офис 25 + функция 20</td><td class="r">45</td></tr>
<tr><td>Доход в Столице</td><td>Объём рынка 240 делят 8 офисов: по 30 на офис, у вас два</td><td class="r">60</td></tr>
<tr><td>Доход на Севере</td><td>Офис новый, работает вполсилы: 45 / 2</td><td class="r">22,5</td></tr>
<tr><td>Содержание офисов</td><td>3 офиса × 6 (цифровые каналы 2-го уровня снижают 8 до 6)</td><td class="r">−%(up)s</td></tr>
<tr><td>Кредитные потери</td><td>3 офиса × 3</td><td class="r">−%(bl)s</td></tr>
<tr class="sum"><td>Прибыль года</td><td>60 + 22,5 − 18 − 9</td><td class="r">%(pr)s</td></tr>
<tr class="sum"><td>Бюджет на конец года</td><td>100 − 45 + 55,5</td><td class="r">%(bu)s</td></tr>
</table>
<p class="small" style="margin-top:2mm">Считать вручную не нужно: итоги года считает ведущий. Пример показывает, из чего складывается прибыль.</p>
<h2>Частые вопросы</h2>
<table class="kv">
<tr><td style="width:74mm"><b>Можно открыть несколько офисов в одном регионе?</b></td><td>Да, сколько позволяет бюджет.</td></tr>
<tr><td><b>Можно поднять функцию сразу на два уровня?</b></td><td>Нет. Один уровень на функцию в год.</td></tr>
<tr><td><b>Что, если бюджет ушёл в минус?</b></td><td>Игра продолжается. Пока бюджет отрицательный, открывать офисы и повышать функции нельзя.</td></tr>
<tr><td><b>Можно изменить бланк после сдачи?</b></td><td>Нет. Исправляются только арифметические ошибки, вместе с ведущим.</td></tr>
</table></div>""" % dict(prow=prow, up=fmt(ex['upkeep']), bl=fmt(ex['base_loss']), pr=fmt(ex['profit']), bu=fmt(ex['budget_end'])))

# ---------------------------------------------------------------- Роли
add('roles', 'Карточки ролей · разрезать', '<div class="roles">%s</div>' % ''.join('<div class="rc"><h3>%s</h3><p>%s</p></div>' % r for r in T.ROLES))

# ---------------------------------------------------------------- Стратегия
add('strategy', 'Стратегия банка', """
<h1>Стратегия банка</h1>
<p class="lead" style="margin-bottom:3mm">Заполняется до начала первого года. Лист остаётся у правления: в конце игры вы сравните его с результатом.</p>
<div class="fieldrow"><span>Название банка</span><span class="fill"></span><span>Председатель правления</span><span class="fill"></span></div>
<p class="q">1. Где наш банк зарабатывает через четыре года <small>два-три региона, которые для нас главные</small></p>%s
<p class="q">2. От чего мы отказываемся</p>%s
<p class="q">3. Наше отношение к риску</p>
<div class="opts"><span><i class="cb"></i>осторожное</span><span><i class="cb"></i>умеренное</span><span><i class="cb"></i>смелое</span></div>
<p class="small">Почему:</p>%s
<p class="q">4. Какие функции усиливаем в первую очередь и зачем</p>%s
<p class="q">5. Что может сломать нашу стратегию и что мы тогда сделаем</p>%s
<p class="q">6. Наша цель</p>
<div class="fieldrow" style="margin-top:2mm"><span>Стоимость банка через четыре года:</span><span class="fill" style="flex:none;width:34mm"></span><span>млрд сум</span></div>
""" % (lines(3), lines(2), lines(2), lines(3), lines(3)))


# ---------------------------------------------------------------- Бланки решений
def decision_form(year):
    regs = ''.join('<th>%s</th>' % G.REGION_NAME[r] for r in G.REGIONS)
    funs = ''.join('<th>%s</th>' % f[0] for f in T.FUNC_INFO)
    empty5, empty4 = '<td></td>' * 5, '<td></td>' * 4
    an = ('<p style="margin-top:2mm;font-size:10.5pt"><i class="cb"></i>покупаем за %d млрд сум</p>' % P['analytics']) if year > 1 else '<p class="muted" style="margin-top:2mm">В первом году не продаётся.</p>'
    return """
<h1>Бланк решений. Год %(y)d</h1>
<div class="fieldrow"><span>Банк</span><span class="fill"></span><span>Бюджет на начало года</span><span class="fill" style="flex:none;width:28mm"></span><span>млрд сум</span></div>
<h2 style="margin-top:2mm">1. Сеть</h2>
<table class="form eq"><tr><th></th>%(regs)s</tr>
<tr><td class="lab">Офисов сейчас</td>%(e5)s</tr>
<tr><td class="lab">Открыть (+), закрыть (−)</td>%(e5)s</tr></table>
<h2>2. Функции</h2>
<table class="form eq"><tr><th></th>%(funs)s</tr>
<tr><td class="lab">Уровень сейчас</td>%(e4)s</tr>
<tr><td class="lab">Повышаем: поставьте ✓</td>%(e4)s</tr></table>
<h2>3. Кредитная политика</h2>
<p style="margin-top:2mm;font-size:10.5pt"><i class="cb"></i>О — осторожная &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i class="cb"></i>С — сбалансированная &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <i class="cb"></i>А — агрессивная</p>
<h2>4. Аналитический обзор</h2>%(an)s
<h2>Сколько стоят решения</h2>
<table class="form calc">
<tr><td class="lab">Новые офисы: число × %(open)d</td><td class="val"></td><td class="lab">Повышение функций</td><td class="val"></td></tr>
<tr><td class="lab">Аналитический обзор</td><td class="val"></td><td class="lab"><b>Итого, не больше бюджета</b></td><td class="val"></td></tr>
</table>
<div class="fieldrow" style="margin-top:4mm;margin-bottom:0"><span><b>Наш прогноз прибыли на этот год</b></span><span class="fill" style="flex:none;width:30mm"></span><span>млрд сум</span></div>
<div class="cutline" style="margin-top:3.5mm;margin-bottom:4mm"></div>
<h2 style="margin-top:0">Итоги года <span class="small" style="font-weight:400">заполните по табло</span></h2>
<table class="form"><tr><th>Доход</th><th>Расходы на сеть</th><th>Кредитные потери</th><th>События</th><th>Прибыль</th><th>Бюджет на конец года</th><th>Стоимость банка</th><th>Место</th></tr>
<tr>%(e8)s</tr></table>
<p class="q">Что нас удивило в этом году</p>%(ln)s
""" % dict(y=year, regs=regs, funs=funs, e5=empty5, e4=empty4, e8='<td></td>' * 8, an=an, open=P['open_cost'], ln=lines(2))


for y in G.YEARS:
    add('forms', 'Бланк решений · год %d' % y, decision_form(y))

# ---------------------------------------------------------------- Отчёт акционерам
add('report', 'Отчёт акционерам', """
<h1>Отчёт акционерам</h1>
<p class="lead" style="margin-bottom:3mm">На подготовку 8 минут, на выступление 2 минуты. Отвечайте коротко и по делу: акционеров интересуют решения, а не оправдания.</p>
<div class="fieldrow"><span>Банк</span><span class="fill"></span><span>Выступает</span><span class="fill"></span></div>
<p class="q">1. Какой была наша стратегия <small>одной фразой</small></p>%s
<p class="q">2. Какое решение оказалось самым удачным и почему</p>%s
<p class="q">3. Какое решение мы бы изменили и почему</p>%s
<p class="q">4. Что мы сделаем иначе, если начать заново</p>%s
<p class="q">5. Сравните с листом стратегии: что совпало, а что нет</p>%s
""" % (lines(2), lines(3), lines(3), lines(3), lines(3)))


# ---------------------------------------------------------------- Обзоры рынка и аналитика
def news_page(year):
    items = ''.join('<div class="card"><b>%s</b><span>%s</span></div>' % n for n in T.NEWS[year])
    return """
<h1>Обзор рынка. Год %d</h1>
<p class="lead">Новости перед началом года. Прогноз объёма рынка по регионам — на табло.</p>
<div class="news">%s</div>
<div class="card soft" style="margin-top:6mm"><b>Аналитический обзор.</b> Точный прогноз на этот год по всем регионам можно купить за %d млрд сум. Скажите ведущему в первые две минуты и отметьте покупку в бланке решений.</div>
""" % (year, items, P['analytics'])


for y in (2, 3, 4):
    add('news%d' % y, 'Обзор рынка · год %d' % y, news_page(y))


def analytics_page(year):
    li = ''.join('<li>%s</li>' % x for x in T.ANALYTICS[year])
    one = """<div class="half"><div class="memo">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4mm"><span class="tag">Только для правления банка</span><span class="stamp">Оплачено: %d млрд сум</span></div>
<h2>Аналитический обзор. Год %d</h2><ul>%s</ul>
<p class="small">Обзор подготовлен для вашего банка. Передавать его другим банкам нельзя.</p></div></div>""" % (P['analytics'], year, li)
    return one + '<div class="cutline" style="margin-top:4mm;margin-bottom:4mm"></div>' + one


for y in (2, 3, 4):
    add('an%d' % y, 'Аналитический обзор · год %d · выдаёт ведущий' % y, analytics_page(y))

# ---------------------------------------------------------------- Личные выводы и анкета
pers = """<div class="pers"><h2 style="margin-top:0;font-size:15pt">Личный вывод</h2>
<p class="q">Где в моей работе мы растём быстрее, чем успеваем управлять</p>%s
<p class="q">Какое решение я приму иначе после этой игры</p>%s
<p class="q">Что я сделаю на этой неделе</p>%s</div>""" % (lines(3), lines(3), lines(2))
add('personal', 'Личный вывод · разрезать', pers + '<div class="cutline"></div>' + pers)

rate = ''.join('<tr><td>%s</td><td class="scale">1 2 3 4 5</td></tr>' % q for q in [
    'Игра была полезна для моей работы', 'Правила были понятны', 'Ведущий объяснял понятно и держал темп',
    'Разбор помог сделать выводы', 'Я знаю, что применю в работе'])
add('feedback', 'Анкета участника', """
<h1>Анкета участника</h1>
<p class="lead" style="margin-bottom:3mm">Две минуты. Анкета анонимная, подразделение указывать не обязательно.</p>
<h2 style="margin-top:2mm">Оцените игру <span class="small" style="font-weight:400">обведите цифру: 1 — совсем нет, 5 — полностью да</span></h2>
<table>%s
<tr><td>Насколько вероятно, что вы посоветуете игру коллеге</td><td class="scale" style="letter-spacing:0.08em">0 1 2 3 4 5 6 7 8 9 10</td></tr></table>
<p class="q">Что было самым полезным</p>%s
<p class="q">Что стоит изменить</p>%s
<p class="q">Одно решение из игры, которое я запомню</p>%s
<div class="fieldrow" style="margin-top:7mm"><span>Подразделение</span><span class="fill"></span></div>
""" % (rate, lines(3), lines(3), lines(2)))

# ---------------------------------------------------------------- Листы ведущего
yrs = ''.join('<th class="n">Год %d</th>' % y for y in G.YEARS)
pool_rows = ''.join('<tr><td><b>%s</b></td>%s</tr>' % (G.REGION_FULL[r], ''.join('<td class="n">%d</td>' % v for v in G.POOL[r])) for r in G.REGIONS)
add('key', 'Только ведущему · сценарий', """<div class="tight">
<h1>Сценарий игры</h1>
<p class="lead" style="margin-bottom:3mm">Что произойдёт в каждом году. Участникам этот лист не показывают до разбора.</p>
<table>
<tr><th style="width:15mm">Год</th><th>Что происходит</th><th style="width:52mm">Что было известно заранее</th><th style="width:44mm">Кого задевает</th></tr>
<tr><td><b>1</b></td><td>Спокойный год, событий нет.</td><td>Регулятор объявил о проверке в следующем году.</td><td>Никого</td></tr>
<tr><td><b>2</b></td><td>Проверка регулятора: штраф 20. Закон о льготах принят, рынок свободной зоны растёт в 2,5 раза.</td><td>О проверке — из новостей двух лет подряд. О законе — только из аналитического обзора.</td><td>Банки с риск-менеджментом 1-го уровня</td></tr>
<tr><td><b>3</b></td><td>Спад на Севере: рынок меньше на треть, каждый офис там несёт потери 24. Кибератака: ущерб 30.</td><td>В новостях — падение цен на металлы и атаки у соседей. Точно — в обзоре.</td><td>Банки с офисами на Севере. Банки с цифровыми каналами 1-го уровня</td></tr>
<tr><td><b>4</b></td><td>Засуха в Долине: рынок меньше на 30%%, каждый офис там несёт потери 20. Отток сотрудников: минус 10%% дохода.</td><td>В новостях — прогноз засухи с вероятностью 60%% и переманивание сотрудников. Точно — в обзоре.</td><td>Банки с офисами в Долине. Банки с командой 1-го уровня</td></tr>
</table>
<p class="small" style="margin-top:2mm">Потери от спада и засухи указаны для сбалансированной политики и риск-менеджмента 1-го уровня. Политика и уровень риск-менеджмента меняют их так же, как обычные кредитные потери.</p>
<h2>Слухи, которые не сбываются</h2>
<ul><li>Налог на сверхприбыль банков — новости перед годом 2.</li><li>Спад туризма на Юге из-за дорогих авиабилетов — перед годом 3.</li><li>Пересмотр льгот свободной зоны — перед годом 4.</li></ul>
<h2>Объём рынка на один банк, млрд сум</h2>
<table><tr><th>Регион</th>%s</tr>%s</table>
<h2>Что нельзя подсказывать</h2>
<p>Какие события произойдут, какие слухи ложные и куда пойдут конкуренты. На вопросы по правилам отвечайте всегда и всем командам одинаково.</p></div>
""" % (yrs, pool_rows))

add('cheat', 'Только ведущему · шпаргалка на год', """
<h1>Шпаргалка ведущего: один год</h1>
<p class="lead" style="margin-bottom:3mm">Каждый из четырёх лет проходит по одному кругу. Держите этот лист рядом с ноутбуком.</p>
<table>
<tr><th style="width:9mm">№</th><th style="width:38mm">Шаг</th><th>Что делаете</th><th style="width:20mm">Время</th></tr>
<tr><td><b>1</b></td><td><b>Обзор рынка</b></td><td>Покажите слайд с новостями года и раздайте печатный обзор, по одному на стол. Прочитайте заголовки вслух, не комментируя.</td><td>3 мин</td></tr>
<tr><td><b>2</b></td><td><b>Аналитика</b></td><td>Со 2-го года: спросите, кто покупает обзор. Выдайте карточку и проследите, чтобы покупку отметили в бланке.</td><td>1 мин</td></tr>
<tr><td><b>3</b></td><td><b>Решение</b></td><td>Запустите таймер. Обходите столы и заполняйте лист наблюдений. За три минуты до конца предупредите.</td><td>12 мин, в 1-й год 15</td></tr>
<tr><td><b>4</b></td><td><b>Бланки</b></td><td>Соберите бланки по сигналу таймера. Опоздавший банк работает с прошлогодним решением: без новых офисов и функций.</td><td>1 мин</td></tr>
<tr><td><b>5</b></td><td><b>Ввод</b></td><td>Лист «Год N» калькулятора: перенесите решения в жёлтые ячейки. В графе «Проверка» у всех должно стоять «ОК».</td><td>3–4 мин</td></tr>
<tr><td><b>6</b></td><td><b>Итоги</b></td><td>Откройте лист «Табло». Назовите прибыль каждого банка, покажите карту рынка и прогноз на следующий год. Причины пока не объясняйте.</td><td>4 мин</td></tr>
<tr><td><b>7</b></td><td><b>Журнал</b></td><td>Верните бланки. Попросите записать итоги года и одну строку «что нас удивило».</td><td>2 мин</td></tr>
</table>
<h2>Пока вы вводите решения</h2>
<p>Команды не должны сидеть без дела. Дайте им задание: «Запишите на обороте бланка, какой прибыли вы ждёте и почему». После четвёртого года в это время они готовят отчёт акционерам.</p>
<h2>Что отметить по годам</h2>
<table>
<tr><th style="width:15mm">Год</th><th>На что смотреть</th></tr>
<tr><td><b>1</b></td><td>Кто поднял риск-менеджмент после новости о проверке. Кто открыл больше трёх офисов и превысил норму управляемости.</td></tr>
<tr><td><b>2</b></td><td>Кто получил штраф. Кто купил аналитику и вошёл в свободную зону раньше других.</td></tr>
<tr><td><b>3</b></td><td>Кто остался на Севере с агрессивной политикой. Кто пострадал от кибератаки.</td></tr>
<tr><td><b>4</b></td><td>Кто закрыл офисы в Долине или сменил политику. Кто перешёл на агрессивную политику ради последнего года.</td></tr>
</table>
""")

obs_rows = ''.join('<tr><td>%s</td>%s</tr>' % (o, '<td></td>' * 6) for o in [
    'Опираются на лист стратегии, а не решают заново каждый год', 'Считают последствия до того, как решить',
    'Замечают сигналы в новостях и обсуждают их', 'Смотрят, что делают конкуренты',
    'Слышат несогласных, а не продавливают решение', 'Укладываются во время без спешки в конце',
    'Меняют курс, когда рынок меняется'])
add('observe', 'Только ведущему · лист наблюдений', """
<h1>Лист наблюдений</h1>
<p class="lead" style="margin-bottom:3mm">Обходите столы во время решений. Ставьте «+», если видели, и «−», если нет. В разборе приведите два-три наблюдения: что вы видели, без оценок.</p>
<table class="form obs"><tr><th style="width:74mm;text-align:left">Что делает правление</th><th>Банк 1</th><th>Банк 2</th><th>Банк 3</th><th>Банк 4</th><th>Банк 5</th><th>Банк 6</th></tr>%s</table>
<h2>Фразы и моменты для разбора</h2>
<p class="small">Записывайте дословно: кто что сказал, из-за чего спорили, какое решение приняли в последнюю минуту.</p>
%s
""" % (obs_rows, lines(12)))

# ---------------------------------------------------------------- Ведомость и сборка
SECTIONS = [
    ('dossier', 'Досье рынка', '2 на команду', 'На стол до начала игры'),
    ('rules', 'Правила игры', '2 на команду', 'На стол до начала игры'),
    ('roles', 'Карточки ролей', '1 на команду', 'Разрезать, на стол'),
    ('strategy', 'Стратегия банка', '1 на команду', 'На стол до начала игры'),
    ('forms', 'Бланки решений, годы 1–4', '1 комплект на команду', 'На стол. Сдаются ведущему каждый год'),
    ('report', 'Отчёт акционерам', '1 на команду', 'Раздать после 4-го года'),
    ('news2', 'Обзор рынка, год 2', '1 на команду', 'Раздать перед годом 2'),
    ('news3', 'Обзор рынка, год 3', '1 на команду', 'Раздать перед годом 3'),
    ('news4', 'Обзор рынка, год 4', '1 на команду', 'Раздать перед годом 4'),
    ('an2', 'Аналитический обзор, год 2', '1 лист на две команды', 'Разрезать. Выдаёт ведущий при покупке'),
    ('an3', 'Аналитический обзор, год 3', '1 лист на две команды', 'Разрезать. Выдаёт ведущий при покупке'),
    ('an4', 'Аналитический обзор, год 4', '1 лист на две команды', 'Разрезать. Выдаёт ведущий при покупке'),
    ('personal', 'Личный вывод', '1 лист на двух участников', 'Разрезать. Раздать в конце'),
    ('feedback', 'Анкета участника', '1 на участника', 'Раздать в конце'),
    ('key', 'Сценарий игры', '1', 'Ведущему'),
    ('cheat', 'Шпаргалка на год', '1', 'Ведущему'),
    ('observe', 'Лист наблюдений', '1', 'Ведущему'),
]


def manifest_rows():
    out, p = [], 2
    for sec, name, copies, where in SECTIONS:
        n = sum(1 for s, _, _ in pages if s == sec)
        rng = '%d–%d' % (p, p + n - 1) if n > 1 else '%d' % p
        out.append((rng, name, copies, where))
        p += n
    return out


def manifest_table():
    return '<table class="compact"><tr><th style="width:16mm">Стр.</th><th>Что</th><th style="width:44mm">Сколько копий</th><th style="width:62mm">Куда</th></tr>%s</table>' % ''.join(
        '<tr><td>%s</td><td><b>%s</b></td><td>%s</td><td>%s</td></tr>' % r for r in manifest_rows())


def build():
    cover = page('Раздаточные материалы · ведущему', """
<h1>Раздаточные материалы</h1>
<p class="lead">Бизнес-симуляция «Экспансия». Печать: A4, с одной стороны, подойдёт чёрно-белая. Эту страницу печатать не обязательно.</p>
<h2>Ведомость печати</h2>%s
<h2>Как собрать комплект</h2>
<ol>
<li>Напечатайте страницы в нужном количестве. Досье и правила — по два экземпляра на команду, чтобы их читали несколько человек сразу.</li>
<li>Соберите папку для каждой команды: досье, правила, карточки ролей, лист стратегии, четыре бланка решений.</li>
<li>Обзоры рынка, аналитические обзоры, отчёт акционерам, личные выводы и анкеты держите у себя и раздавайте по сценарию.</li>
</ol>
<p class="small">Пример. Четыре команды, двадцать участников — около 110 листов.</p>
""" % manifest_table(), pageno='1')
    body = cover
    order = [s for s, _, _, _ in SECTIONS]
    k = 2
    for sec in order:
        for s, label, html in pages:
            if s == sec:
                body += page(label, html, pageno=str(k))
                k += 1
    to_pdf(html_doc('Экспансия — раздаточные материалы', CSS + PAGE_CSS + EXTRA, body), OUT, name='handouts')
    print('раздаточные: %d стр. -> %s' % (k - 1, os.path.abspath(OUT)))


if __name__ == '__main__':
    build()
