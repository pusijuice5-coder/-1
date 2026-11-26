# -*- coding: utf-8 -*-
"""Builds the course «Защита от мошенничества» (Ipak Yuli Bank) on the template's master and theme.

    python3 generator/fraud/build.py [out.pptx]

Text comes from the course document (RU) verbatim; slide titles are Minto conclusions; no voice-over,
no video — entrance animations, fade transitions and click triggers (module 7, confirmation in module 6).
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib
from content_a import cover, why, goals, route, module1, module2
from content_b import module3
from content_c import module4, module5, module6
from content_d import module7, module8

THEME = {"dk1": "0F2418", "dk2": "0F2418", "lt2": "EEF3EF", "accent1": lib.GREEN, "accent2": lib.LIME, "hlink": lib.GREEN}
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "Zashchita_ot_moshennichestva_kurs.pptx")
WORK = "/tmp/fraud_build"

lib.make_base(os.path.join(HERE, "base"), WORK, THEME, "Защита от мошенничества — онлайн-курс")
d = lib.Deck(WORK)
for part in (cover, why, goals, route, module1, module2, module3, module4, module5, module6, module7, module8):
    part(d)
d.save(os.path.abspath(OUT))
print("slides:", len(d.slides), "->", os.path.abspath(OUT), "%.1f MB" % (os.path.getsize(OUT) / 1e6))
for w in lib.SHRUNK:
    print("SHRINK", w)
for w in lib.WARN:
    print("WARN", w)
