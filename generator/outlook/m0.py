# -*- coding: utf-8 -*-
"""Intro: cover, how to take the course, what you get, programme (fan -> grid morph)."""
from kit import *

TIMES = ["≈ 6 мин", "≈ 9 мин", "≈ 7 мин", "≈ 9 мин", "≈ 5 мин", "≈ 5 мин"]
PROGRAM = [(n, t, d) for n, t, d in MODULES] + [("06", "Итоговый тест", "Шпаргалка и 5 вопросов")]
OPENERS = ["m1-open", "m2-open", "m3-open", "m4-open", "m5-open", "fin-cheat"]


def build(k):
    k.mod = None
    # ------------------------------------------------------------------ cover
    s = k.slide("cover", title=COURSE, glow="hero", nav=False, crumb=False, logo=False, show_title=False, trans="fade",
                notes="Здравствуйте! Это курс «Outlook: почта и календарь». За полчаса вы разберётесь, как устроена программа, "
                      "как писать понятные письма, держать почту в порядке и назначать встречи. Нажмите «Начать курс».")
    s.pic(A("logo") + ".png", MX, 0.55, w=1.75, name="!!logo")
    s.pic(obj("i_calendar"), 10.35, 0.5, h=2.5, name="!!hero-cal", rot=8, anim=500)
    s.pic(obj("i_envelope"), 6.75, 1.95, w=5.6, name="!!hero-env", anim=250)
    s.pic(obj("i_bell"), 6.55, 4.85, h=1.75, name="!!hero-bell", rot=-10, anim=650)
    pill(s, MX, 2.05, "Электронный курс", sz=13, h=0.44, name="cover-pill", dot=True, anim=0)
    s.shape(MX, 2.7, 6.6, 1.75, text=[{"t": "Outlook:"}, {"t": "почта и календарь"}], sz=46, color=WHITE, font=FONT, lnsp=0.9,
            inset=(0, 0, 0, 0), ph="title", name="!!title", anim=100)
    s.text(MX, 4.55, 5.9, 0.75, "Всё, что нужно для ежедневной работы, — просто и по шагам", sz=17, color=TEXT, font=FONT_L, lnsp=1.0,
           name="cover-sub", anim=200)
    button(s, MX, 5.6, 2.7, 0.64, "Начать курс", link="next", name="cover-btn", sz=16, anim=350)
    s.text(MX + 3.0, 5.6, 3.6, 0.64, "5 модулей  ·  ≈ 40 минут  ·  тест", sz=13, color=MUTED, anchor="ctr", name="cover-meta", anim=450)

    # ------------------------------------------------------------------ how to take the course
    s = k.slide("howto", title="Как проходить курс", sub="Четыре простых правила — и можно начинать", glow="a",
                notes="Листайте слайды кнопками в правом нижнем углу или стрелками на клавиатуре. В конце каждого модуля будет короткая "
                      "проверка: нажмите на вариант ответа и увидите разбор. Проходите курс в удобном темпе, а лучше всего — откройте "
                      "Outlook рядом и сразу повторяйте каждое действие.")
    items = [
        dict(icon="mouse-pointer-click", title="Листайте слайды", body="Кнопки «Назад» и «Далее» — в правом нижнем углу. Работают и стрелки на клавиатуре."),
        dict(icon="list-checks", title="Отвечайте на вопросы", body="В конце каждого модуля — короткая проверка. Нажмите на вариант и увидите разбор."),
        dict(icon="timer", title="Идите в своём темпе", body="Курс занимает около 40 минут. К любому слайду можно вернуться."),
        dict(icon="monitor", title="Повторяйте в Outlook", body="Откройте Outlook рядом и пробуйте каждое действие сразу — так запоминается лучше."),
    ]
    h, used = grid(s, items, y=2.25, cols=4, gap=0.26)
    note(s, MX, 2.25 + used + 0.3, CW,
         "В курсе показан классический Outlook для Windows на русском языке. В новой и в веб-версии кнопки называются так же, но могут выглядеть немного иначе.",
         icon="info", anim=650)

    # ------------------------------------------------------------------ what you get
    s = k.slide("why", title="Что вы будете уметь после курса", sub="Outlook — главный рабочий инструмент: в нём договариваются, согласовывают и планируют",
                glow="b", title_w=9.6,
                notes="После курса вы будете писать письма, которые понимают с первого раза, находить любое письмо за секунды, "
                      "назначать встречи без долгой переписки и распознавать опасные письма.")
    items = [
        dict(img=obj("i_envelope"), title="Писать понятные письма", body="Тема, адресаты и текст — так, чтобы вам ответили быстро и по делу."),
        dict(img=obj("i_search"), title="Находить письма за секунды", body="Поиск, папки, категории и правила вместо бесконечной прокрутки."),
        dict(img=obj("i_calendar"), title="Назначать встречи", body="Свободное время коллег видно сразу — без переписки «а когда вам удобно?»."),
        dict(img=obj("i_shield"), title="Защищать данные банка", body="Узнаёте опасное письмо по признакам и знаете, что с ним делать."),
    ]
    grid(s, items, y=2.35, cols=4, gap=0.26, img_h=1.15, tsz=17)

    # ------------------------------------------------------------------ programme: fan of cards -> grid (morph)
    program(k, "program-a", fan=True)
    program(k, "program-b", fan=False)


