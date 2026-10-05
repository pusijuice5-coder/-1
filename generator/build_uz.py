import sys, os, shutil, subprocess, importlib, json, re
sys.path.insert(0, os.path.dirname(__file__))
import lib
from lxml import etree
W = "/tmp/claude-0/w"
MODS = ["m1", "m2", "m3", "m4", "m5", "m6"]
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
CYR = re.compile("[А-Яа-яЁё]")


def para_key(p):
    """Paragraph text with <a:br/> as \\n."""
    out = []
    for el in p:
        tag = etree.QName(el).localname
        if tag == "r" or tag == "fld":
            out.append("".join(t.text or "" for t in el.iter("{%s}t" % A)))
        elif tag == "br":
            out.append("\n")
    return "".join(out)


def user_parts(root):
    """Slides 1-11 and their notes: the user's own XML (slide 12 is regenerated)."""
    parts = ["ppt/slides/slide%d.xml" % i for i in range(1, 12)]
    for n in sorted(os.listdir(os.path.join(root, "ppt/notesSlides"))):
        if n.endswith(".xml"):
            parts.append("ppt/notesSlides/" + n)
    return parts


def collect_user(root):
    keys = []
    for part in user_parts(root):
        t = etree.parse(os.path.join(root, part))
        for p in t.iter("{%s}p" % A):
            k = para_key(p)
            if CYR.search(k) and k not in keys:
                keys.append(k)
    return keys


def translate_user(root, tr):
    missing = []
    for part in user_parts(root):
        path = os.path.join(root, part)
        t = etree.parse(path)
        changed = False
        for p in t.iter("{%s}p" % A):
            k = para_key(p)
            if not CYR.search(k):
                continue
            if k not in tr:
                missing.append(k)
                continue
            if tr[k] == k:          # kept as is (bilingual language picker)
                continue
            runs = [el for el in p if etree.QName(el).localname in ("r", "br", "fld")]
            first = next((el for el in runs if etree.QName(el).localname == "r"), None)
            rpr = first.find("{%s}rPr" % A) if first is not None else None
            idx = list(p).index(runs[0])
            for el in runs:
                p.remove(el)
            segs = tr[k].split("\n")
            new = []
            for i, seg in enumerate(segs):
                if i:
                    br = etree.Element("{%s}br" % A)
                    if rpr is not None:
                        br.append(etree.fromstring(etree.tostring(rpr)))
                    new.append(br)
                if seg:
                    r = etree.Element("{%s}r" % A)
                    if rpr is not None:
                        r.append(etree.fromstring(etree.tostring(rpr)))
                    tt = etree.SubElement(r, "{%s}t" % A)
                    tt.text = seg
                    new.append(r)
            for j, el in enumerate(new):
                p.insert(idx + j, el)
            changed = True
        if changed:
            for rp in t.iter("{%s}rPr" % A, "{%s}endParaRPr" % A, "{%s}defRPr" % A):
                if rp.get("lang") in ("ru-RU", "en-US", "en-ID"):
                    rp.set("lang", lib.LANG)
                if "err" in rp.attrib:
                    del rp.attrib["err"]
            t.write(path, xml_declaration=True, encoding="UTF-8", standalone=True)
    return missing


if __name__ == "__main__":
    mode = sys.argv[1]
    B = W + "/build_uz"
    if os.path.exists(B):
        shutil.rmtree(B)
    shutil.copytree(W + "/ku", B)
    if mode == "collect":
        user = collect_user(B)
        d = lib.Deck(B)
        for m in MODS:
            importlib.import_module(m).build(d)
        json.dump({"user": user, "gen": lib.SEEN}, open(W + "/uz/strings.json", "w"), ensure_ascii=False, indent=1)
        print("user", len(user), "gen", len(lib.SEEN))
    else:
        tr = {}
        for fn in sorted(os.listdir(W + "/uz")):
            if fn.startswith("tr_") and fn.endswith(".json"):
                tr.update(json.load(open(os.path.join(W + "/uz", fn))))
        lib.TR.update(tr)
        lib.LANG = "uz-Latn-UZ"
        miss_user = translate_user(B, tr)
        d = lib.Deck(B)
        for m in MODS:
            importlib.import_module(m).build(d)
        d.save()
        # spell-check language: everything except the bilingual language picker (slide 2)
        sd = os.path.join(B, "ppt/slides")
        for fn in os.listdir(sd):
            if fn.endswith(".xml") and fn != "slide2.xml":
                fp = os.path.join(sd, fn)
                x = open(fp, encoding="utf-8").read()
                open(fp, "w", encoding="utf-8").write(x.replace('lang="ru-RU"', 'lang="%s"' % lib.LANG))
        out = W + "/out_uz.pptx"
        if os.path.exists(out):
            os.remove(out)
        subprocess.run("cd %s && zip -qXr %s ." % (B, out), shell=True, check=True)
        miss_gen = [s for s in lib.SEEN if s not in tr]
        print("slides:", len(d.slides), "->", out)
        print("missing user:", len(miss_user), "missing gen:", len(miss_gen))
        for s in (miss_user + miss_gen)[:40]:
            print("  MISSING:", repr(s[:90]))
        for w in lib.SHRUNK: print("SHRINK", w)
        for w in lib.WARN: print("WARN", w)
