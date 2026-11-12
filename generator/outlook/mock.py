# -*- coding: utf-8 -*-
"""Schematic Outlook windows drawn with native shapes (dark glass style).
Each mock returns a dict of zones {name: (x, y, w, h)} in slide inches - used for the moving highlight."""
from kit import *

WIN = "0B0A10"       # window body
BAR = "14121C"       # title bar / ribbon
PANE = "0F0E16"
FIELD = "17151F"
LN = (WHITE, 13)
TXT = "CFC7D4"
DIM = "8F8799"


class M:
    """Drawing surface with its own origin and scale."""

    def __init__(self, s, x, y, k=1.0):
        self.s, self.x, self.y, self.k = s, x, y, k

    def X(self, v):
        return self.x + v * self.k

    def Y(self, v):
        return self.y + v * self.k

    def r(self, x, y, w, h, fill=None, line=None, r=0.05, **kw):
        return self.s.rrect(self.X(x), self.Y(y), w * self.k, h * self.k, r=r * self.k, fill=fill, line=line, **kw)

    def box(self, x, y, w, h, fill=None, line=None, **kw):
        return self.s.rect(self.X(x), self.Y(y), w * self.k, h * self.k, fill=fill, line=line, **kw)

    def o(self, x, y, d, fill=None, line=None, **kw):
        return self.s.oval(self.X(x), self.Y(y), d * self.k, d * self.k, fill=fill, line=line, **kw)

    def t(self, x, y, w, h, text, sz=8.5, color=TXT, **kw):
        kw.setdefault("anchor", "ctr")
        kw.setdefault("check", False)
        return self.s.text(self.X(x), self.Y(y), w * self.k, h * self.k, text, sz=round(sz * self.k * 2) / 2.0, color=color, lnsp=0.98, **kw)

    def i(self, icon, x, y, w, white=True, alpha=None, file=None):
        return self.s.pic(file or ic(icon, white=white), self.X(x), self.Y(y), w=w * self.k, alpha=alpha)

    def ln(self, x1, y1, x2, y2, color=LN, lw=0.75, **kw):
        return self.s.line(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), color=color, lw=lw, **kw)

    def zone(self, x, y, w, h):
        return (self.X(x), self.Y(y), w * self.k, h * self.k)


def _frame(m, W, H, title, tabs, active=1):
    m.r(0, 0, W, H, fill=WIN, line="glass", r=0.16, fx="shadow")
    m.s.shape(m.X(0), m.Y(0), W * m.k, 0.62 * m.k, geom="round2SameRect", radius=0.16 * m.k, fill=BAR)
    for j, c in enumerate(("FF5F57", "FEBC2E", "28C840")):
        m.o(0.16 + j * 0.17, 0.115, 0.1, fill=(c, 75))
    m.t(1.0, 0.03, W - 2.0, 0.28, title, sz=8.5, color=DIM, align="ctr")
    x = 0.2
    for j, tb in enumerate(tabs):
        w = text_width(tb, 8.5, FONT) + 0.26
        if j == active:
            m.t(x, 0.33, w, 0.27, tb, sz=8.5, color=WHITE, font=FONT_SB, align="ctr")
            m.r(x + 0.06, 0.585, w - 0.12, 0.03, fill=A("ACC"), r=0.015)
        else:
            m.t(x, 0.33, w, 0.27, tb, sz=8.5, color=DIM, align="ctr")
        x += w + 0.04


def _rbtn(m, x, y, icon, label, w=0.74, accent=False, big=True, lines=None):
    """Ribbon button: icon over a (two-line) label."""
    if accent:
        m.r(x + 0.03, y + 0.04, w - 0.06, 0.7, fill=(A("ACC"), 16), line=(A("ACC"), 55), r=0.07)
    isz = 0.27
    m.i(icon, x + (w - isz) / 2, y + 0.1, isz, white=not accent)
    m.t(x - 0.06, y + 0.4, w + 0.12, 0.32, label, sz=7, color=WHITE if accent else TXT, align="ctr", anchor="t")
    return x + w


def _sep(m, x, y):
    m.ln(x, y + 0.08, x, y + 0.7)


# ====================================================================== main mail window
MAILS = [
    ("Азиз Каримов", "Отчёт за октябрь", "Добрый день! Направляю отчёт за…", "10:42", True, True),
    ("Дилноза Рахимова", "Согласование договора", "Коллеги, прошу согласовать до…", "09:15", True, False),
    ("Отдел кадров", "График отпусков на 2027 год", "Уважаемые коллеги, до 20 ноября…", "Вт", False, False),
    ("Тимур Юсупов", "Приглашение: планёрка", "Когда: понедельник, 10:00–10:30", "Пн", False, False),
    ("Служба поддержки", "Заявка № 1024 выполнена", "Ваша заявка закрыта. Если вопрос…", "Пт", False, False),
]
FOLDERS = [("inbox", "Входящие", "3"), ("pen-line", "Черновики", ""), ("send", "Отправленные", ""), ("trash-2", "Удаленные", ""),
           ("archive", "Архив", ""), ("ban", "Нежелательная почта", "")]

MAIL_W, MAIL_H = 8.3, 4.72


