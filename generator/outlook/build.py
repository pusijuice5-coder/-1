# -*- coding: utf-8 -*-
"""Build the Outlook course.
usage: python3 build.py OUT.pptx [--theme magenta|green] [--only m0,m1]
"""
import sys, os, shutil, importlib, tempfile, zipfile, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lib, kit

ALL = ["m0", "m1", "m2", "m3", "m4", "m5", "m6"]


def build(out, theme="magenta", only=None, workdir=None):
    lib.set_theme(theme)
    mods = [importlib.import_module(m) for m in (only or ALL)]
    total = None
    for attempt in (1, 2):          # first pass only counts the slides (for "N / total" and the progress line)
        lib.WARN[:] = []
        root = tempfile.mkdtemp(prefix="olbuild_", dir=workdir)
        build_dir = os.path.join(root, "pkg")
        shutil.copytree(os.path.join(HERE, "base"), build_dir)
        d = lib.Deck(build_dir)
        k = kit.Kit(d, total=total)
        for m in mods:
            m.build(k)
        total = len(d.slides)
    d.save()
    if os.path.exists(out):
        os.remove(out)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(build_dir, "[Content_Types].xml"), "[Content_Types].xml")
        for base, _, files in os.walk(build_dir):
            for f in sorted(files):
                full = os.path.join(base, f)
                rel = os.path.relpath(full, build_dir)
                if rel != "[Content_Types].xml":
                    z.write(full, rel)
    print("slides:", total, "->", out, "(%.1f MB)" % (os.path.getsize(out) / 1e6))
    for i, s in enumerate(d.slides, 1):
        print("%3d %-18s %s" % (i, s.key, s.title_text[:60]))
    for w in lib.WARN:
        print("WARN", w)
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--theme", default="magenta")
    ap.add_argument("--only")
    ap.add_argument("--workdir")
    a = ap.parse_args()
    build(a.out, a.theme, a.only.split(",") if a.only else None, a.workdir)
