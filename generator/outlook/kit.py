# -*- coding: utf-8 -*-
"""Reusable slide parts of the Outlook course: page chrome, glass cards, lists, buttons, quiz."""
import lib
from lib import *

MX = 0.75                 # side margin
CW = SW - 2 * MX          # content width
TOP = 2.05                # content top (below title)
BOT = 6.55                # content bottom (above footer)

COURSE = "Outlook: почта и календарь"
MODULES = [
    ("01", "Знакомство с Outlook", "Окно программы, папки и значки"),
    ("02", "Письма", "Написать, ответить, переслать"),
    ("03", "Порядок в почте", "Поиск, папки, правила, автоответ"),
    ("04", "Календарь", "Встречи, собрания, приглашения"),
    ("05", "Безопасность и этикет", "Фишинг и правила переписки"),
]

GLOWS = {   # name -> (file, x, y, w, h, rot, alpha)
    "hero": ("glow1.jpg", 0, 0, SW, SH, 0, 46),
    "hero2": ("glow1.jpg", -1.2, -0.8, SW + 2.4, SH + 1.6, 180, 40),
    "a": ("glow2.jpg", 0, 0, SW, SH, 180, 20),
    "b": ("glow2.jpg", -2.2, -1.4, SW + 3.2, SH + 2.4, 180, 20),
    "c": ("glow2.jpg", -1.0, -0.4, SW + 3.4, SH + 2.0, 172, 20),
    "d": ("glow2.jpg", -2.6, -2.0, SW + 4.0, SH + 2.6, 188, 20),
}


def ic(name, white=False):
    return "ic_%s%s.png" % (name, "_w" if white else A("suffix"))


def obj(name):
    """3D object picture for the current theme."""
    return "%s%s.png" % (name, A("suffix"))


class Kit:
    """Keeps slide numbering and builds the common page frame."""

    def __init__(self, deck, total=None):
        self.d = deck
        self.total = total
        self.mod = None       # current module index (0-based) or None
        self._g = 0

    # ---------------------------------------------------------------- frame
    def slide(self, key, title="", sub=None, notes="", glow=None, nav=True, crumb=True, logo=True, trans="morph",
              dur=1000, adv_click=True, title_w=None, title_sz=30, title_y=0.95, center=False, show_title=True):
        d = self.d
        s = d.new(key, title=title, notes=notes, trans=trans, dur=dur, adv_click=adv_click)
        no = len(d.slides)
        s.no = no
        if glow is None:
            glow = "abcd"[self._g % 4]
            self._g += 1
        fn, gx, gy, gw, gh, rot, al = GLOWS[glow]
        s.pic(fn, gx, gy, gw, gh, name="!!glow", alpha=al, rot=rot)
        if logo:
            lw = 1.25
            s.pic(A("logo") + ".png", SW - MX - lw, 0.4, w=lw, name="!!logo")
        if crumb and self.mod is not None:
            num, name, _ = MODULES[self.mod]
            s.oval(MX, 0.535, 0.1, 0.1, fill=A("ACC"), name="!!crumb-dot")
            s.text(MX + 0.22, 0.42, 6.0, 0.34, "Модуль %s · %s" % (num, name), sz=12, color=TEXT, font=FONT, anchor="ctr", name="!!crumb")
        elif crumb:
            s.oval(MX, 0.535, 0.1, 0.1, fill=A("ACC"), name="!!crumb-dot")
            s.text(MX + 0.22, 0.42, 6.0, 0.34, COURSE, sz=12, color=TEXT, anchor="ctr", name="!!crumb")
        if title and show_title:
            tw = title_w or (CW - 1.6)
            if center:
                s.shape((SW - tw) / 2, title_y, tw, 0.66, text=title, sz=title_sz, color=WHITE, font=FONT, align="ctr", anchor="t",
                        inset=(0, 0, 0, 0), ph="title", name="!!title", lnsp=0.95)
            else:
                s.shape(MX, title_y, tw, 0.66, text=title, sz=title_sz, color=WHITE, font=FONT, anchor="t", inset=(0, 0, 0, 0),
                        ph="title", name="!!title", lnsp=0.95)
        elif title:
            # keep a real (off-slide) title so the slide has a name in outlines and players
            s.shape(MX, -1.2, 8, 0.6, text=title, sz=20, color=WHITE, inset=(0, 0, 0, 0), ph="title", name="!!title", check=False)
        if sub:
            if center:
                s.text((SW - 8.6) / 2, title_y + 0.72, 8.6, 0.62, sub, sz=15, color=TEXT, font=FONT_L, align="ctr", name="!!sub", lnsp=1.0)
            else:
                s.text(MX, title_y + 0.68, title_w or 8.6, 0.36, sub, sz=15, color=TEXT, font=FONT_L, name="!!sub")
        if nav:
            self.footer(s, no)
        return s

    def footer(self, s, no):
        total = self.total or 99
        y = 6.93
        # progress line
        s.rrect(MX, y + 0.19, 3.0, 0.04, r=0.02, fill=(WHITE, 14), name="!!prog-track")
        s.rrect(MX, y + 0.19, max(0.06, 3.0 * no / total), 0.04, r=0.02, fill=A("ACC"), name="!!prog-fill")
        s.text(MX + 3.2, y + 0.04, 1.6, 0.34, "%d / %d" % (no, total), sz=11, color=MUTED, anchor="ctr", name="!!prog-num")
        bx = SW - MX - 0.42
        nav_btn(s, bx - 0.54, y, "prev")
        nav_btn(s, bx, y, "next")