def mail_window(s, x, y, k=1.0, name="!!mock-mail", badges=None, active_badge=None):
    """Classic Outlook main window. badges: list of zone names to mark with numbers 1..n."""
    W, H = MAIL_W, MAIL_H
    m = M(s, x, y, k)
    s.begin(name)
    _frame(m, W, H, "Входящие — Outlook", ["Файл", "Главная", "Отправка и получение", "Папка", "Вид", "Справка"])
    # ---- ribbon
    ry = 0.62
    m.box(0.012, ry, W - 0.024, 0.8, fill=BAR)
    m.ln(0.012, ry + 0.8, W - 0.012, ry + 0.8)
    cx = 0.14
    cx = _rbtn(m, cx, ry, "mail-plus", "Создать\nсообщение", w=0.86, accent=True)
    _sep(m, cx + 0.07, ry); cx += 0.14
    cx = _rbtn(m, cx, ry, "trash-2", "Удалить", w=0.66)
    cx = _rbtn(m, cx, ry, "archive", "Архивиро-\nвать", w=0.7)
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_reply = cx
    cx = _rbtn(m, cx, ry, "reply", "Ответить", w=0.7)
    cx = _rbtn(m, cx, ry, "reply-all", "Ответить\nвсем", w=0.7)
    cx = _rbtn(m, cx, ry, "forward", "Переслать", w=0.72)
    x_reply2 = cx
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_tools = cx
    cx = _rbtn(m, cx, ry, "folder-open", "Переместить", w=0.82)
    cx = _rbtn(m, cx, ry, "list-filter", "Правила", w=0.66)
    cx = _rbtn(m, cx, ry, "tag", "Категории", w=0.72)
    cx = _rbtn(m, cx, ry, "flag", "К исполне-\nнию", w=0.72)
    x_tools2 = cx
    # ---- folder pane
    by = 1.43
    fw = 1.78
    m.box(0.012, by, fw, H - by - 0.02, fill=PANE)
    m.ln(fw + 0.012, by, fw + 0.012, H - 0.03)
    m.t(0.16, by + 0.08, 1.5, 0.24, "Избранное", sz=7.5, color=DIM)
    fy = by + 0.36
    for j, (icn, nm, cnt) in enumerate(FOLDERS):
        if j == 0:
            m.r(0.08, fy - 0.01, fw - 0.14, 0.28, fill=(A("ACC"), 18), r=0.06)
        m.i(icn, 0.16, fy + 0.055, 0.16, white=True, alpha=100 if j == 0 else 60)
        m.t(0.4, fy, 1.2, 0.27, nm, sz=8, color=WHITE if j == 0 else TXT, font=FONT_SB if j == 0 else FONT)
        if cnt:
            m.t(fw - 0.42, fy, 0.3, 0.27, cnt, sz=8, color=A("ACC_SOFT"), font=FONT_SB, align="r")
        fy += 0.31
    # ---- section switcher (bottom-left)
    ny = H - 0.5
    m.ln(0.012, ny, fw + 0.012, ny)
    for j, icn in enumerate(("mail", "calendar-days", "users", "clipboard-check")):
        if j == 0:
            m.r(0.13 + j * 0.42 - 0.05, ny + 0.09, 0.32, 0.32, fill=(A("ACC"), 20), r=0.07)
        m.i(icn, 0.13 + j * 0.42, ny + 0.14, 0.22, white=(j != 0), alpha=None if j == 0 else 70)
    # ---- message list
    lx = fw + 0.012
    lw = 2.78
    m.ln(lx + lw, by, lx + lw, H - 0.03)
    m.r(lx + 0.1, by + 0.09, lw - 0.2, 0.27, fill=FIELD, line=LN, r=0.06)
    m.i("search", lx + 0.17, by + 0.145, 0.16, alpha=60)
    m.t(lx + 0.4, by + 0.09, lw - 0.6, 0.27, "Поиск в текущем почтовом ящике", sz=7.5, color=DIM)
    m.t(lx + 0.12, by + 0.42, 0.5, 0.22, "Все", sz=7.5, color=WHITE, font=FONT_SB)
    m.t(lx + 0.5, by + 0.42, 1.2, 0.22, "Непрочитанные", sz=7.5, color=DIM)
    m.t(lx + lw - 1.0, by + 0.42, 0.9, 0.22, "По дате ↓", sz=7.5, color=DIM, align="r")
    my = by + 0.68
    mh = 0.5
    for j, (snd, subj, prev, tm, unread, att) in enumerate(MAILS):
        if j == 0:
            m.box(lx + 0.01, my, lw - 0.02, mh, fill=(A("ACC"), 12))
        if unread:
            m.r(lx + 0.05, my + 0.07, 0.035, mh - 0.14, fill=A("ACC"), r=0.015)
        m.t(lx + 0.16, my + 0.03, lw - 0.9, 0.17, snd, sz=8, color=WHITE if unread else TXT, font=FONT_SB if unread else FONT)
        m.t(lx + lw - 0.6, my + 0.03, 0.5, 0.17, tm, sz=7, color=A("ACC_SOFT") if unread else DIM, align="r")
        m.t(lx + 0.16, my + 0.185, lw - 0.6, 0.16, subj, sz=7.5, color=A("ACC_SOFT") if unread else TXT, font=FONT_SB if unread else FONT)
        m.t(lx + 0.16, my + 0.325, lw - 0.3, 0.15, prev, sz=7, color=DIM)
        if att:
            m.i("paperclip", lx + lw - 0.3, my + 0.2, 0.13, alpha=70)
        m.ln(lx + 0.1, my + mh, lx + lw - 0.1, my + mh, color=(WHITE, 7))
        my += mh
    # ---- reading pane
    px = lx + lw
    pw = W - px - 0.012
    m.t(px + 0.2, by + 0.1, pw - 0.4, 0.3, "Отчёт за октябрь", sz=11.5, color=WHITE, font=FONT_SB)
    m.o(px + 0.2, by + 0.5, 0.36, fill=(A("ACC2"), 55))
    m.t(px + 0.2, by + 0.5, 0.36, 0.36, "АК", sz=7.5, color=WHITE, font=FONT_SB, align="ctr")
    m.t(px + 0.66, by + 0.47, 1.9, 0.2, "Азиз Каримов", sz=8.5, color=WHITE, font=FONT_SB)
    m.t(px + 0.66, by + 0.66, 2.2, 0.2, "Кому: Отдел продаж", sz=7.5, color=DIM)
    for j, icn in enumerate(("reply", "reply-all", "forward")):
        m.r(px + pw - 1.06 + j * 0.31, by + 0.52, 0.26, 0.26, fill=(WHITE, 6), line=LN, r=0.06)
        m.i(icn, px + pw - 1.06 + j * 0.31 + 0.05, by + 0.57, 0.16, alpha=80)
    m.ln(px + 0.2, by + 0.98, px + pw - 0.2, by + 0.98)
    m.t(px + 0.2, by + 1.06, pw - 0.4, 1.02,
        [{"t": "Добрый день, коллеги!", "spcAft": 3}, {"t": "Направляю отчёт за октябрь. Прошу посмотреть и прислать замечания до пятницы.", "spcAft": 3},
         {"t": "С уважением,"}, {"t": "Азиз Каримов"}], sz=8, color=TXT, anchor="t")
    m.r(px + 0.2, by + 2.2, 1.55, 0.36, fill=FIELD, line=LN, r=0.07)
    m.i("file-text", px + 0.28, by + 2.28, 0.2, white=False)
    m.t(px + 0.55, by + 2.2, 1.15, 0.36, "Отчёт_октябрь.xlsx", sz=7.5, color=TXT)
    z = {
        "ribbon": m.zone(0.06, 0.33, W - 0.12, 1.07),
        "new": m.zone(0.14, ry + 0.02, 0.86, 0.76),
        "reply": m.zone(x_reply - 0.02, ry + 0.02, x_reply2 - x_reply + 0.04, 0.76),
        "tools": m.zone(x_tools - 0.02, ry + 0.02, x_tools2 - x_tools + 0.04, 0.76),
        "folders": m.zone(0.06, by + 0.04, fw - 0.08, ny - by - 0.08),
        "nav": m.zone(0.06, ny + 0.04, fw - 0.08, 0.42),
        "search": m.zone(lx + 0.06, by + 0.05, lw - 0.12, 0.35),
        "list": m.zone(lx + 0.05, by + 0.04, lw - 0.1, H - by - 0.1),
        "reading": m.zone(px + 0.05, by + 0.04, pw - 0.1, H - by - 0.1),
        "attach": m.zone(px + 0.16, by + 2.16, 1.63, 0.44),
        "first": m.zone(lx + 0.04, by + 0.66, lw - 0.08, mh + 0.02),
        "win": m.zone(0, 0, W, H),
    }
    s.end()
    if badges:
        pos = {"ribbon": (W - 0.52, 0.84), "folders": (1.3, by + 0.02), "list": (lx + lw - 0.44, by + 1.78), "reading": (px + pw - 0.5, by + 1.25),
               "nav": (1.42, ny + 0.1)}
        for j, zn in enumerate(badges):
            bx, byy = pos[zn]
            badge(s, m.X(bx), m.Y(byy), j + 1, active=(active_badge == zn), name="!!badge-%s" % zn, d=0.36 * k)
    return z


