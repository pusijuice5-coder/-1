# -*- coding: utf-8 -*-
"""Recurring slide types of the course, in the style of Agile_kurs_1."""
from lib import *

LETTERS = ["А", "Б", "В", "Г"]


def module_cover(d, n, title, items, notes, pose="present"):
    """Dark module cover - same composition as the user's slide 9."""
    s = d.new(bg="dark", notes=notes)
    s.ezoza(pose, x=7.35, h=7.25)
    s.logo(dark_bg=True, w=2.05)
    s.text(0.46, 1.75, 6.6, 0.46, "%d Модуль" % n, sz=24, bold=True, color=WHITE, anim=0)
    th = text_height([{"runs": parse_runs(title)}], 6.6, 36, True, 0.95)
    s.text(0.46, 2.3, 6.6, th + 0.05, title, sz=36, bold=True, color=WHITE, lnsp=0.95, anim=150)
    y = 2.3 + th + 0.35
    s.text(0.46, y, 6.6, 0.37, "В ЭТОМ МОДУЛЕ", sz=14, bold=True, color=G2, anim=300)
    s.text(0.46, y + 0.5, 6.6, 0.42 * len(items), ["%d. %s" % (i + 1, t) for i, t in enumerate(items)],
           sz=15, bold=True, color=WHITE, lnsp=1.0, spc_after=9, anim=450)
    return s


def talk(d, text, notes=None, pose="present", bg="glass", bw=5.7, bx=0.7, by=0.9, sz=None, tail=(-62000, 30000), extra=None):
    """Ezoza speaks: glass office background + speech bubble (slides 3 and 8)."""
    s = d.new(bg=bg, notes=notes or text.replace("\n", " ").replace("**", ""))
    if sz is None:
        ln = len("\n".join(T(t) for t in text.split("\n")))
        sz = 20 if ln < 110 else 18 if ln < 200 else 16
    s.ezoza(pose, right=12.9, h=7.15)
    paras = [{"runs": parse_runs(t), "spcAft": 6} for t in text.split("\n")]
    bh = text_height(paras, bw - 0.7, sz, False, 1.05, 6) + 0.75
    s.bubble(bx, by, bw, bh, text, sz=sz, tail=tail, anim=0)
    if extra:
        extra(s, by + bh)
    return s