def nav_btn(s, x, y, kind, d=0.42):
    """Round glass button with an arrow (like the arrow buttons of the reference cards)."""
    s.oval(x, y, d, d, fill=(WHITE, 7), line="glass2", name="!!nav-%s" % kind, link=kind,
           tip="Назад" if kind == "prev" else "Далее")
    icon = "chevron-left" if kind == "prev" else "chevron-right"
    s.pic(ic(icon, white=True), x + d * 0.22, y + d * 0.22, w=d * 0.56, name="!!nav-%s-i" % kind, link=kind)


# ---------------------------------------------------------------- basic parts
def pill(s, x, y, text, sz=12, h=0.4, name=None, fill=None, line="glass", color=TEXT, anim=None, pad=0.22, w=None, font=FONT, dot=False):
    w = w or (text_width(text, sz, font) + 2 * pad + (0.2 if dot else 0))
    if dot:
        s.begin(name or "pill")
        s.rrect(x, y, w, h, r=h / 2, fill=fill, line=line)
        s.oval(x + pad - 0.02, y + h / 2 - 0.045, 0.09, 0.09, fill=A("ACC"))
        s.text(x + pad + 0.16, y, w - pad - 0.16, h, text, sz=sz, color=color, anchor="ctr", font=font)
        s.end(anim=anim)
    else:
        s.rrect(x, y, w, h, r=h / 2, fill=fill, line=line, text=text, sz=sz, color=color, align="ctr", anchor="ctr",
                inset=(0.05, 0, 0.05, 0), name=name, anim=anim, font=font)
    return w


def button(s, x, y, w, h, text, link="next", name=None, sz=15, anim=None, primary=True):
    """Accent pill button with a hyperlink."""
    s.rrect(x, y, w, h, r=h / 2, fill="accent" if primary else (WHITE, 8), line=None if primary else "glass",
            text=text, sz=sz, color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.1, 0, 0.1, 0.02),
            link=link, name=name, anim=anim, fx="glow_s" if primary else None)