def badge(s, x, y, n, active=False, name=None, d=0.36):
    s.oval(x, y, d, d, fill="accent" if active else ("26222E", 96), line=None if active else "glass", text=str(n), sz=12 * d / 0.36,
           color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0, 0, 0, 0.01), name=name, fx="glow_s" if active else None)


def highlight(s, zone, name="!!hl", pad=0.05, color=None):
    """Moving frame: a soft wide halo line + a crisp line (no effects, so every renderer shows it the same way)."""
    x, y, w, h = zone
    c = color or A("ACC")
    s.rrect(x - pad - 0.03, y - pad - 0.03, w + 2 * pad + 0.06, h + 2 * pad + 0.06, r=0.14, fill=None, line=(c, 28), lw=6, name=name + "-halo")
    return s.rrect(x - pad, y - pad, w + 2 * pad, h + 2 * pad, r=0.12, fill=(c, 8), line=c, lw=1.75, name=name)


# ====================================================================== new message window
COMPOSE_W, COMPOSE_H = 6.9, 4.72


def compose_window(s, x, y, k=1.0, name="!!mock-compose", fill=7, cc=True, attach=True, bcc=False, subject="Отчёт за октябрь — прошу согласовать до 13.11"):
    """New message. fill = how many steps are already filled: 1 To, 2 Cc, 3 Subject, 4 Body, 5 Attachment."""
    W, H = COMPOSE_W, COMPOSE_H
    m = M(s, x, y, k)
    s.begin(name)
    _frame(m, W, H, "%s — Сообщение" % (subject.split(" —")[0] if fill >= 3 else "Без имени"),
           ["Файл", "Сообщение", "Вставка", "Параметры", "Формат текста", "Рецензирование"])
    ry = 0.62
    m.box(0.012, ry, W - 0.024, 0.8, fill=BAR)
    m.ln(0.012, ry + 0.8, W - 0.012, ry + 0.8)
    cx = 0.14
    cx = _rbtn(m, cx, ry, "clipboard-list", "Вставить", w=0.66)
    _sep(m, cx + 0.07, ry); cx += 0.14
    for j, (ch, st) in enumerate((("Ж", True), ("К", False), ("Ч", False))):
        m.r(cx + j * 0.3, ry + 0.14, 0.26, 0.26, fill=(WHITE, 6), line=LN, r=0.05)
        m.t(cx + j * 0.3, ry + 0.14, 0.26, 0.26, ch, sz=8.5, color=WHITE, font=FONT_SB if st else FONT, align="ctr")
    m.t(cx - 0.05, ry + 0.46, 1.0, 0.2, "Шрифт", sz=7, color=DIM, align="ctr")
    cx += 0.98
    _sep(m, cx + 0.02, ry); cx += 0.1
    cx = _rbtn(m, cx, ry, "contact", "Адресная\nкнига", w=0.72)
    cx = _rbtn(m, cx, ry, "user-check", "Проверить\nимена", w=0.74)
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_att = cx
    cx = _rbtn(m, cx, ry, "paperclip", "Вложить\nфайл", w=0.7, accent=(fill == 5))
    x_sig = cx
    cx = _rbtn(m, cx, ry, "signature", "Подпись", w=0.68)
    _sep(m, cx + 0.07, ry); cx += 0.14
    cx = _rbtn(m, cx, ry, "circle-alert", "Высокая\nважность", w=0.74)
    # ---- header fields
    by = 1.5
    m.r(0.16, by, 0.8, 1.02, fill=(A("ACC"), 16) if fill < 6 else "accent", line=(A("ACC"), 55), r=0.08)
    m.i("send", 0.16 + 0.27, by + 0.2, 0.26, white=(fill >= 6))
    m.t(0.16, by + 0.56, 0.8, 0.3, "Отправить", sz=8, color=WHITE, font=FONT_SB, align="ctr")
    rows = [("Кому…", "Азиз Каримов;  Дилноза Рахимова" if fill >= 1 else ""),
            ("Копия…", "Тимур Юсупов" if (fill >= 2 and cc) else ""),
            ("Тема", subject if fill >= 3 else "")]
    if bcc:
        rows.insert(2, ("СК…", ""))
    fx0 = 1.08
    rh = 0.34 if not bcc else 0.255
    fy = by
    zrow = {}
    for j, (lab, val) in enumerate(rows):
        btn = lab.endswith("…")
        if btn:
            m.r(fx0, fy + 0.03, 0.66, rh - 0.07, fill=(WHITE, 6), line=LN, r=0.05)
        m.t(fx0, fy + 0.03, 0.66, rh - 0.07, lab, sz=8, color=TXT, align="ctr")
        m.r(fx0 + 0.74, fy + 0.03, W - fx0 - 0.74 - 0.16, rh - 0.07, fill=FIELD, line=LN, r=0.05)
        if val:
            m.t(fx0 + 0.84, fy + 0.03, W - fx0 - 1.1, rh - 0.07, val, sz=8, color=WHITE)
        zrow[lab] = m.zone(fx0 - 0.03, fy, W - fx0 - 0.1, rh)
        fy += rh
    ay = by + 1.08
    has_att = attach and fill >= 5
    if has_att:
        m.t(fx0, ay, 0.7, 0.3, "Вложено", sz=8, color=TXT, align="ctr")
        m.r(fx0 + 0.74, ay, 1.7, 0.3, fill=FIELD, line=LN, r=0.06)
        m.i("file-text", fx0 + 0.81, ay + 0.055, 0.19, white=False)
        m.t(fx0 + 1.06, ay, 1.36, 0.3, "Отчёт_октябрь.xlsx", sz=7.5, color=TXT)
    # ---- body
    ty = by + 1.5
    m.r(0.16, ty, W - 0.32, H - ty - 0.16, fill=FIELD, line=LN, r=0.07)
    if fill >= 4:
        m.t(0.32, ty + 0.1, W - 0.64, 1.05,
            [{"t": "Добрый день, коллеги!", "spcAft": 3},
             {"t": "Направляю отчёт за октябрь. Прошу посмотреть и прислать замечания до пятницы, 13 ноября.", "spcAft": 3}],
            sz=8.5, color=TXT, anchor="t")
        m.t(0.32, ty + 0.92, W - 0.64, 0.66,
            [{"t": "С уважением,"}, {"t": "Нигора Алиева"}, {"t": "Главный специалист · Отдел продаж", "color": DIM}], sz=8, color=TXT, anchor="t")
    else:
        m.box(0.32, ty + 0.14, 0.012, 0.2, fill=A("ACC"))
    z = {
        "send": m.zone(0.13, by - 0.03, 0.86, 1.08),
        "to": zrow["Кому…"], "cc": zrow["Копия…"], "subject": zrow["Тема"],
        "bcc": zrow.get("СК…"),
        "attach_btn": m.zone(x_att, ry + 0.02, 0.7, 0.76),
        "sig_btn": m.zone(x_sig, ry + 0.02, 0.68, 0.76),
        "attach": m.zone(fx0 - 0.03, ay - 0.04, 2.6, 0.38),
        "body": m.zone(0.13, ty - 0.03, W - 0.26, H - ty - 0.1),
        "text": m.zone(0.24, ty + 0.05, W - 0.48, 0.7),
        "sig": m.zone(0.24, ty + 0.9, 3.2, 0.66),
        "win": m.zone(0, 0, W, H),
    }
    s.end()
    return z