def program(k, key, fan):
    s = k.slide(key, title="Программа курса", sub="Пять модулей и итоговый тест. Нажмите на карточку, чтобы перейти к модулю",
                glow="hero2", center=True, title_y=0.82, dur=1250,
                notes="В курсе пять модулей и итоговый тест. Сначала познакомимся с окном Outlook, затем научимся писать письма, "
                      "наводить порядок в почте, работать с календарём и защищаться от опасных писем." if fan else
                      "Каждая карточка — отдельный модуль. Нажмите на карточку, чтобы перейти к модулю, или просто листайте дальше.")
    # big glowing panel under the cards (rounded picture, like on the reference 'Products' slides)
    s.pic("glow1.jpg", 0.72, 2.42, 11.9, 6.2, geom="roundRect", radius=0.9, name="!!prog-panel", rot=180)
    s.rrect(0.72, 2.42, 11.9, 6.2, r=0.9, fill=None, line="glass", name="!!prog-panel-line")
    cw, ch = 3.55, 1.92
    for i, (num, title, desc) in enumerate(PROGRAM):
        if fan:
            x = SW / 2 - cw / 2 + (i - 2.5) * 0.5
            y = 3.25 + abs(i - 2.5) * 0.12
            rot = (i - 2.5) * 9
        else:
            r, c = divmod(i, 3)
            x = 1.06 + c * (cw + 0.28)
            y = 2.78 + r * (ch + 0.26)
            rot = 0
        s.begin("!!prog-card-%d" % i)
        s.rrect(x, y, cw, ch, r=0.26, fill="glass", line="glass", link=("slide", OPENERS[i]), tip=title)
        s.oval(x + 0.3, y + 0.34, 0.09, 0.09, fill=A("ACC"))
        s.text(x + 0.48, y + 0.22, 1.8, 0.32, ("Модуль %s" % num) if i < 5 else "Финал", sz=11.5, color=TEXT, anchor="ctr")
        s.text(x + cw - 1.3, y + 0.22, 1.02, 0.32, TIMES[i], sz=11, color=MUTED, anchor="ctr", align="r")
        s.text(x + 0.3, y + 0.62, cw - 0.6, 0.42, title, sz=17, color=WHITE, font=FONT_SB, anchor="ctr")
        s.line(x + 0.3, y + 1.12, x + cw - 0.3, y + 1.12, color=(WHITE, 22))
        s.text(x + 0.3, y + 1.24, cw - 0.6, 0.5, desc, sz=13, color=TEXT, lnsp=1.0)
        s.end(rot=rot)
    return s