def card(s, x, y, w, h, title=None, body=None, icon=None, num=None, tag=None, name=None, anim=None, style="glass",
         tsz=17, bsz=14, pad=0.3, img=None, img_h=0.62, divider=True, r=0.24, bullet=False, center=False, body_color=TEXT, link=None):
    """Glass card: [icon | number] + title + thin divider + body text."""
    s.begin(name or "card")
    line = "glass" if style in ("glass", "glass2") else None
    s.rrect(x, y, w, h, r=r, fill=style, line=line, link=link)
    cy = y + pad
    al = "ctr" if center else "l"
    if img:
        iw = img_h * img_size(img)[0] / img_size(img)[1]
        s.pic(img, x + (w - iw) / 2 if center else x + pad - 0.04, cy - 0.04, h=img_h)
        cy += img_h + 0.1
    elif icon:
        isz = 0.46
        s.pic(ic(icon, white=(style == "accent")), x + (w - isz) / 2 if center else x + pad - 0.03, cy, w=isz)
        cy += isz + 0.16
    elif num is not None:
        s.text(x + pad, cy - 0.08, w - 2 * pad, 0.5, str(num), sz=26, color=A("ACC") if style != "accent" else WHITE, font=FONT_L, align=al)
        cy += 0.5
    if tag:
        s.text(x + pad, cy, w - 2 * pad, 0.26, tag, sz=11, color=A("ACC_SOFT") if style != "accent" else WHITE, font=FONT_SB, align=al)
        cy += 0.3
    tw = w - 2 * pad
    if title:
        th = text_height(title, tw, tsz, FONT_SB, lnsp=0.98)
        s.text(x + pad, cy, tw, th + 0.04, title, sz=tsz, color=WHITE, font=FONT_SB, lnsp=0.98, align=al)
        cy += th + 0.14
    if body:
        if divider and title:
            s.line(x + pad, cy, x + w - pad, cy, color=(WHITE, 20))
            cy += 0.16
        s.text(x + pad, cy, tw, max(0.3, y + h - cy - pad * 0.7), body, sz=bsz, color=body_color if style != "accent" else WHITE,
               font=FONT, lnsp=1.0, spc_after=5, bullet=bullet, align=al)
    return s.end(anim=anim)


def card_h(title, body, w, tsz=17, bsz=14, pad=0.3, icon=False, num=False, tag=False, bullet=False, divider=True):
    """Height a card needs for its content."""
    tw = w - 2 * pad
    h = pad
    if icon:
        h += 0.62
    if num:
        h += 0.5
    if tag:
        h += 0.3
    if title:
        h += text_height(title, tw, tsz, FONT_SB, lnsp=0.98) + 0.14
    if body:
        if divider and title:
            h += 0.16
        h += text_height(body, tw, bsz, FONT, lnsp=1.0, spc_after=5, bullet=bullet)
    return h + pad * 0.85


def grid(s, items, x=MX, y=TOP, w=CW, cols=3, gap=0.28, h=None, anim0=150, step=110, name="c", **kw):
    """Lay cards on a grid. items: dicts passed to card()."""
    cw = (w - gap * (cols - 1)) / cols
    rows = (len(items) + cols - 1) // cols
    if h is None:
        hs = []
        for it in items:
            hs.append(card_h(it.get("title"), it.get("body"), cw, tsz=kw.get("tsz", 17), bsz=kw.get("bsz", 14), pad=kw.get("pad", 0.3),
                             icon=bool(it.get("icon")), num=it.get("num") is not None, tag=bool(it.get("tag")), bullet=kw.get("bullet", False)))
        h = max(hs)
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        opts = dict(kw)
        opts.update(it)
        opts.setdefault("name", "%s%d" % (name, i))
        card(s, x + c * (cw + gap), y + r * (h + gap), cw, h, anim=(anim0 + i * step) if anim0 is not None else None, **opts)
    return h, rows * h + (rows - 1) * gap


def bullets(s, x, y, w, items, sz=15, gap=9, name=None, anim=None, color=TEXT, h=None):
    """Simple list with accent dots."""
    paras = [{"t": t, "spcAft": gap} for t in items]
    hh = h or text_height(paras, w, sz, FONT, lnsp=1.0, spc_after=gap, bullet=True) + 0.1
    s.text(x, y, w, hh, paras, sz=sz, color=color, bullet=True, lnsp=1.0, name=name, anim=anim)
    return hh