# ====================================================================== calendar window
CAL_W, CAL_H = 8.3, 4.72
DAYS = [("Пн", "9"), ("Вт", "10"), ("Ср", "11"), ("Чт", "12"), ("Пт", "13")]
EVENTS = [   # day, start hour, duration h, title, kind
    (0, 9.5, 0.5, "Планёрка", "acc"),
    (0, 14.0, 1.0, "Встреча с клиентом", "vio"),
    (1, 11.0, 1.0, "Обучение: Outlook", "acc"),
    (2, 10.0, 0.5, "Созвон с филиалом", "vio"),
    (2, 15.0, 1.5, "Подготовка отчёта", "dim"),
    (3, 9.5, 0.5, "Планёрка", "acc"),
    (4, 13.0, 1.0, "Обед с командой", "dim"),
]


def calendar_window(s, x, y, k=1.0, name="!!mock-cal", view=1, new_event=None):
    """Calendar: work-week view. new_event = (day, start, dur, title) drawn as a fresh accent block."""
    W, H = CAL_W, CAL_H
    m = M(s, x, y, k)
    s.begin(name)
    _frame(m, W, H, "Календарь — Outlook", ["Файл", "Главная", "Отправка и получение", "Папка", "Вид", "Справка"])
    ry = 0.62
    m.box(0.012, ry, W - 0.024, 0.8, fill=BAR)
    m.ln(0.012, ry + 0.8, W - 0.012, ry + 0.8)
    cx = 0.14
    x_new = cx
    cx = _rbtn(m, cx, ry, "calendar-plus", "Создать\nвстречу", w=0.76, accent=True)
    cx = _rbtn(m, cx, ry, "users", "Создать\nсобрание", w=0.78, accent=True)
    x_new2 = cx
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_today = cx
    cx = _rbtn(m, cx, ry, "calendar-check", "Сегодня", w=0.68)
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_view = cx
    for j, (icn, lab) in enumerate((("calendar", "День"), ("calendar-range", "Рабочая\nнеделя"), ("calendar-days", "Неделя"), ("grid-2x2", "Месяц"))):
        if j == view:
            m.r(cx + 0.03, ry + 0.04, 0.68, 0.7, fill=(WHITE, 9), line=LN, r=0.07)
        cx = _rbtn(m, cx, ry, icn, lab, w=0.74)
    x_view2 = cx
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_share = cx
    cx = _rbtn(m, cx, ry, "folder-open", "Открыть\nкалендарь", w=0.8)
    cx = _rbtn(m, cx, ry, "share-2", "Общий\nдоступ", w=0.7)
    x_share2 = cx
    # ---- left pane: mini month + calendars
    by = 1.43
    fw = 1.78
    m.box(0.012, by, fw, H - by - 0.02, fill=PANE)
    m.ln(fw + 0.012, by, fw + 0.012, H - 0.03)
    m.t(0.16, by + 0.06, 1.5, 0.24, "Ноябрь 2026", sz=8, color=WHITE, font=FONT_SB)
    cw = (fw - 0.26) / 7
    for j, dn in enumerate("ПВСЧПСВ"):
        m.t(0.13 + j * cw, by + 0.32, cw, 0.17, dn, sz=6.5, color=DIM, align="ctr")
    import datetime
    start = datetime.date(2026, 10, 26)          # Monday; the grid shows 6 weeks
    for r in range(6):
        for c in range(7):
            dt = start + datetime.timedelta(days=r * 7 + c)
            in_month = dt.month == 11
            cur_week = (r == 2 and c < 5)
            if cur_week:
                m.r(0.13 + c * cw + 0.01, by + 0.5 + r * 0.18 + 0.01, cw - 0.02, 0.16, fill=(A("ACC"), 22 if c else 60), r=0.04)
            m.t(0.13 + c * cw, by + 0.5 + r * 0.18, cw, 0.18, str(dt.day), sz=6.5, color=(WHITE if cur_week else TXT) if in_month else "5A5363", align="ctr")
    cy = by + 1.68
    m.t(0.16, cy, 1.5, 0.22, "Мои календари", sz=7.5, color=DIM)
    m.r(0.18, cy + 0.28, 0.15, 0.15, fill=A("ACC"), r=0.03)
    m.t(0.42, cy + 0.24, 1.3, 0.23, "Календарь", sz=8, color=WHITE)
    m.t(0.16, cy + 0.54, 1.5, 0.22, "Общие календари", sz=7.5, color=DIM)
    m.r(0.18, cy + 0.82, 0.15, 0.15, fill=None, line=LN, r=0.03)
    m.t(0.42, cy + 0.78, 1.3, 0.23, "Отдел продаж", sz=8, color=TXT)
    ny = H - 0.5
    m.ln(0.012, ny, fw + 0.012, ny)
    for j, icn in enumerate(("mail", "calendar-days", "users", "clipboard-check")):
        if j == 1:
            m.r(0.13 + j * 0.42 - 0.05, ny + 0.09, 0.32, 0.32, fill=(A("ACC"), 20), r=0.07)
        m.i(icn, 0.13 + j * 0.42, ny + 0.14, 0.22, white=(j != 1), alpha=None if j == 1 else 70)
    # ---- week grid
    gx = fw + 0.012
    gw = W - gx - 0.012
    tw = 0.48
    dw = (gw - tw - 0.06) / 5
    m.t(gx + 0.12, by + 0.05, 3.0, 0.26, "9–13 ноября 2026", sz=9.5, color=WHITE, font=FONT_SB)
    hy = by + 0.36
    for j, (dn, dd) in enumerate(DAYS):
        m.t(gx + tw + j * dw + 0.06, hy, dw - 0.1, 0.26, "%s  %s" % (dd, dn), sz=8, color=WHITE if j == 0 else TXT, font=FONT_SB if j == 0 else FONT)
        m.ln(gx + tw + j * dw, hy, gx + tw + j * dw, H - 0.03, color=(WHITE, 8))
    m.ln(gx, hy + 0.28, W - 0.012, hy + 0.28)
    g0 = hy + 0.3
    hh = (H - g0 - 0.04) / 9.0      # 9:00 .. 18:00
    for hr in range(9):
        m.t(gx, g0 + hr * hh - 0.02, tw - 0.06, 0.2, "%d:00" % (9 + hr), sz=6.5, color=DIM, align="r", anchor="t")
        if hr:
            m.ln(gx + tw, g0 + hr * hh, W - 0.012, g0 + hr * hh, color=(WHITE, 7))
    cols = {"acc": ((A("ACC"), 30), A("ACC")), "vio": ((A("ACC2"), 34), A("ACC2")), "dim": ((WHITE, 9), "7A7286")}
    ev = list(EVENTS)
    zone_new = None
    for d_, st, du, ttl, kind in ev:
        ex, ey = gx + tw + d_ * dw + 0.03, g0 + (st - 9) * hh + 0.015
        fl, bar = cols[kind]
        m.r(ex, ey, dw - 0.06, du * hh - 0.03, fill=fl, r=0.04)
        m.r(ex, ey, 0.035, du * hh - 0.03, fill=bar, r=0.015)
        m.t(ex + 0.08, ey + 0.01, dw - 0.16, min(0.2, du * hh - 0.04), ttl, sz=7, color=WHITE, anchor="t")
    if new_event:
        d_, st, du, ttl = new_event
        ex, ey = gx + tw + d_ * dw + 0.03, g0 + (st - 9) * hh + 0.015
        m.r(ex, ey, dw - 0.06, du * hh - 0.03, fill="accent", r=0.04)
        m.t(ex + 0.08, ey + 0.01, dw - 0.16, min(0.34, du * hh - 0.04), ttl, sz=7, color=WHITE, font=FONT_SB, anchor="t")
        zone_new = m.zone(d_ * dw + gx + tw, (st - 9) * hh + g0 - 0.02, dw, du * hh + 0.04)
    z = {
        "new": m.zone(x_new, ry + 0.02, x_new2 - x_new, 0.76),
        "today": m.zone(x_today, ry + 0.02, 0.68, 0.76),
        "views": m.zone(x_view, ry + 0.02, x_view2 - x_view, 0.76),
        "share": m.zone(x_share, ry + 0.02, x_share2 - x_share, 0.76),
        "mini": m.zone(0.06, by + 0.04, fw - 0.08, 1.58),
        "cals": m.zone(0.06, cy - 0.04, fw - 0.08, 1.1),
        "nav": m.zone(0.06, ny + 0.04, fw - 0.08, 0.42),
        "grid": m.zone(gx + 0.05, by + 0.04, gw - 0.1, H - by - 0.1),
        "event": m.zone(gx + tw + 1 * dw, g0 + 2 * hh - 0.02, dw, hh + 0.04),
        "new_event": zone_new,
        "win": m.zone(0, 0, W, H),
    }
    s.end()
    return z