def quiz(d, module, situation, question, options, correct, notes_extra=""):
    s = d.new(bg="video", notes="Проверьте себя. %s %s Правильный ответ: %s. %s" % (situation, question, LETTERS[correct], notes_extra))
    s.title("Проверьте себя", anim=0)
    s.ezoza("chest", right=13.25, h=6.55)
    # situation card
    s.begin("Ситуация")
    paras = [{"runs": parse_runs(situation)}, {"runs": parse_runs("**" + question + "**"), "spcBef": 6}]
    th = text_height(paras, 7.9 - 1.5, 15, False, 1.05, 4)
    ch = max(1.5, th + 0.75)
    s.rrect(0.55, 1.35, 7.9, ch, r=0.22, fill=DARK, shadow="green")
    s.shape(0.8, 1.6, 0.62, 0.62, geom="ellipse", fill=LIME, text="?", sz=22, bold=True, color=DARK, align="ctr", anchor="ctr", inset=(0, 0, 0, 0))
    s.text(1.65, 1.55, 6.5, 0.3, "СИТУАЦИЯ", sz=11, bold=True, color=LIME)
    s.text(1.65, 1.9, 6.55, ch - 0.7, [{"t": situation, "spcAft": 4}, {"t": question, "b": True, "color": LIME, "spcBef": 4}],
           sz=15, color=WHITE, lnsp=1.05)
    s.end(anim=100)
    y0 = 1.35 + ch + 0.3
    oh = (6.45 - y0 - 0.2) / 2
    for i, opt in enumerate(options):
        x = 0.55 + (i % 2) * 4.05
        y = y0 + (i // 2) * (oh + 0.2)
        s.begin("Вариант " + LETTERS[i])
        s.rrect(x, y, 3.85, oh, r=0.3, grad="button", shadow="pill")
        s.circle_num(x + 0.18, y + oh / 2 - 0.26, 0.52, LETTERS[i], fill=DARK, sz=15)
        s.text(x + 0.85, y + 0.08, 2.85, oh - 0.16, opt, sz=13, color="1B2A22", anchor="ctr", lnsp=1.0)
        s.end(anim=250 + i * 120)
    s.text(0.55, 6.62, 7.9, 0.35, "Выберите один вариант. Разбор — на следующем слайде.", sz=12, color=MUTED,
           anim=800)
    return s


def review(d, module, options, explanations, correct, notes):
    s = d.new(bg="video", notes=notes)
    s.title("Разбор", anim=0)
    s.ezoza("present", right=13.3, h=6.4)
    cw = 3.95
    tw = cw - 0.5
    need = []
    for opt, ex in zip(options, explanations):
        oh = text_height([{"runs": parse_runs(opt)}], tw, 13, True, 1.0)
        eh = text_height([{"runs": parse_runs(ex)}], tw, 12, False, 1.0)
        need.append((oh, eh))
    chh = min(2.62, max(0.85 + o + 0.12 + x + 0.2 for o, x in need))
    for i, (opt, ex) in enumerate(zip(options, explanations)):
        x = 0.55 + (i % 2) * (cw + 0.2)
        y = 1.35 + (i // 2) * (chh + 0.22)
        ok = i == correct
        oh, eh = need[i]
        s.begin("Разбор " + LETTERS[i])
        if ok:
            s.rrect(x, y, cw, chh, r=0.22, fill=DARK, shadow="green")
        else:
            s.rrect(x, y, cw, chh, r=0.22, fill=WHITE, shadow="soft")
        s.circle_num(x + 0.22, y + 0.22, 0.48, LETTERS[i], fill=LIME if ok else GREY, color=DARK, sz=14)
        s.chip(x + cw - 1.42, y + 0.29, 1.2, 0.34, "ВЕРНО" if ok else "НЕВЕРНО", fill=LIME if ok else GREY, color=DARK, sz=10)
        s.text(x + 0.25, y + 0.85, tw, oh + 0.05, opt, sz=13, bold=True, color=WHITE if ok else TITLE, lnsp=1.0)
        s.text(x + 0.25, y + 0.85 + oh + 0.12, tw, eh + 0.05, ex, sz=12, color="D8E8DC" if ok else BODY, lnsp=1.0)
        s.end(anim=150 + i * 120)
    return s


def summary(d, n, points, nxt, notes):
    """Dark summary slide with white pills and hexagon numbers (style of the user's slide 6)."""
    s = d.new(bg="dark", notes=notes)
    s.ezoza("wave", right=13.25, h=7.0)
    s.text(0.55, 0.55, 7.5, 0.7, "Главное из модуля %d" % n, sz=34, bold=True, color=WHITE, anim=0)
    y = 1.65
    for i, p in enumerate(points):
        s.begin("Пункт %d" % (i + 1))
        s.rrect(0.95, y, 6.45, 1.2, r=0.3, fill=WHITE, shadow="pill")
        s.text(2.2, y + 0.1, 5.0, 1.0, p, sz=14, color="2B3A33", anchor="ctr", lnsp=1.05)
        s.hexnum(0.45, y + 0.14, 1.36, "%02d" % (i + 1), fill=G2, sz=24)
        s.end(anim=150 + i * 150)
        y += 1.45
    s.begin("Далее")
    s.rrect(0.95, y + 0.15, 6.45, 0.7, r=0.35, grad="button")
    s.text(1.2, y + 0.15, 6.0, 0.7, nxt, sz=15, bold=True, color=DARK, anchor="ctr")
    s.end(anim=700)
    return s


def section_title_light(s, title, sub=None):
    s.title(title, anim=0)
    if sub:
        s.subtitle(sub, anim=100)


def photo(s, key, x, y, w, h, r=0.2, focus=0.45, name=None, anim=None):
    """Picture cropped to the box aspect (2048x1152 sources)."""
    pw, ph = 2048, 1152
    asp = w / h
    if asp >= pw / ph:
        keep = (pw / asp) / ph
        t = (1 - keep) * focus
        crop = (0, t, 0, 1 - keep - t)
    else:
        keep = (ph * asp) / pw
        l = (1 - keep) / 2
        crop = (l, 0, 1 - keep - l, 0)
    return s.pic(key, x, y, w, h, crop=crop, geom="roundRect" if r else "rect", radius=r, name=name, anim=anim)


def card(s, x, y, w, h, dark=False, r=0.22):
    return s.rrect(x, y, w, h, r=r, fill=DARK if dark else WHITE, shadow="green" if dark else "soft")


def bullets(s, x, y, w, h, items, sz=13, color=BODY, bcolor=G2, spc=5, lnsp=1.0, bold=False):
    return s.text(x, y, w, h, [{"t": t, "bullet": bcolor, "spcAft": spc} for t in items], sz=sz, color=color, lnsp=lnsp, bold=bold)


def check_icon(s, x, y, d, fill=G2, color=WHITE):
    s.shape(x, y, d, d, geom="ellipse", fill=fill)
    s.freeform([(0.0, 0.52), (0.38, 0.9), (1.0, 0.0)], x + d * 0.27, y + d * 0.31, d * 0.46, d * 0.38, color=color, lw=max(1.5, d * 5))


def cross_icon(s, x, y, d, fill=GREY, color=DARK):
    s.shape(x, y, d, d, geom="ellipse", fill=fill)
    s.line(x + d * 0.33, y + d * 0.33, x + d * 0.67, y + d * 0.67, color=color, lw=max(1.25, d * 4))
    s.line(x + d * 0.67, y + d * 0.33, x + d * 0.33, y + d * 0.67, color=color, lw=max(1.25, d * 4))