def note(s, x, y, w, text, icon="lightbulb", name=None, anim=None, sz=14, h=None, style="soft", color=TEXT):
    """Small hint strip with an icon."""
    tw = w - 1.05
    h = h or max(0.62, text_height(text, tw, sz, FONT, lnsp=1.0) + 0.3)
    s.begin(name or "note")
    s.rrect(x, y, w, h, r=min(0.2, h / 2), fill=style if style != "soft" else (WHITE, 6), line="glass2")
    s.pic(ic(icon), x + 0.24, y + h / 2 - 0.19, w=0.38)
    s.text(x + 0.8, y, tw, h, text, sz=sz, color=color, anchor="ctr", lnsp=1.0)
    s.end(anim=anim)
    return h


def tile3d(s, x, y, w, h, tile, name=None, anim=None, r=0.22):
    """Opaque 3D picture from the reference deck on its dark panel (as on the reference 'Quick Start' cards)."""
    s.begin(name or "tile")
    s.rrect(x, y, w, h, r=r, fill=PANEL)
    pw, ph = img_size(tile)
    ih = h * 0.96
    iw = ih * pw / ph
    if iw > w * 0.98:
        iw = w * 0.98
        ih = iw * ph / pw
    s.pic(tile, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih, geom="roundRect", radius=r * 0.8)
    return s.end(anim=anim)


def keycap(s, x, y, text, sz=13, h=0.44, name=None, w=None):
    w = w or max(0.56, text_width(text, sz, FONT_SB) + 0.34)
    s.rrect(x, y, w, h, r=0.09, fill=("grad", [(0, "2A2A33", None), (100, "17171C", None)], 90), line="glass",
            text=text, sz=sz, color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.03, 0, 0.03, 0.02), name=name)
    return w


def keys(s, x, y, combo, sz=13, h=0.44):
    """'Ctrl+Shift+M' -> row of key caps with '+' between; returns total width."""
    cx = x
    parts = combo.split("+")
    for i, p in enumerate(parts):
        cx += keycap(s, cx, y, p, sz=sz, h=h)
        if i < len(parts) - 1:
            s.text(cx, y, 0.22, h, "+", sz=sz, color=MUTED, align="ctr", anchor="ctr")
            cx += 0.22
    return cx - x


def path_steps(s, x, y, steps, sz=13, h=0.46, gap=0.12, name="path", anim=None):
    """Menu path: [Файл] > [Параметры] > [Почта] - pills with chevrons."""
    s.begin(name)
    cx = x
    for i, t in enumerate(steps):
        w = text_width(t, sz, FONT_SB) + 0.44
        last = i == len(steps) - 1
        s.rrect(cx, y, w, h, r=h / 2, fill="accent" if last else (WHITE, 7), line=None if last else "glass2", text=t, sz=sz,
                color=WHITE, font=FONT_SB, align="ctr", anchor="ctr", inset=(0.04, 0, 0.04, 0.02))
        cx += w
        if not last:
            s.pic(ic("chevron-right", white=True), cx + gap - 0.04, y + h / 2 - 0.13, w=0.26, alpha=60)
            cx += gap * 2 + 0.18
    s.end(anim=anim)
    return cx - x


# ---------------------------------------------------------------- quiz
LETTERS = "ABCD"