# ====================================================================== meeting form
MEET_W, MEET_H = 6.9, 4.72


def meeting_window(s, x, y, k=1.0, name="!!mock-meet", fill=6, tab=1):
    """New meeting request. fill: 1 title, 2 attendees, 3 time, 4 place, 5 agenda, 6 ready to send."""
    W, H = MEET_W, MEET_H
    m = M(s, x, y, k)
    s.begin(name)
    _frame(m, W, H, "%s — Собрание" % ("Итоги октября" if fill >= 1 else "Без имени"),
           ["Файл", "Собрание", "Помощник по планированию", "Вставка", "Формат текста"], active=tab)
    ry = 0.62
    m.box(0.012, ry, W - 0.024, 0.8, fill=BAR)
    m.ln(0.012, ry + 0.8, W - 0.012, ry + 0.8)
    cx = 0.14
    cx = _rbtn(m, cx, ry, "trash-2", "Удалить", w=0.64)
    _sep(m, cx + 0.07, ry); cx += 0.14
    cx = _rbtn(m, cx, ry, "calendar", "Встреча", w=0.66)
    x_as = cx
    cx = _rbtn(m, cx, ry, "calendar-clock", "Помощник по\nпланированию", w=0.98)
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_opt = cx
    cx = _rbtn(m, cx, ry, "circle-user", "Показать\nкак: Занят", w=0.8)
    cx = _rbtn(m, cx, ry, "bell", "Напомнить:\n15 минут", w=0.82)
    cx = _rbtn(m, cx, ry, "repeat", "Повторение", w=0.76)
    x_opt2 = cx
    _sep(m, cx + 0.07, ry); cx += 0.14
    x_priv = cx
    cx = _rbtn(m, cx, ry, "lock", "Частное", w=0.64)
    by = 1.5
    m.r(0.16, by, 0.8, 1.02, fill=(A("ACC"), 16) if fill < 6 else "accent", line=(A("ACC"), 55), r=0.08)
    m.i("send", 0.16 + 0.27, by + 0.2, 0.26, white=(fill >= 6))
    m.t(0.16, by + 0.56, 0.8, 0.3, "Отправить", sz=8, color=WHITE, font=FONT_SB, align="ctr")
    fx0 = 1.08
    rh = 0.29
    lw = 1.02
    fy = by
    rows = [("Название", "Итоги октября: обсуждение отчёта" if fill >= 1 else "", False),
            ("Обязательный", "Азиз Каримов;  Дилноза Рахимова" if fill >= 2 else "", True),
            ("Необязательный", "Тимур Юсупов" if fill >= 2 else "", True)]
    zr = {}
    for lab, val, btn in rows:
        if btn:
            m.r(fx0, fy + 0.025, lw, rh - 0.05, fill=(WHITE, 6), line=LN, r=0.05)
        m.t(fx0, fy + 0.025, lw, rh - 0.05, lab, sz=7.5, color=TXT, align="ctr")
        m.r(fx0 + lw + 0.08, fy + 0.025, W - fx0 - lw - 0.24, rh - 0.05, fill=FIELD, line=LN, r=0.05)
        if val:
            m.t(fx0 + lw + 0.18, fy + 0.025, W - fx0 - lw - 0.5, rh - 0.05, val, sz=8, color=WHITE)
        zr[lab] = m.zone(fx0 - 0.03, fy, W - fx0 - 0.1, rh)
        fy += rh
    # time rows
    ty0 = fy
    for lab, d1, t1 in (("Время начала", "Чт 12.11.2026", "11:00"), ("Время окончания", "Чт 12.11.2026", "11:30")):
        m.t(fx0, fy + 0.025, lw, rh - 0.05, lab, sz=7.5, color=TXT, align="ctr")
        m.r(fx0 + lw + 0.08, fy + 0.025, 1.3, rh - 0.05, fill=FIELD, line=LN, r=0.05)
        m.r(fx0 + lw + 1.46, fy + 0.025, 0.74, rh - 0.05, fill=FIELD, line=LN, r=0.05)
        if fill >= 3:
            m.t(fx0 + lw + 0.16, fy + 0.025, 1.2, rh - 0.05, d1, sz=8, color=WHITE)
            m.t(fx0 + lw + 1.54, fy + 0.025, 0.64, rh - 0.05, t1, sz=8, color=WHITE)
        if lab == "Время начала":
            m.r(fx0 + lw + 2.42, fy + 0.085, 0.13, 0.13, fill=None, line=LN, r=0.03)
            m.t(fx0 + lw + 2.62, fy + 0.025, 1.0, rh - 0.05, "Целый день", sz=7.5, color=TXT)
        fy += rh
    m.t(fx0, fy + 0.025, lw, rh - 0.05, "Место", sz=7.5, color=TXT, align="ctr")
    m.r(fx0 + lw + 0.08, fy + 0.025, W - fx0 - lw - 1.34, rh - 0.05, fill=FIELD, line=LN, r=0.05)
    m.r(W - 1.24, fy + 0.025, 1.08, rh - 0.05, fill=(WHITE, 6), line=LN, r=0.05)
    m.t(W - 1.24, fy + 0.025, 1.08, rh - 0.05, "Поиск помещений", sz=7, color=TXT, align="ctr")
    if fill >= 4:
        m.t(fx0 + lw + 0.18, fy + 0.025, 3.0, rh - 0.05, "Переговорная № 2, 3 этаж", sz=8, color=WHITE)
    zplace = m.zone(fx0 - 0.03, fy, W - fx0 - 0.1, rh)
    fy += rh
    ty = fy + 0.1
    m.r(0.16, ty, W - 0.32, H - ty - 0.16, fill=FIELD, line=LN, r=0.07)
    if fill >= 5:
        m.t(0.32, ty + 0.08, W - 0.64, H - ty - 0.32,
            [{"t": "Цель: согласовать отчёт за октябрь.", "spcAft": 2}, {"t": "1. Итоги месяца — Азиз, 10 минут"},
             {"t": "2. Замечания к отчёту — все, 15 минут"}, {"t": "3. Решения и сроки — 5 минут"}], sz=8, color=TXT, anchor="t")
    else:
        m.box(0.32, ty + 0.14, 0.012, 0.2, fill=A("ACC"))
    z = {
        "send": m.zone(0.13, by - 0.03, 0.86, 1.08),
        "title": zr["Название"],
        "people": m.zone(fx0 - 0.03, by + rh, W - fx0 - 0.1, rh * 2),
        "time": m.zone(fx0 - 0.03, ty0, W - fx0 - 0.1, rh * 2),
        "place": zplace,
        "body": m.zone(0.13, ty - 0.03, W - 0.26, H - ty - 0.1),
        "assistant": m.zone(x_as, ry + 0.02, 0.98, 0.76),
        "options": m.zone(x_opt, ry + 0.02, x_opt2 - x_opt, 0.76),
        "remind": m.zone(x_opt + 0.8, ry + 0.02, 0.82, 0.76),
        "repeat": m.zone(x_opt + 1.62, ry + 0.02, 0.76, 0.76),
        "private": m.zone(x_priv, ry + 0.02, 0.64, 0.76),
        "win": m.zone(0, 0, W, H),
    }
    s.end()
    return z


