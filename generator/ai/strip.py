"""Remove every slide (and its notes) from an unpacked deck, keeping masters, layouts and media."""
import os, re, sys
root = sys.argv[1]
pres_p = os.path.join(root, "ppt/presentation.xml")
rels_p = os.path.join(root, "ppt/_rels/presentation.xml.rels")
ct_p = os.path.join(root, "[Content_Types].xml")
pres = open(pres_p, encoding="utf-8").read()
rels = open(rels_p, encoding="utf-8").read()
ct = open(ct_p, encoding="utf-8").read()
pres = re.sub(r"<p:sldIdLst>.*?</p:sldIdLst>", "<p:sldIdLst></p:sldIdLst>", pres, flags=re.S)
rels = re.sub(r'<Relationship [^>]*Type="[^"]*/slide"[^>]*/>', "", rels)
ct = re.sub(r'<Override PartName="/ppt/(slides|notesSlides)/[^"]+"[^>]*/>', "", ct)
for d in ("ppt/slides", "ppt/notesSlides"):
    for base, _, files in os.walk(os.path.join(root, d)):
        for f in files:
            os.remove(os.path.join(base, f))
open(pres_p, "w", encoding="utf-8").write(pres)
open(rels_p, "w", encoding="utf-8").write(rels)
open(ct_p, "w", encoding="utf-8").write(ct)
print("stripped")