def quiz(k, key, question, options, correct, explain, tag="Проверьте себя", situation=None, wrong=None, notes=""):
    """Question slide. Click an option -> its mark and a feedback panel appear (triggers); other feedback hides.
    options: list of str; correct: index; explain: text shown for the right answer; wrong: text for wrong ones."""
    wrong = wrong or "Не совсем. Подумайте ещё и выберите другой вариант."
    n = "Вопрос. %s%s Варианты: %s. Правильный ответ: %s. %s %s" % (
        (situation + " ") if situation else "", question, "; ".join("%s) %s" % (LETTERS[i], o) for i, o in enumerate(options)),
        LETTERS[correct], explain, notes)
    s = k.slide(key, title=tag, notes=n, adv_click=False, show_title=False)
    pill(s, MX, 0.98, tag, sz=12, name="!!qtag", dot=True)
    y = 1.56
    qw = CW
    if situation:
        sh = text_height(situation, qw, 15, FONT_L, lnsp=1.0) + 0.06
        s.text(MX, y, qw, sh, situation, sz=15, color=TEXT, font=FONT_L, lnsp=1.0, name="q-sit", anim=0)
        y += sh + 0.1
    qh = text_height(question, qw, 24, FONT, lnsp=0.98) + 0.06
    s.text(MX, y, qw, qh, question, sz=24, color=WHITE, lnsp=0.98, name="q-text", anim=0 if not situation else 80)
    y += qh + 0.3
    # options (left) + feedback panel (right)
    ow = 7.35
    fx, fw = MX + ow + 0.35, CW - ow - 0.35
    tw = ow - 1.5
    hs = [max(0.74, text_height(o, tw, 15, FONT, lnsp=1.0) + 0.34) for o in options]
    gap = 0.16
    avail = BOT - y
    tot = sum(hs) + gap * (len(hs) - 1)
    if tot > avail:
        lib.WARN.append("%s: quiz options do not fit (%.2f > %.2f)" % (key, tot, avail))
    oy = y
    rects = []
    for i, (o, oh) in enumerate(zip(options, hs)):
        s.begin("opt%d" % i)
        s.rrect(MX, oy, ow, oh, r=min(0.22, oh / 2), fill="glass", line="glass")
        s.oval(MX + 0.2, oy + oh / 2 - 0.2, 0.4, 0.4, fill=(WHITE, 8), line="glass2", text=LETTERS[i], sz=13, color=WHITE, font=FONT_SB,
               align="ctr", anchor="ctr", inset=(0, 0, 0, 0.01))
        s.text(MX + 0.82, oy, tw, oh, o, sz=15, color=WHITE, anchor="ctr", lnsp=1.0)
        s.end(anim=200 + i * 90)
        rects.append((oy, oh))
        oy += oh + gap
    # idle hint in the feedback area
    ph = oy - gap - y
    s.begin("q-hint")
    s.rrect(fx, y, fw, ph, r=0.24, fill=(WHITE, 4), line="glass2", dash="dash")
    s.pic(ic("mouse-pointer-click"), fx + fw / 2 - 0.28, y + ph / 2 - 0.62, w=0.56)
    s.text(fx + 0.3, y + ph / 2 + 0.06, fw - 0.6, 0.7, "Нажмите на вариант ответа", sz=14, color=MUTED, align="ctr", lnsp=1.0)
    hint = s.end(anim=560)
    # feedback groups
    fbs = []
    for i, (ry, rh) in enumerate(rects):
        good = i == correct
        col = OK if good else BAD
        s.begin("fb%d" % i)
        s.rrect(MX, ry, ow, rh, r=min(0.22, rh / 2), fill=(col, 10), line=col, lw=1.5)
        s.pic("ic_circle-check_ok.png" if good else "ic_circle-x_bad.png", MX + ow - 0.62, ry + rh / 2 - 0.19, w=0.38)
        s.rrect(fx, y, fw, ph, r=0.24, fill="glass", line=col, lw=1.25)
        s.pic("ic_circle-check_ok.png" if good else "ic_circle-x_bad.png", fx + 0.3, y + 0.3, w=0.5)
        s.text(fx + 0.95, y + 0.3, fw - 1.2, 0.5, "Верно!" if good else "Не совсем", sz=20, color=col, font=FONT_SB, anchor="ctr")
        body = explain if good else wrong
        s.text(fx + 0.3, y + 1.02, fw - 0.6, ph - 1.2, body, sz=14, color=TEXT, lnsp=1.02, spc_after=6)
        fbs.append(s.end())
    # transparent click areas on top
    for i, (ry, rh) in enumerate(rects):
        hit = s.rrect(MX, ry, ow, rh, r=min(0.22, rh / 2), fill="hit", name="hit%d" % i, tip="Вариант %s" % LETTERS[i])
        s.trigger(hit, show=[fbs[i]], hide=[hint] + [f for j, f in enumerate(fbs) if j != i])
    return s