# ====================================================================== scheduling assistant
def assistant_grid(s, x, y, w, h, name="!!mock-assist", slot=4, show_slot=True):
    """Free/busy grid: attendees x half-hour slots 9:00-14:00. slot = index of the chosen half-hour."""
    people = [("Все участники", None), ("Нигора Алиева (вы)", [(1, 2), (8, 2)]), ("Азиз Каримов", [(0, 3), (6, 2)]),
              ("Дилноза Рахимова", [(1, 3), (7, 3)]), ("Тимур Юсупов", [(2, 2), (9, 1)]), ("Переговорная № 2", [(0, 2), (6, 4)])]
    n = 10
    s.begin(name)
    s.rrect(x, y, w, h, r=0.18, fill=WIN, line="glass", fx="shadow")
    lw = 2.25
    hh = 0.42
    rh = (h - hh - 0.5) / len(people)
    sw = (w - lw - 0.2) / n
    gx = x + lw
    for j in range(n + 1):
        hr = 9 + j // 2
        if j % 2 == 0 and j < n:
            s.text(gx + j * sw + 0.04, y + 0.06, sw * 2 - 0.08, hh - 0.1, "%d:00" % hr, sz=9, color=DIM, anchor="ctr", check=False)
        s.line(gx + j * sw, y + (0.08 if j % 2 == 0 else hh), gx + j * sw, y + hh + rh * len(people), color=(WHITE, 12 if j % 2 == 0 else 6))
    busy_all = set()
    for i, (nm, busy) in enumerate(people):
        ry = y + hh + i * rh
        s.line(x + 0.1, ry, x + w - 0.1, ry, color=(WHITE, 10))
        if i:
            s.pic(ic("door-open" if i == 5 else "circle-user", white=True), x + 0.2, ry + rh / 2 - 0.11, w=0.22, alpha=70)
        s.text(x + (0.52 if i else 0.2), ry, lw - 0.6, rh, nm, sz=10 if i else 9.5, color=WHITE if i else DIM, font=FONT if i else FONT_SB, anchor="ctr", check=False)
        if busy:
            for st, du in busy:
                s.rrect(gx + st * sw + 0.02, ry + 0.07, du * sw - 0.04, rh - 0.14, r=0.05, fill=(A("ACC2"), 62))
                for q in range(st, st + du):
                    busy_all.add(q)
    ry = y + hh
    for q in sorted(busy_all):
        s.rrect(gx + q * sw + 0.02, ry + 0.1, sw - 0.04, rh - 0.2, r=0.04, fill=(A("ACC2"), 30))
    s.line(x + 0.1, y + hh + rh * len(people), x + w - 0.1, y + hh + rh * len(people), color=(WHITE, 10))
    ly = y + h - 0.42
    s.rrect(x + 0.24, ly + 0.09, 0.3, 0.16, r=0.04, fill=(A("ACC2"), 62))
    s.text(x + 0.62, ly, 1.0, 0.34, "Занят", sz=10, color=TXT, anchor="ctr")
    s.rrect(x + 1.5, ly + 0.09, 0.3, 0.16, r=0.04, fill=None, line=(WHITE, 30))
    s.text(x + 1.88, ly, 1.2, 0.34, "Свободен", sz=10, color=TXT, anchor="ctr")
    s.rrect(x + 3.0, ly + 0.07, 0.3, 0.2, r=0.04, fill=(OK, 22), line=OK, lw=1.25)
    s.text(x + 3.38, ly, 2.6, 0.34, "Выбранное время собрания", sz=10, color=TXT, anchor="ctr")
    s.end()
    zone = (gx + slot * sw, y + hh - 0.02, sw, rh * len(people) + 0.04)
    if show_slot:
        s.rrect(zone[0], zone[1], zone[2], zone[3], r=0.06, fill=(OK, 16), line=OK, lw=1.5, name="!!assist-slot")
    return zone
